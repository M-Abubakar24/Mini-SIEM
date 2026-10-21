from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from monitoring.views import LoginRateLimitedTokenView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("monitoring.urls")),
    path(
        "api/token/",
        LoginRateLimitedTokenView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]