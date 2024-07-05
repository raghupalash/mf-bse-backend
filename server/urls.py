from django.urls import path

from .views import GenerateOTPView

urlpatterns = [path("generate_otp", GenerateOTPView.as_view(), name="generate_otp")]
