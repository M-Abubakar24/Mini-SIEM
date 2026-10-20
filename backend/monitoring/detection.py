
from datetime import timedelta

from django.utils import timezone

from .models import SecurityAlert, SecurityEvent


# Detection thresholds for this educational project.
BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 5


def analyze_event(event):
    """
    Analyze a saved security event and create an alert
    when a detection rule matches.
    """
    if event.event_type != SecurityEvent.EventType.LOGIN_FAILURE:
        return []

    window_start = timezone.now() - timedelta(
        minutes=BRUTE_FORCE_WINDOW_MINUTES
    )

    failed_attempts = SecurityEvent.objects.filter(
        event_type=SecurityEvent.EventType.LOGIN_FAILURE,
        source_ip=event.source_ip,
        timestamp__gte=window_start,
    ).count()

    if failed_attempts < BRUTE_FORCE_THRESHOLD:
        return []

    # Avoid creating another active brute-force alert
    # for the same source IP within the detection window.
    existing_alert = SecurityAlert.objects.filter(
        source_ip=event.source_ip,
        title="Possible brute-force login activity",
        status__in=[
            SecurityAlert.Status.OPEN,
            SecurityAlert.Status.INVESTIGATING,
        ],
        created_at__gte=window_start,
    ).exists()

    if existing_alert:
        return []

    alert = SecurityAlert.objects.create(
        title="Possible brute-force login activity",
        description=(
            f"{failed_attempts} failed login attempts from "
            f"{event.source_ip} were observed within approximately "
            f"{BRUTE_FORCE_WINDOW_MINUTES} minutes."
        ),
        severity=SecurityAlert.Severity.HIGH,
        source_ip=event.source_ip,
        event=event,
    )

    return [alert]
