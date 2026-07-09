from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Tracker, TrackerCategory
from .serializers import TrackerCategorySerializer, TrackerSerializer

class TrackerCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TrackerCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TrackerCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TrackerViewSet(viewsets.ModelViewSet):
    serializer_class = TrackerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Tracker.objects.filter(user=self.request.user).select_related(
            'category', 'range_config', 'value_config'
        )

        category = self.request.query_params.get('category')
        tracker_type = self.request.query_params.get('type')
        is_archived = self.request.query_params.get('is_archived')

        if category is not None:
            qs = qs.filter(category_id=category)
        if tracker_type is not None:
            qs = qs.filter(type=tracker_type)
        if is_archived is not None:
            qs = qs.filter(is_archived=is_archived.lower() == 'true')

        return qs
