
from django.urls import path

from .views import (
    SecurityAlertListView,
    SecurityAlertStatusUpdateView,
    SecurityEventListCreateView,
)
from .views import AuditLogListView

urlpatterns = [
    path("events/", SecurityEventListCreateView.as_view(), name="event-list"),
    path("alerts/", SecurityAlertListView.as_view(), name="alert-list"),
    path("audit-logs/", AuditLogListView.as_view(), name="audit-logs"),
    path(
        "alerts/<int:pk>/status/",
        SecurityAlertStatusUpdateView.as_view(),
        name="alert-status-update",
    ),
]
