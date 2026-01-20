from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Category

User = get_user_model()

# Default categories with their colors
DEFAULT_CATEGORIES = [
    {'name': 'Random Thoughts', 'color': '#EF9C66'},
    {'name': 'School', 'color': '#FCDC94'},
    {'name': 'Personal', 'color': '#C8CFA0'},
]


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    """Create default categories when a new user is created."""
    if created:
        for category_data in DEFAULT_CATEGORIES:
            Category.objects.create(
                name=category_data['name'],
                color=category_data['color'],
                user=instance
            )
