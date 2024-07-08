from django.urls import path

from .views import GenerateOTPView, VerifyOTPView, VerifyTokenView, ProfileView

urlpatterns = [
    path("generate_otp_for_username", GenerateOTPView.as_view(), name="generate_otp"),
    path("verify_otp_for_username", VerifyOTPView.as_view(), name="verify_otp"),
    path("verify_token", VerifyTokenView.as_view(), name="verify_token"),
    path("profile", ProfileView.as_view(), name="profile"),
]
