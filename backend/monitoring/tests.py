
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .detection import analyze_event
from .models import AuditLog, SecurityAlert, SecurityEvent


User = get_user_model()


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


class PermissionTests(APITestCase):
    def setUp(self):
        self.analyst = User.objects.create_user(
            username="analyst_test",
            password="TestPassword123!",
        )

        self.admin = User.objects.create_user(
            username="admin_test",
            password="TestPassword123!",
            is_staff=True,
        )

        self.events_url = "/api/events/"
        self.alerts_url = "/api/alerts/"

    def authenticate_as(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_unauthenticated_user_cannot_view_alerts(self):
        response = self.client.get(self.alerts_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_analyst_can_view_alerts(self):
        self.authenticate_as(self.analyst)

        response = self.client.get(self.alerts_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_analyst_cannot_create_event(self):
        self.authenticate_as(self.analyst)

        response = self.client.post(
            self.events_url,
            {
                "event_type": "LOGIN_FAILURE",
                "username": "test_user",
                "source_ip": "192.0.2.20",
                "message": "Invalid credentials",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_create_event(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.events_url,
            {
                "event_type": "LOGIN_FAILURE",
                "username": "test_user",
                "source_ip": "192.0.2.30",
                "message": "Invalid credentials",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_admin_can_view_events(self):
        self.authenticate_as(self.admin)

        response = self.client.get(self.events_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        
    def test_admin_cannot_submit_invalid_ip(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.events_url,
            {
                "event_type": "LOGIN_FAILURE",
                "username": "test_user",
                "source_ip": "not-an-ip",
                "message": "Invalid credentials",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_submit_blank_message(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.events_url,
            {
                "event_type": "LOGIN_FAILURE",
                "username": "test_user",
                "source_ip": "192.0.2.50",
                "message": "   ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_cannot_submit_blank_username(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.events_url,
            {
                "event_type": "LOGIN_FAILURE",
                "username": "   ",
                "source_ip": "192.0.2.51",
                "message": "Invalid credentials",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_analyst_cannot_update_alert_status(self):
        event = SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.LOGIN_FAILURE,
            username="test_user",
            source_ip="192.0.2.40",
            message="Invalid credentials",
        )

        alert = SecurityAlert.objects.create(
            title="Test alert",
            description="Permission test alert",
            severity=SecurityAlert.Severity.HIGH,
            source_ip="192.0.2.40",
            event=event,
        )

        self.authenticate_as(self.analyst)

        response = self.client.patch(
            f"/api/alerts/{alert.pk}/status/",
            {"status": SecurityAlert.Status.RESOLVED},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_update_alert_status(self):
        event = SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.LOGIN_FAILURE,
            username="test_user",
            source_ip="192.0.2.41",
            message="Invalid credentials",
        )

        alert = SecurityAlert.objects.create(
            title="Test alert",
            description="Permission test alert",
            severity=SecurityAlert.Severity.HIGH,
            source_ip="192.0.2.41",
            event=event,
        )

        self.authenticate_as(self.admin)

        response = self.client.patch(
            f"/api/alerts/{alert.pk}/status/",
            {"status": SecurityAlert.Status.RESOLVED},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        alert.refresh_from_db()
        self.assertEqual(
            alert.status,
            SecurityAlert.Status.RESOLVED,
        )
        
class AuditLogTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="audit_admin",
            password="TestPassword123!",
            is_staff=True,
        )
        self.analyst = User.objects.create_user(
            username="audit_analyst",
            password="TestPassword123!",
        )

        self.events_url = "/api/events/"
        self.audit_logs_url = "/api/audit-logs/"

        event = SecurityEvent.objects.create(
            event_type=SecurityEvent.EventType.LOGIN_FAILURE,
            username="test_user",
            source_ip="192.0.2.60",
            message="Invalid credentials",
        )

        self.alert = SecurityAlert.objects.create(
            title="Test audit alert",
            description="Testing audit history",
            severity=SecurityAlert.Severity.HIGH,
            source_ip="192.0.2.60",
            event=event,
        )

    def authenticate_as(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_event_creation_creates_audit_log(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.events_url,
            {
                "event_type": "LOGIN_SUCCESS",
                "username": "alice",
                "source_ip": "192.0.2.61",
                "message": "Successful login",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        audit = AuditLog.objects.get(
            action=AuditLog.Action.EVENT_CREATED,
            user=self.admin,
        )
        self.assertIn("created", audit.description.lower())

    def test_alert_status_change_creates_audit_log(self):
        self.authenticate_as(self.admin)

        response = self.client.patch(
            f"/api/alerts/{self.alert.pk}/status/",
            {"status": SecurityAlert.Status.RESOLVED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        audit = AuditLog.objects.get(
            action=AuditLog.Action.ALERT_STATUS_CHANGED,
            user=self.admin,
        )
        self.assertIn("OPEN", audit.description)
        self.assertIn("RESOLVED", audit.description)

    def test_same_status_does_not_create_duplicate_audit_log(self):
        self.authenticate_as(self.admin)

        response = self.client.patch(
            f"/api/alerts/{self.alert.pk}/status/",
            {"status": SecurityAlert.Status.OPEN},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            AuditLog.objects.filter(
                action=AuditLog.Action.ALERT_STATUS_CHANGED
            ).count(),
            0,
        )

    
def test_analyst_cannot_read_audit_logs(self):
    self.authenticate_as(self.analyst)

    response = self.client.get(self.audit_logs_url)

    self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
    )


    def test_unauthenticated_user_cannot_read_audit_logs(self):
        response = self.client.get(self.audit_logs_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_audit_logs_endpoint_does_not_allow_post(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.audit_logs_url,
            {
                "action": "EVENT_CREATED",
                "description": "Fake audit entry",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

def test_analyst_cannot_read_audit_logs(self):
    self.authenticate_as(self.analyst)

    response = self.client.get(self.audit_logs_url)

    self.assertEqual(
        response.status_code,
        status.HTTP_403_FORBIDDEN,
    )

def test_admin_can_read_audit_logs(self):
    self.authenticate_as(self.admin)

    response = self.client.get(self.audit_logs_url)

    self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
    )
