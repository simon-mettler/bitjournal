from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from .services import TIMEFRAMES


class SignalStatsQuerySerializer(serializers.Serializer):
    timeframe = serializers.ChoiceField(choices=TIMEFRAMES)
    period_start = serializers.DateField()
    tz = serializers.CharField()

    def validate_tz(self, value):
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError:
            raise serializers.ValidationError('Unknown timezone.')
        return value
