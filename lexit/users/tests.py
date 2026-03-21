from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.test import SimpleTestCase, override_settings

from . import activecampaign
from .forms import SimpleUserCreationForm
from .models import Referrer
from .views import _find_referrer_profile


class ActiveCampaignReferralCodeTagTests(SimpleTestCase):
	@override_settings(ACTIVECAMPAIGN_REFERRAL_CODE_TAG_PREFIX='ref=')
	def test_build_referral_code_tag_name_normalizes_code(self):
		tag_name = activecampaign.build_referral_code_tag_name(' my-code_123 ')
		self.assertEqual(tag_name, 'ref=MYCODE123')

	@override_settings(ACTIVECAMPAIGN_REFERRAL_CODE_TAG_PREFIX='campaign-ref:')
	def test_build_referral_code_tag_name_uses_custom_prefix(self):
		tag_name = activecampaign.build_referral_code_tag_name('abc-42')
		self.assertEqual(tag_name, 'campaign-ref:ABC42')

	@override_settings(
		ACTIVECAMPAIGN_API_URL='https://example.api-us1.com',
		ACTIVECAMPAIGN_API_KEY='test-key',
		ACTIVECAMPAIGN_REFERRAL_CODE_TAG_PREFIX='ref=',
	)
	def test_creates_and_applies_referral_code_tag_when_missing(self):
		user = SimpleNamespace(
			email='newuser@example.com',
			first_name='New',
			last_name='User',
		)

		post_calls = []

		def fake_post(url, payload, api_key):
			post_calls.append((url, payload, api_key))

			if url.endswith('/contact/sync'):
				return {'contact': {'id': '123'}}
			if url.endswith('/tags'):
				return {'tag': {'id': '777'}}
			return {}

		with patch.object(activecampaign, '_post_json', side_effect=fake_post), patch.object(
			activecampaign,
			'_get_json',
			return_value={'tags': []},
		):
			result = activecampaign.sync_contact(user, referral_code='code-123')

		self.assertTrue(result['success'])
		self.assertIn('777', result.get('applied_tags', []))

		tag_create_calls = [call for call in post_calls if call[0].endswith('/tags')]
		self.assertEqual(len(tag_create_calls), 1)
		self.assertEqual(tag_create_calls[0][1]['tag']['tag'], 'ref=CODE123')

		contact_tag_calls = [
			call
			for call in post_calls
			if call[0].endswith('/contactTags') and call[1].get('contactTag', {}).get('tag') == '777'
		]
		self.assertEqual(len(contact_tag_calls), 1)

	@override_settings(
		ACTIVECAMPAIGN_API_URL='https://example.api-us1.com',
		ACTIVECAMPAIGN_API_KEY='test-key',
		ACTIVECAMPAIGN_REFERRAL_CODE_TAG_PREFIX='ref=',
	)
	def test_reuses_existing_referral_code_tag(self):
		user = SimpleNamespace(
			email='another@example.com',
			first_name='Another',
			last_name='User',
		)

		post_calls = []

		def fake_post(url, payload, api_key):
			post_calls.append((url, payload, api_key))
			if url.endswith('/contact/sync'):
				return {'contact': {'id': '123'}}
			return {}

		existing_tags_response = {
			'tags': [
				{'id': '555', 'tag': 'ref=CODE123'},
			]
		}

		with patch.object(activecampaign, '_post_json', side_effect=fake_post), patch.object(
			activecampaign,
			'_get_json',
			return_value=existing_tags_response,
		):
			result = activecampaign.sync_contact(user, referral_code='CODE123')

		self.assertTrue(result['success'])
		self.assertIn('555', result.get('applied_tags', []))

		tag_create_calls = [call for call in post_calls if call[0].endswith('/tags')]
		self.assertEqual(len(tag_create_calls), 0)

		contact_tag_calls = [
			call
			for call in post_calls
			if call[0].endswith('/contactTags') and call[1].get('contactTag', {}).get('tag') == '555'
		]
		self.assertEqual(len(contact_tag_calls), 1)


class ActiveCampaignReferrerNotificationTests(SimpleTestCase):
	@override_settings(
		ACTIVECAMPAIGN_API_URL='https://example.api-us1.com',
		ACTIVECAMPAIGN_API_KEY='test-key',
		ACTIVECAMPAIGN_REFERRER_NOTIFICATION_TAG_ID='901',
		ACTIVECAMPAIGN_REFERRER_USER_ID_FIELD_NAME='Latest Referred User ID',
		ACTIVECAMPAIGN_REFERRER_CODE_FIELD_NAME='Latest Referral Code Used',
	)
	def test_notify_referrer_creates_note_and_tag(self):
		referrer_user = SimpleNamespace(
			email='referrer@example.com',
			first_name='Ref',
			last_name='Errer',
		)
		referred_user = SimpleNamespace(
			id=42,
			email='newmember@example.com',
		)

		post_calls = []
		put_calls = []

		def fake_post(url, payload, api_key):
			post_calls.append((url, payload, api_key))
			if url.endswith('/contact/sync'):
				return {'contact': {'id': '777'}}
			if url.endswith('/fieldValues'):
				return {'fieldValue': {'id': '444'}}
			return {}

		def fake_get(url, api_key):
			if '/fields?search=' in url:
				return {
					'fields': [
						{'id': '301', 'title': 'Latest Referred User ID'},
						{'id': '302', 'title': 'Latest Referral Code Used'},
					]
				}
			if '/contacts/777/fieldValues' in url:
				return {'fieldValues': []}
			return {}

		with patch.object(activecampaign, '_post_json', side_effect=fake_post), patch.object(
			activecampaign,
			'_get_json',
			side_effect=fake_get,
		), patch.object(activecampaign, '_put_json', side_effect=lambda url, payload, api_key: put_calls.append((url, payload, api_key)) or {}):
			result = activecampaign.notify_referrer_of_signup(
				referrer_user=referrer_user,
				referred_user=referred_user,
				referral_code='ABC123',
			)

		self.assertTrue(result['success'])
		self.assertEqual(result['contact_id'], '777')
		self.assertEqual(result['referred_identifier'], 'LXT-000042')

		note_calls = [call for call in post_calls if call[0].endswith('/notes')]
		self.assertEqual(len(note_calls), 1)
		self.assertIn('LXT-000042', note_calls[0][1]['note']['note'])
		self.assertNotIn('newmember@example.com', note_calls[0][1]['note']['note'])

		tag_calls = [
			call
			for call in post_calls
			if call[0].endswith('/contactTags') and call[1].get('contactTag', {}).get('tag') == '901'
		]
		self.assertEqual(len(tag_calls), 1)

		field_value_calls = [
			call for call in post_calls if call[0].endswith('/fieldValues')
		]
		self.assertEqual(len(field_value_calls), 2)
		self.assertEqual(len(put_calls), 0)
		self.assertEqual(
			{
				call[1]['fieldValue']['field']: call[1]['fieldValue']['value']
				for call in field_value_calls
			},
			{
				'301': 'LXT-000042',
				'302': 'ABC123',
			}
		)

	def test_build_referred_user_identifier_hides_contact_details(self):
		referred_user = SimpleNamespace(
			id=123,
			email='private@example.com',
		)

		identifier = activecampaign.build_referred_user_identifier(referred_user)
		self.assertEqual(identifier, 'LXT-000123')


class SimpleUserCreationFormEmailUniquenessTests(TestCase):
	def test_rejects_duplicate_email_case_insensitive(self):
		User.objects.create_user(
			username='existing-user',
			email='existing@example.com',
			password='ExistingPass123!'
		)

		form = SimpleUserCreationForm(data={
			'username': 'new-user',
			'first_name': 'New',
			'last_name': 'Person',
			'email': 'EXISTING@example.com',
			'password1': 'StrongPass123!',
			'password2': 'StrongPass123!',
			'agree_terms': True,
			'agree_gdpr': True,
		})

		self.assertFalse(form.is_valid())
		self.assertIn('email', form.errors)

	def test_accepts_unique_email(self):
		form = SimpleUserCreationForm(data={
			'username': 'unique-user',
			'first_name': 'Unique',
			'last_name': 'Person',
			'email': 'unique@example.com',
			'password1': 'StrongPass123!',
			'password2': 'StrongPass123!',
			'agree_terms': True,
			'agree_gdpr': True,
		})

		self.assertTrue(form.is_valid())

	def test_rejects_missing_terms_or_gdpr_consent(self):
		form = SimpleUserCreationForm(data={
			'username': 'consent-user',
			'first_name': 'Consent',
			'last_name': 'Missing',
			'email': 'consent@example.com',
			'password1': 'StrongPass123!',
			'password2': 'StrongPass123!',
		})

		self.assertFalse(form.is_valid())
		self.assertIn('agree_terms', form.errors)
		self.assertIn('agree_gdpr', form.errors)


class UserEmailDatabaseUniquenessTests(TestCase):
	def test_database_rejects_duplicate_email_case_insensitive(self):
		User.objects.create_user(
			username='db-existing-user',
			email='dbexisting@example.com',
			password='ExistingPass123!'
		)

		with self.assertRaises(IntegrityError):
			User.objects.create_user(
				username='db-new-user',
				email='DBEXISTING@example.com',
				password='StrongPass123!'
			)


class ReferralCodeMatchingTests(TestCase):
	def test_matches_referrer_by_referral_code(self):
		referrer = User.objects.create_user(
			username='ref-owner',
			email='ref-owner@example.com',
			password='StrongPass123!'
		)
		referrer.profile.can_refer = True
		referrer.profile.referral_code = 'ABC12345'
		referrer.profile.save(update_fields=['can_refer', 'referral_code'])

		profile = _find_referrer_profile('abc-12345')
		self.assertIsNotNone(profile)
		self.assertEqual(profile.user_id, referrer.id)

	def test_does_not_match_referrer_when_not_manually_enabled(self):
		referrer = User.objects.create_user(
			username='disabled-ref-owner',
			email='disabled-ref-owner@example.com',
			password='StrongPass123!'
		)
		referrer.profile.can_refer = False
		referrer.profile.referral_code = 'DISABLED1'
		referrer.profile.save(update_fields=['can_refer', 'referral_code'])

		profile = _find_referrer_profile('DISABLED1')
		self.assertIsNone(profile)

	def test_does_not_match_referrer_by_username_only(self):
		referrer = User.objects.create_user(
			username='username-only-ref',
			email='username-only-ref@example.com',
			password='StrongPass123!'
		)

		profile = _find_referrer_profile(referrer.username)
		self.assertIsNone(profile)


class ReferrerAdminModelTests(TestCase):
	def test_creating_referrer_creates_user_and_referral_urls(self):
		referrer = Referrer.objects.create(
			first_name='Manual',
			last_name='Referrer',
			email='manual.referrer@example.com',
			is_active=True,
		)

		self.assertIsNotNone(referrer.user_id)
		self.assertTrue(bool(referrer.referral_code))
		self.assertTrue(referrer.user.profile.can_refer)
		self.assertIn('?ref=', referrer.referral_landing_url)
		self.assertIn('/users/register/?ref=', referrer.referral_signup_url)

	def test_disabling_referrer_revokes_referral_eligibility(self):
		referrer = Referrer.objects.create(
			first_name='Manual',
			last_name='Disable',
			email='manual.disable@example.com',
			is_active=True,
		)

		self.assertIsNotNone(_find_referrer_profile(referrer.referral_code))

		referrer.is_active = False
		referrer.save(update_fields=['is_active'])
		referrer.refresh_from_db()

		self.assertFalse(referrer.user.profile.can_refer)
		self.assertIsNone(_find_referrer_profile(referrer.referral_code))
