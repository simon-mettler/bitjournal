from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.signals.models import Signal

from .models import AnalyticsBoard, AnalyticsWidget
from .serializers import (
    AnalyticsBoardCreateSerializer,
    AnalyticsBoardReorderSerializer,
    AnalyticsBoardSerializer,
    AnalyticsBoardUpdateSerializer,
    AnalyticsWidgetCreateSerializer,
    AnalyticsWidgetSerializer,
    AnalyticsWidgetWriteSerializer,
    SignalStatsQuerySerializer,
    TimezoneQuerySerializer,
)
from .services import (
    get_signal_day_of_week,
    get_signal_heatmap,
    get_signal_timeseries,
    get_signal_totals,
    get_widget_values,
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


class AnalyticsBoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            AnalyticsBoard.objects
            .filter(user=self.request.user)
            .prefetch_related('widgets__signal')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return AnalyticsBoardCreateSerializer
        if self.action in ('update', 'partial_update'):
            return AnalyticsBoardUpdateSerializer
        if self.action == 'reorder':
            return AnalyticsBoardReorderSerializer
        return AnalyticsBoardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer.save(user=request.user)
        except IntegrityError:
            return Response(
                {'name': 'A board with this name already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            AnalyticsBoardSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        return self._save_board(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'PATCH is not supported.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @transaction.atomic
    def _save_board(self, request, *args, **kwargs):
        board = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        board.name = data['name']
        try:
            with transaction.atomic():
                board.save(update_fields=['name'])
        except IntegrityError:
            return Response(
                {'name': 'A board with this name already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        widget_ids = [str(wid) for wid in data['widget_ids']]
        widgets = {str(w.id): w for w in board.widgets.all()}
        unknown = set(widget_ids) - set(widgets.keys())
        if unknown:
            transaction.set_rollback(True)
            return Response(
                {'widget_ids': f'Unknown widget ids for this board: {sorted(unknown)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # widgets left out of widget_ids are removed, the rest reordered.
        board.widgets.exclude(pk__in=widget_ids).delete()
        for index, widget_id in enumerate(widget_ids):
            widget = widgets[widget_id]
            if widget.order != index:
                widget.order = index
                widget.save(update_fields=['order'])

        board = self.get_queryset().get(pk=board.pk)
        return Response(AnalyticsBoardSerializer(board).data)

    @action(detail=True, methods=['get'], url_path='values')
    def values(self, request, pk=None):
        query = TimezoneQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        tz = ZoneInfo(query.validated_data['tz'])

        board = self.get_object()
        return Response([
            get_widget_values(widget, request.user, tz)
            for widget in board.widgets.all()
        ])

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board_ids = [str(bid) for bid in serializer.validated_data['board_ids']]

        boards = {str(b.id): b for b in self.get_queryset()}

        # check if request contains exactly all boards
        if len(board_ids) != len(boards) or set(board_ids) != set(boards.keys()):
            return Response(
                {'detail': 'board_ids must match exactly your current boards.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for index, board_id in enumerate(board_ids):
                board = boards[board_id]
                if board.order != index:
                    board.order = index
                    board.save(update_fields=['order'])

        ordered_boards = [boards[bid] for bid in board_ids]
        return Response(AnalyticsBoardSerializer(ordered_boards, many=True).data)


class AnalyticsWidgetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            AnalyticsWidget.objects
            .filter(board__user=self.request.user)
            .select_related('signal')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return AnalyticsWidgetCreateSerializer
        if self.action in ('update', 'partial_update'):
            return AnalyticsWidgetWriteSerializer
        return AnalyticsWidgetSerializer

    def _get_signal(self, signal_id):
        return get_object_or_404(Signal, pk=signal_id, user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        board = get_object_or_404(AnalyticsBoard, pk=data.pop('board_id'), user=request.user)
        signal = self._get_signal(data.pop('signal_id'))

        widget = AnalyticsWidget.objects.create(
            board=board,
            signal=signal,
            order=board.widgets.count(),
            **data,
        )
        return Response(AnalyticsWidgetSerializer(widget).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        widget = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        widget.signal = self._get_signal(data.pop('signal_id'))
        for field, value in data.items():
            setattr(widget, field, value)
        widget.save()
        return Response(AnalyticsWidgetSerializer(widget).data)

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'PATCH is not supported.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
