from rest_framework import serializers
from .models import SignalBoard, BoardSignal
from signals.serializers import SignalSerializer  # adjust import to your actual module


class BoardSignalSerializer(serializers.ModelSerializer):
    signal = SignalSerializer(read_only=True)

    class Meta:
        model = BoardSignal
        fields = ['signal', 'order']


class SignalBoardSerializer(serializers.ModelSerializer):
    board_signals = BoardSignalSerializer(many=True, read_only=True)

    class Meta:
        model = SignalBoard
        fields = ['id', 'name', 'order', 'board_signals', 'created_at']


class SignalBoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalBoard
        fields = ['name']

def validate_no_duplicates(value, field_name):
    if len(value) != len(set(value)):
        raise serializers.ValidationError(f'Duplicate {field_name}.')
    return value


class SignalBoardUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    signal_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)

    def validate_signal_ids(self, value):
        return validate_no_duplicates(value, 'signal ids')


class BoardReorderSerializer(serializers.Serializer):
    board_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)

    def validate_board_ids(self, value):
        return validate_no_duplicates(value, 'board ids')
