from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Property


class PropertyAnalysisRegressionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='safe-password-123',
        )
        self.client.login(username='tester', password='safe-password-123')

    def test_property_detail_allows_zero_estimated_market_value(self):
        property_obj = Property.objects.create(
            owner=self.user,
            property_name='Zero Value Test',
            property_type='semi',
            street_name='High Street',
            city='London',
            postcode='SW1A1AA',
            number_bedrooms=2,
            number_bathrooms=1,
            purchase_price=200000,
            estimated_market_value=0,
            weekly_rent=350,
            date_of_purchase=date(2024, 1, 1),
            ownership_status='individual',
        )

        response = self.client.get(reverse('user_home:property_detail', args=[property_obj.slug]))

        self.assertEqual(response.status_code, 200)

    def test_upload_property_flow_handles_blank_market_value(self):
        response = self.client.post(
            reverse('user_home:upload_property'),
            {
                'property_name': 'Uploaded Test Property',
                'property_type': 'semi',
                'street_name': 'Main Road',
                'street_number': '12',
                'city': 'Bristol',
                'postcode': 'BS11AA',
                'number_bedrooms': 3,
                'number_bathrooms': 1,
                'purchase_price': 180000,
                'estimated_market_value': '',
                'weekly_rent': 300,
                'date_of_purchase': '2024-01-01',
                'ownership_status': 'individual',
                'deposit_paid': 20000,
                'annual_income': 35000,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Uploaded Test Property')
