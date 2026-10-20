
from rest_framework import serializers

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
