
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAnalystOrAdmin
from .detection import analyze_event
from .models import AuditLog, SecurityAlert, SecurityEvent
from .serializers import (
    AuditLogSerializer,
    SecurityAlertSerializer,
    SecurityEventSerializer,
)


class LoginRateLimitedTokenView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class SecurityEventListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAnalystOrAdmin]
    serializer_class = SecurityEventSerializer
    queryset = SecurityEvent.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.EVENT_CREATED,
            description=f"Security event #{event.pk} created.",
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        alerts = analyze_event(event)

        response_data = {
            "event": SecurityEventSerializer(event).data,
            "alerts": SecurityAlertSerializer(
                alerts, many=True
            ).data,
        }

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


class SecurityAlertListView(generics.ListAPIView):
    permission_classes = [IsAnalystOrAdmin]
    serializer_class = SecurityAlertSerializer
    queryset = SecurityAlert.objects.all()


class SecurityAlertStatusUpdateView(APIView):
    permission_classes = [IsAnalystOrAdmin]

    def patch(self, request, pk):
        try:
            alert = SecurityAlert.objects.get(pk=pk)
        except SecurityAlert.DoesNotExist:
            return Response(
                {"detail": "Alert not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")
        allowed_statuses = SecurityAlert.Status.values

        if new_status not in allowed_statuses:
            return Response(
                {"detail": "Invalid alert status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = alert.status

        if new_status != old_status:
            alert.status = new_status
            alert.save(update_fields=["status"])

            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.ALERT_STATUS_CHANGED,
                description=(
                    f"Alert #{alert.pk} status changed "
                    f"from {old_status} to {new_status}."
                ),
                ip_address=request.META.get("REMOTE_ADDR"),
            )

        return Response(SecurityAlertSerializer(alert).data)


class AuditLogListView(generics.ListAPIView):
    permission_classes = [IsAnalystOrAdmin]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related("user").all()
