from django.urls import path
from .views_v1 import (
    RegisterView,
    VerifyEmailView,
    UserLoginView,
    UserLogoutView,
    TokenRefreshView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)

# API v1 URL patterns 
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    ]