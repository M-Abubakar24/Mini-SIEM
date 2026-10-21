
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAnalystOrAdmin
from .detection import analyze_event
from .models import SecurityAlert, SecurityEvent
from .serializers import SecurityAlertSerializer, SecurityEventSerializer


class SecurityEventListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAnalystOrAdmin]
    serializer_class = SecurityEventSerializer
    queryset = SecurityEvent.objects.all()
    # Demo only. We'll add authentication and permissions next.

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        alerts = analyze_event(event)

        response_data = {
            "event": SecurityEventSerializer(event).data,
            "alerts": SecurityAlertSerializer(alerts, many=True).data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


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

        alert.status = new_status
        alert.save(update_fields=["status"])

        return Response(SecurityAlertSerializer(alert).data)
