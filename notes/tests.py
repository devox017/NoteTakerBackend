from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import Category, Note

User = get_user_model()


class CategoryModelTests(TestCase):
    """Test Category model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(
            user=self.user,
            name='Work',
            color='#EF9C66'
        )

        self.assertEqual(str(category), 'Work')
        self.assertEqual(category.user, self.user)
        self.assertEqual(category.color, '#EF9C66')

    def test_category_notes_count(self):
        """Test that category tracks notes count correctly"""
        category = Category.objects.create(
            user=self.user,
            name='Work',
            color='#EF9C66'
        )

        # Initially no notes - check via API
        from .serializers import CategorySerializer
        serializer = CategorySerializer(category)
        self.assertEqual(serializer.data['notes_count'], 0)

        # Create notes
        Note.objects.create(
            user=self.user,
            category=category,
            title='Note 1',
            content='Content 1'
        )
        Note.objects.create(
            user=self.user,
            category=category,
            title='Note 2',
            content='Content 2'
        )

        # Check via serializer again
        serializer = CategorySerializer(category)
        self.assertEqual(serializer.data['notes_count'], 2)


class NoteModelTests(TestCase):
    """Test Note model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        # Get one of the default categories instead of creating "Personal"
        self.category = Category.objects.filter(user=self.user).first()

    def test_create_note(self):
        """Test creating a note"""
        note = Note.objects.create(
            user=self.user,
            category=self.category,
            title='Test Note',
            content='Test content'
        )

        self.assertEqual(str(note), 'Test Note')
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.category, self.category)

    def test_note_auto_timestamps(self):
        """Test that note timestamps are automatically set"""
        note = Note.objects.create(
            user=self.user,
            category=self.category,
            title='Test Note'
        )

        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.updated_at)

    def test_note_title_max_length(self):
        """Test that note title max length constraint is enforced"""
        long_title = 'a' * 256
        note = Note(
            user=self.user,
            category=self.category,
            title=long_title
        )

        # This should raise a validation error when saved
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            note.full_clean()


class CategoryAPITests(TestCase):
    """Test Category API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_categories(self):
        """Test retrieving a list of categories"""
        Category.objects.create(user=self.user, name='Work', color='#EF9C66')
        Category.objects.create(user=self.user, name='Study', color='#C8CFA0')

        response = self.client.get('/api/categories/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include default categories + created ones
        self.assertGreaterEqual(len(response.data), 2)

    def test_categories_limited_to_user(self):
        """Test that categories are limited to authenticated user"""
        Category.objects.create(user=self.user, name='User1 Category', color='#EF9C66')
        
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        Category.objects.create(user=other_user, name='User2 Category', color='#C8CFA0')

        response = self.client.get('/api/categories/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that other user's category is not included
        category_names = [cat['name'] for cat in response.data]
        self.assertIn('User1 Category', category_names)
        self.assertNotIn('User2 Category', category_names)

    def test_create_category(self):
        """Test creating a category via API"""
        initial_count = Category.objects.filter(user=self.user).count()
        
        payload = {'name': 'New Category', 'color': '#FCDC94'}
        response = self.client.post('/api/categories/', payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], payload['name'])
        self.assertEqual(response.data['color'], payload['color'])
        
        # Check category was created
        new_count = Category.objects.filter(user=self.user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_retrieve_categories_unauthenticated(self):
        """Test authentication is required to retrieve categories"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/categories/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NoteAPITests(TestCase):
    """Test Note API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        # Get one of the default categories
        self.category = Category.objects.filter(user=self.user).first()

    def test_retrieve_notes(self):
        """Test retrieving a list of notes"""
        Note.objects.create(
            user=self.user,
            category=self.category,
            title='Note 1',
            content='Content 1'
        )
        Note.objects.create(
            user=self.user,
            category=self.category,
            title='Note 2',
            content='Content 2'
        )

        response = self.client.get('/api/notes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_notes_by_category(self):
        """Test filtering notes by category"""
        # Get another default category
        all_categories = Category.objects.filter(user=self.user)
        category2 = all_categories.exclude(id=self.category.id).first()

        Note.objects.create(
            user=self.user,
            category=self.category,
            title='Work Note'
        )
        Note.objects.create(
            user=self.user,
            category=category2,
            title='Other Note'
        )

        response = self.client.get(
            f'/api/notes/?category={self.category.id}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Work Note')

    def test_notes_limited_to_user(self):
        """Test that notes are limited to authenticated user"""
        Note.objects.create(
            user=self.user,
            category=self.category,
            title='User1 Note'
        )

        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        other_category = Category.objects.filter(user=other_user).first()
        Note.objects.create(
            user=other_user,
            category=other_category,
            title='User2 Note'
        )

        response = self.client.get('/api/notes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'User1 Note')

    def test_create_note(self):
        """Test creating a new note"""
        payload = {
            'category': self.category.id,
            'title': 'New Note',
            'content': 'Note content'
        }
        response = self.client.post('/api/notes/', payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertEqual(response.data['content'], payload['content'])

        # Check note exists in database
        note_exists = Note.objects.filter(
            user=self.user,
            title=payload['title']
        ).exists()
        self.assertTrue(note_exists)

    def test_create_note_with_minimal_data(self):
        """Test creating a note with only required fields"""
        payload = {}
        response = self.client.post('/api/notes/', payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should create with default category
        self.assertIsNotNone(response.data['category'])

    def test_update_note(self):
        """Test updating a note"""
        note = Note.objects.create(
            user=self.user,
            category=self.category,
            title='Original Title',
            content='Original Content'
        )

        payload = {
            'title': 'Updated Title',
            'content': 'Updated Content'
        }
        response = self.client.patch(
            f'/api/notes/{note.id}/',
            payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.title, payload['title'])
        self.assertEqual(note.content, payload['content'])

    def test_update_note_category(self):
        """Test updating note category"""
        note = Note.objects.create(
            user=self.user,
            category=self.category,
            title='Note'
        )
        # Get another default category
        all_categories = Category.objects.filter(user=self.user)
        new_category = all_categories.exclude(id=self.category.id).first()

        payload = {'category': new_category.id}
        response = self.client.patch(
            f'/api/notes/{note.id}/',
            payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.category, new_category)

    def test_delete_note(self):
        """Test deleting a note"""
        note = Note.objects.create(
            user=self.user,
            category=self.category,
            title='Note to Delete'
        )

        response = self.client.delete(f'/api/notes/{note.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(id=note.id).exists())

    def test_delete_other_user_note_fails(self):
        """Test that users cannot delete other users' notes"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        other_category = Category.objects.filter(user=other_user).first()
        other_note = Note.objects.create(
            user=other_user,
            category=other_category,
            title='Other User Note'
        )

        response = self.client.delete(f'/api/notes/{other_note.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Note should still exist
        self.assertTrue(Note.objects.filter(id=other_note.id).exists())

    def test_note_title_max_length(self):
        """Test that note title cannot exceed 255 characters"""
        long_title = 'a' * 256
        payload = {
            'category': self.category.id,
            'title': long_title,
            'content': 'Content'
        }
        response = self.client.post('/api/notes/', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_retrieve_notes_unauthenticated(self):
        """Test authentication is required to retrieve notes"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/notes/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
