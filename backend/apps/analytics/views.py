from zoneinfo import ZoneInfo

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.signals.models import Signal

from .serializers import SignalStatsQuerySerializer
from .services import (
    get_signal_day_of_week,
    get_signal_heatmap,
    get_signal_timeseries,
    get_signal_totals,
    resolve_period,
)


class SignalStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, signal_id):
        query = SignalStatsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data

        signal = get_object_or_404(Signal, pk=signal_id, user=request.user)
        period = resolve_period(
            timeframe=params['timeframe'],
            period_start=params['period_start'],
            tz=ZoneInfo(params['tz']),
        )
        totals = get_signal_totals(signal, request.user, period)
        timeseries = get_signal_timeseries(signal, request.user, period)
        day_of_week = get_signal_day_of_week(signal, request.user, period)
        heatmap = get_signal_heatmap(signal, request.user, period)

        return Response({
            'signal': {
                'id': signal.id,
                'summary_method': signal.summary_method,
            },
            'period': {
                'start': period.start_local.isoformat(),
                'end': period.end_local.isoformat(),
                'timeframe': period.timeframe,
            },
            'total': totals['total'],
            'average': totals['average'],
            'count': totals['count'],
            'timeseries': timeseries,
            'day_of_week': day_of_week,
            'heatmap': heatmap,
        })
