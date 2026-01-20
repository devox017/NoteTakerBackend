from rest_framework import serializers
from .models import Category, Note


class CategorySerializer(serializers.ModelSerializer):
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'color', 'notes_count')
        read_only_fields = ('id',)

    def get_notes_count(self, obj):
        return obj.notes.count()


class NoteSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'category', 'category_name', 'category_color', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'category_name', 'category_color')


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'category', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
