
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_ipv46_address

from .models import SecurityAlert, SecurityEvent


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = [
            "id",
            "event_type",
            "username",
            "source_ip",
            "message",
            "timestamp",
            "raw_log",
        ]
        read_only_fields = ["id", "timestamp"]

    def validate_source_ip(self, value):
        try:
            validate_ipv46_address(value)
        except DjangoValidationError:
            raise serializers.ValidationError(
                "Enter a valid IPv4 or IPv6 address."
            )
        return value

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Username cannot be blank."
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                "Username cannot exceed 150 characters."
            )
        return value

    def validate_message(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Message cannot be blank."
            )
        return value


class SecurityAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityAlert
        fields = [
            "id",
            "title",
            "description",
            "severity",
            "source_ip",
            "event",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "title",
            "description",
            "severity",
            "source_ip",
            "event",
            "created_at",
        ]
