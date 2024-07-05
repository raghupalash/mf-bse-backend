from django.urls import path

from .views import GenerateOTPView, VerifyOTPView

urlpatterns = [
    path("generate_otp_for_username", GenerateOTPView.as_view(), name="generate_otp_for_username"),
    path("verify_otp_for_username", VerifyOTPView.as_view(), name="verify_otp"),
]
