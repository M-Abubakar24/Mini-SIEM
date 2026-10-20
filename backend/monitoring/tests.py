
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .detection import analyze_event
from .models import SecurityAlert, SecurityEvent


class BruteForceDetectionTests(TestCase):
    def create_failure(self, ip="192.0.2.10"):
        return SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.LOGIN_FAILURE,
            username="test_user",
            source_ip=ip,
            message="Invalid credentials",
        )

    def test_alert_created_after_five_failed_logins(self):
        for _ in range(5):
            event = self.create_failure()

        alerts = analyze_event(event)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(
            alerts[0].severity,
            SecurityAlert.Severity.HIGH,
        )

    def test_no_alert_below_threshold(self):
        for _ in range(4):
            event = self.create_failure()

        alerts = analyze_event(event)

        self.assertEqual(alerts, [])

    def test_active_alert_is_not_duplicated(self):
        for _ in range(5):
            event = self.create_failure()

        analyze_event(event)
        alerts = analyze_event(event)

        self.assertEqual(alerts, [])
        self.assertEqual(SecurityAlert.objects.count(), 1)

    def test_old_failures_do_not_trigger_alert(self):
        for _ in range(5):
            event = self.create_failure()

        SecurityEvent.objects.filter(
            source_ip="192.0.2.10"
        ).update(
            timestamp=timezone.now() - timedelta(minutes=10)
        )

        alerts = analyze_event(event)

        self.assertEqual(alerts, [])
