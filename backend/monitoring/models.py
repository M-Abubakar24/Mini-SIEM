
from django.db import models


class SecurityEvent(models.Model):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "LOGIN_SUCCESS", "Login Success"
        LOGIN_FAILURE = "LOGIN_FAILURE", "Login Failure"
        SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY", "Suspicious Activity"

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
    )
    username = models.CharField(max_length=150, blank=True, default="")
    source_ip = models.GenericIPAddressField()
    message = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    raw_log = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.event_type} from {self.source_ip}"


class SecurityAlert(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        INVESTIGATING = "INVESTIGATING", "Investigating"
        RESOLVED = "RESOLVED", "Resolved"

    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.LOW,
    )
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    event = models.ForeignKey(
        SecurityEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.severity}: {self.title}"
class AuditLog(models.Model):
    class Action(models.TextChoices):
        EVENT_CREATED = "EVENT_CREATED", "Event Created"
        ALERT_STATUS_CHANGED = (
            "ALERT_STATUS_CHANGED",
            "Alert Status Changed",
        )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(
        max_length=30,
        choices=Action.choices,
    )
    description = models.TextField()
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.created_at}"