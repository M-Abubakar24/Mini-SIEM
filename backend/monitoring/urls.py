
from django.urls import path

from .views import (
    SecurityAlertListView,
    SecurityAlertStatusUpdateView,
    SecurityEventListCreateView,
)

urlpatterns = [
    path("events/", SecurityEventListCreateView.as_view(), name="event-list"),
    path("alerts/", SecurityAlertListView.as_view(), name="alert-list"),
    path(
        "alerts/<int:pk>/status/",
        SecurityAlertStatusUpdateView.as_view(),
        name="alert-status-update",
    ),
]
