from django.urls import path

from .views import SignalStatsView

urlpatterns = [
    path('analytics/signals/<uuid:signal_id>/stats/', SignalStatsView.as_view(), name='signal-stats'),
]
