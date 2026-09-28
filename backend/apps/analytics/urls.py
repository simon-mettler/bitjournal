from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AnalyticsBoardViewSet, AnalyticsWidgetViewSet, SignalStatsView

router = DefaultRouter()
router.register('analytics-boards', AnalyticsBoardViewSet, basename='analytics-board')
router.register('analytics-widgets', AnalyticsWidgetViewSet, basename='analytics-widget')

urlpatterns = [
    path('analytics/signals/<uuid:signal_id>/stats/', SignalStatsView.as_view(), name='signal-stats'),
    *router.urls,
]
