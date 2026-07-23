from rest_framework import serializers

from .models import (
    Signal,
    SignalType,
    SignalCategory,
    SignalRangeConfig,
    SignalValueConfig
)

class SignalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalCategory
        fields = ['id', 'name', 'icon', 'color']


class SignalRangeConfigSerializer(serializers.ModelSerializer):
    min_value = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    max_value = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = SignalRangeConfig
        fields = ['min_value', 'max_value', 'min_label', 'max_label']


class SignalValueConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalValueConfig
        fields = ["unit"]


class SignalSerializer(serializers.ModelSerializer):
    range_config = SignalRangeConfigSerializer(required=False)
    value_config = SignalValueConfigSerializer(required=False)

    class Meta:
        model = Signal 
        fields = [
            'id',
            'category',
            'name',
            'type',
            'icon',
            'color',
            'summary_method',
            'is_archived',
            'range_config',
            'value_config',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    
    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields['type'].read_only = True
        return fields

    
    def validate(self, attrs):
        signal_type = attrs.get('type', getattr(self.instance, 'type', None))
        range_config = attrs.get('range_config')
        value_config = attrs.get('value_config')

        if signal_type == SignalType.RANGE and range_config is None and self.instance is None:
            raise serializers.ValidationError({'range_config': 'Required for range signals.'})
        if signal_type == SignalType.VALUE and value_config is None and self.instance is None:
            raise serializers.ValidationError({'value_config': 'Required for value signals.'})
        if signal_type != SignalType.RANGE and range_config is not None:
            raise serializers.ValidationError({'range_config': 'Only allowed for range signals.'})
        if signal_type != SignalType.VALUE and value_config is not None:
            raise serializers.ValidationError({'value_config': 'Only allowed for value signals.'})

        return attrs

    
    def create(self, validated_data):
        range_config_data = validated_data.pop('range_config', None)
        value_config_data = validated_data.pop('value_config', None)
        validated_data['user'] = self.context['request'].user

        signal = Signal.objects.create(**validated_data)

        if range_config_data is not None:
            SignalRangeConfig.objects.create(signal=signal, **range_config_data)
        if value_config_data is not None:
            SignalValueConfig.objects.create(signal=signal, **value_config_data)

        return signal


    def update(self, instance, validated_data):
        range_config_data = validated_data.pop('range_config', None)
        value_config_data = validated_data.pop('value_config', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if range_config_data is not None and hasattr(instance, 'range_config'):
            for attr, value in range_config_data.items():
                setattr(instance.range_config, attr, value)
            instance.range_config.save()

        if value_config_data is not None and hasattr(instance, 'value_config'):
            for attr, value in value_config_data.items():
                setattr(instance.value_config, attr, value)
            instance.value_config.save()

        return instance
