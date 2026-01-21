from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserModelTests(TestCase):
    """Test User model"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        email = 'test@EXAMPLE.COM'
        user = User.objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            User.objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = User.objects.create_superuser(
            'admin@example.com',
            'test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class AuthenticationAPITests(TestCase):
    """Test authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def test_register_user_success(self):
        """Test registering a new user successfully"""
        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])

        # Check user was created in database
        user_exists = User.objects.filter(
            email=self.user_data['email']
        ).exists()
        self.assertTrue(user_exists)

    def test_register_user_duplicate_email(self):
        """Test registering a user with existing email fails"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_short_password(self):
        """Test that password must be at least 8 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'short'
        }
        response = self.client.post(self.register_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success(self):
        """Test logging in a user successfully"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        """Test logging in with invalid credentials fails"""
        User.objects.create_user(**self.user_data)
        payload = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test logging in with non-existent user fails"""
        response = self.client.post(self.login_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for user profile"""
        response = self.client.get('/api/auth/user/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
