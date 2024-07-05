from django.urls import path

from .views import GenerateOTPView, VerifyOTPView

urlpatterns = [
    path("generate_otp", GenerateOTPView.as_view(), name="generate_otp"),
    path("verify_otp", VerifyOTPView.as_view(), name="verify_otp"),
]
