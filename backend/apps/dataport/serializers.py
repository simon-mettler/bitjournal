from rest_framework import serializers

MAX_IMPORT_BYTES = 100 * 1024 * 1024


def _max_size(file):
    if file.size > MAX_IMPORT_BYTES:
        raise serializers.ValidationError('The file is too large.')


class ImportSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[_max_size])
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Password is incorrect.')
        return value
