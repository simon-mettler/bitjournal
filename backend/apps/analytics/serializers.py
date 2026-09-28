from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from apps.signals.serializers import SignalSerializer

from .models import AnalyticsBoard, AnalyticsWidget, WidgetAggregation, WidgetTimeframe, WidgetType
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
        fields = ['id', 'order', 'type', 'title', 'signal', 'aggregation', 'timeframe', 'period_start', 'days']


class AnalyticsBoardSerializer(serializers.ModelSerializer):
    widgets = AnalyticsWidgetSerializer(many=True, read_only=True)

    class Meta:
        model = AnalyticsBoard
        fields = ['id', 'name', 'order', 'widgets', 'created_at']


class AnalyticsBoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsBoard
        fields = ['name']


class AnalyticsWidgetWriteSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=WidgetType.choices, default=WidgetType.VALUE)
    title = serializers.CharField(max_length=100)
    signal_id = serializers.UUIDField()
    aggregation = serializers.ChoiceField(choices=WidgetAggregation.choices)
    timeframe = serializers.ChoiceField(choices=WidgetTimeframe.choices)
    period_start = serializers.DateField(required=False, allow_null=True, default=None)
    days = serializers.IntegerField(required=False, allow_null=True, default=None, min_value=1)

    def validate(self, attrs):
        timeframe = attrs['timeframe']
        if timeframe in (WidgetTimeframe.QUARTER, WidgetTimeframe.YEAR):
            if attrs['period_start'] is None:
                raise serializers.ValidationError({'period_start': 'Required for this timeframe.'})
        else:
            attrs['period_start'] = None
        if timeframe == WidgetTimeframe.LAST_DAYS:
            if attrs['days'] is None:
                raise serializers.ValidationError({'days': 'Required for this timeframe.'})
        else:
            attrs['days'] = None
        return attrs


class AnalyticsWidgetCreateSerializer(AnalyticsWidgetWriteSerializer):
    board_id = serializers.UUIDField()


class AnalyticsBoardUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    widget_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)

    def validate_widget_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Duplicate widget ids.')
        return value


class AnalyticsBoardReorderSerializer(serializers.Serializer):
    board_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)

    def validate_board_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Duplicate board ids.')
        return value
