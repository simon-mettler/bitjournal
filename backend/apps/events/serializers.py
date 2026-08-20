from rest_framework import serializers
from apps.signals.serializers import SignalSerializer
from .models import Event, SignalEntry


class SignalEntrySerializer(serializers.ModelSerializer):
    signal = SignalSerializer(read_only=True)

    class Meta:
        model = SignalEntry
        fields = ['signal', 'value', 'duration']


class EventSerializer(serializers.ModelSerializer):
    entries = SignalEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'occurred_at', 'note', 'entries', 'created_at', 'updated_at']


class SignalEntryInputSerializer(serializers.Serializer):
    signal_id = serializers.UUIDField()
    value = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    duration = serializers.DurationField(required=False, allow_null=True)

    def validate(self, attrs):
        value = attrs.get('value')
        duration = attrs.get('duration')
        if value is not None and duration is not None:
            raise serializers.ValidationError('Only one of value or duration may be set.')
        if value is None and duration is None:
            raise serializers.ValidationError('Either value or duration must be set.')
        return attrs


class EventWriteSerializer(serializers.Serializer):
    occurred_at = serializers.DateTimeField()
    note = serializers.CharField(required=False, allow_blank=True, default='')
    entries = SignalEntryInputSerializer(many=True)

    def validate_entries(self, value):
        if not value:
            raise serializers.ValidationError('At least one entry is required.')
        return value
