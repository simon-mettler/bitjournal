from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Signal, SignalCategory
from .serializers import SignalCategorySerializer, SignalSerializer

class SignalCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = SignalCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SignalCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SignalViewSet(viewsets.ModelViewSet):
    serializer_class = SignalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Signal.objects.filter(user=self.request.user).select_related(
            'category', 'range_config', 'value_config'
        )

        category = self.request.query_params.get('category')
        signal_type = self.request.query_params.get('type')
        is_archived = self.request.query_params.get('is_archived')

        if category is not None:
            qs = qs.filter(category_id=category)
        if signal_type is not None:
            qs = qs.filter(type=signal_type)
        if is_archived is not None:
            qs = qs.filter(is_archived=is_archived.lower() == 'true')

        return qs
