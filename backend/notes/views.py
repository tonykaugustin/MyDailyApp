from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def get_queryset(self):
        qs = Note.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        pinned = self.request.query_params.get('pinned')
        tag = self.request.query_params.get('tag')

        if category:
            qs = qs.filter(category_id=category)
        if pinned is not None:
            qs = qs.filter(is_pinned=(pinned.lower() == 'true'))
        if tag:
            qs = qs.filter(tags__contains=[tag])

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle-pin')
    def toggle_pin(self, request, pk=None):
        note = self.get_object()
        note.is_pinned = not note.is_pinned
        note.save(update_fields=['is_pinned', 'updated_at'])
        return Response(NoteSerializer(note).data)
