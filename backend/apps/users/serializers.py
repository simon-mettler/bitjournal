from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

User = get_user_model()

EMAIL_CHANGE_SALT = 'users.email-change'

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), lookup='iexact')]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password']

    def validate(self, attrs):
        try:
            validate_password(attrs['password'], User(email=attrs['email']))
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password']
        )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value, self.context['request'].user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Password is incorrect.')
        return value

    def validate_email(self, value):
        if value.strip().lower() != self.context['request'].user.email.lower():
            raise serializers.ValidationError('Email does not match your account.')
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(attrs['uid'])), is_active=True)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError, DjangoValidationError):
            user = None
        if user is None or not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({'token': ['This link is invalid or has expired.']})
        try:
            validate_password(attrs['new_password'], user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        attrs['user'] = user
        return attrs


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    current_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Password is incorrect.')
        return value

    def validate_new_email(self, value):
        value = User.objects.normalize_email(value.strip()).lower()
        if value == self.context['request'].user.email.lower():
            raise serializers.ValidationError('This is already your email.')
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value


class ConfirmEmailChangeSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        invalid = serializers.ValidationError(
            {'token': ['This link is invalid or has expired.']}
        )
        try:
            data = signing.loads(
                attrs['token'], salt=EMAIL_CHANGE_SALT, max_age=settings.EMAIL_CHANGE_TIMEOUT
            )
        except signing.BadSignature:
            raise invalid
        user = User.objects.filter(pk=data['uid'], is_active=True).first()
        # the old email must still be current: any other change invalidates the link
        if user is None or user.email != data['old']:
            raise invalid
        if User.objects.filter(email__iexact=data['new']).exclude(pk=user.pk).exists():
            raise serializers.ValidationError({'token': ['This email is already in use.']})
        attrs['user'] = user
        attrs['new_email'] = data['new']
        return attrs
