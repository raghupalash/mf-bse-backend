from django.core.validators import ValidationError, validate_email
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response

from .helpers import random_num_with_N_digits
from .models import UserOTP


class GenerateOTPView(APIView):
    def post(self, request):
        email = request.data.get("email", None)
        if not email:
            return Response("Email is required!", 400)

        # validate email
        try:
            validate_email(email)
        except ValidationError:
            return Response("Enter valid email!", 400)

        otp = random_num_with_N_digits(6)
        userotp_instance, _ = UserOTP.objects.get_or_create(email=email)
        userotp_instance.otp_code = otp
        userotp_instance.save()
        data = {}
        data["message"] = "OTP sent to email"

        mail_message = (
            "Welcome to our demo Mutual Funds Application powerd by BSE Star! Here's your OTP: "
            f"{otp}"
        )
        send_mail(
            "OTP Verification",
            mail_message,
            "sbnritech@sbnri.com",
            [email],
            fail_silently=False,
        )

        return Response({"data": "OTP sent to mail!"})
