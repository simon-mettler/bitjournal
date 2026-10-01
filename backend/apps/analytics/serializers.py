from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from apps.signals.models import Signal
from apps.signals.serializers import SignalSerializer

from .models import (
    TIMESERIES_EXCLUDED_TIMEFRAMES,
    AnalyticsBoard,
    AnalyticsWidget,
    WidgetAggregation,
    WidgetChartType,
    WidgetTimeframe,
    WidgetType,
)
from .services import TIMEFRAMES


def validate_tz_name(value):
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError:
        raise serializers.ValidationError('Unknown timezone.')
    return value


class SignalStatsQuerySerializer(serializers.Serializer):
    timeframe = serializers.ChoiceField(choices=TIMEFRAMES)
    period_start = serializers.DateField()
    tz = serializers.CharField(validators=[validate_tz_name])


class TimezoneQuerySerializer(serializers.Serializer):
    tz = serializers.CharField(validators=[validate_tz_name])


class AnalyticsWidgetSerializer(serializers.ModelSerializer):
    signal = SignalSerializer(read_only=True)

    class Meta:
        model = AnalyticsWidget
        fields = [
            'id', 'order', 'type', 'title', 'signal', 'aggregation', 'chart_type', 'show_average',
            'timeframe', 'period_start', 'days',
        ]


class AnalyticsBoardSerializer(serializers.ModelSerializer):
    widgets = AnalyticsWidgetSerializer(many=True, read_only=True)

    class Meta:
        model = AnalyticsBoard
        fields = ['id', 'name', 'order', 'widgets', 'created_at']


class AnalyticsBoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsBoard
        fields = ['name']


class AnalyticsWidgetWriteSerializer(serializers.ModelSerializer):
    signal_id = serializers.PrimaryKeyRelatedField(source='signal', queryset=Signal.objects.none())

    class Meta:
        model = AnalyticsWidget
        fields = [
            'type', 'title', 'aggregation', 'chart_type', 'show_average', 'timeframe',
            'period_start', 'days', 'signal_id',
        ]
        extra_kwargs = {'days': {'min_value': 1, 'max_value': 1095}}

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        fields['signal_id'].queryset = Signal.objects.filter(user=user)
        if 'board_id' in fields:
            fields['board_id'].queryset = AnalyticsBoard.objects.filter(user=user)
        return fields

    def validate(self, attrs):
        timeframe = attrs['timeframe']
        is_timeseries = attrs.get('type', getattr(self.instance, 'type', None)) == WidgetType.TIMESERIES
        if is_timeseries and timeframe in TIMESERIES_EXCLUDED_TIMEFRAMES:
            raise serializers.ValidationError(
                {'timeframe': 'Over time widgets need a timeframe of more than one day.'}
            )
        if timeframe in (WidgetTimeframe.QUARTER, WidgetTimeframe.YEAR):
            if attrs.get('period_start') is None:
                raise serializers.ValidationError({'period_start': 'Required for this timeframe.'})
        else:
            attrs['period_start'] = None
        if timeframe == WidgetTimeframe.LAST_DAYS:
            if attrs.get('days') is None:
                raise serializers.ValidationError({'days': 'Required for this timeframe.'})
        else:
            attrs['days'] = None
        if is_timeseries:
            attrs['aggregation'] = WidgetAggregation.TOTAL
        else:
            attrs['chart_type'] = WidgetChartType.BAR
            attrs['show_average'] = True
        return attrs


class AnalyticsWidgetCreateSerializer(AnalyticsWidgetWriteSerializer):
    board_id = serializers.PrimaryKeyRelatedField(source='board', queryset=AnalyticsBoard.objects.none())

    class Meta(AnalyticsWidgetWriteSerializer.Meta):
        fields = [*AnalyticsWidgetWriteSerializer.Meta.fields, 'board_id']


class AnalyticsBoardUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    widget_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True, max_length=100)

    def validate_widget_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Duplicate widget ids.')
        return value


class AnalyticsBoardReorderSerializer(serializers.Serializer):
    board_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True, max_length=100)

    def validate_board_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Duplicate board ids.')
        return value
