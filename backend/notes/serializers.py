from rest_framework import serializers
from .models import Note
from categories.serializers import CategorySerializer
from categories.models import Category

class NoteSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'category', 'category_details',
            'is_pinned', 'color', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

