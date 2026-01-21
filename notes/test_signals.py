from django.test import TestCase
from django.contrib.auth import get_user_model
from notes.models import Category

User = get_user_model()


class SignalTests(TestCase):
    """Test signal handlers"""

    def test_default_categories_created_on_user_creation(self):
        """Test that default categories are created when a new user is created"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        # Check that default categories were created
        categories = Category.objects.filter(user=user)
        category_names = [cat.name for cat in categories]

        self.assertGreaterEqual(categories.count(), 3)
        self.assertIn('Random Thoughts', category_names)
        self.assertIn('School', category_names)
        self.assertIn('Personal', category_names)

    def test_default_categories_have_colors(self):
        """Test that default categories are created with proper colors"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        categories = Category.objects.filter(user=user)
        
        for category in categories:
            self.assertIsNotNone(category.color)
            self.assertTrue(category.color.startswith('#'))

    def test_no_duplicate_default_categories(self):
        """Test that default categories are only created once per user"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        initial_count = Category.objects.filter(user=user).count()

        # Trigger save again (shouldn't create duplicates)
        user.save()

        final_count = Category.objects.filter(user=user).count()
        self.assertEqual(initial_count, final_count)
