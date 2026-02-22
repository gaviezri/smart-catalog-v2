"""URL routing for the users bounded context."""
from __future__ import annotations

from django.urls import path

from users.application.views import LoginView, LogoutView

urlpatterns = [
    path("login", LoginView.as_view(), name="auth-login"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
]
