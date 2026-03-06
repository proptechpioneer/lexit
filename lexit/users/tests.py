from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from . import activecampaign


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
