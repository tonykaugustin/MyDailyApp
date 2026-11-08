from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class AuthAndDashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration_and_automatic_seed(self):
        res = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'display_name': 'New User'
        })
        self.assertEqual(res.status_code, 201)

        # Login to obtain JWT
        login_res = self.client.post('/api/auth/login/', {
            'username': 'newuser',
            'password': 'password123'
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Check dashboard summary API
        dash_res = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn('stats', dash_res.data)
        self.assertIn('today_schedule', dash_res.data)
        self.assertIn('weekly_summary', dash_res.data)
