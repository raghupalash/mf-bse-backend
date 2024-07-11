from django.core.validators import ValidationError, validate_email
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .helpers import *
from .models import UserOTP, User, UserLoginToken
from .firebase import generate_firebase_link_for_auth, get_credentails_from_id_token


class GenerateOTPView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow access to all

    def post(self, request):
        email = request.data.get("email", None)
        if not email:
            return Response(dict(status=0, data="Email is required!"), 400)

        # validate email
        try:
            validate_email(email)
        except ValidationError:
            return Response(dict(status=0, data="Enter valid email!"), 400)

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

        return Response({"status": 1, "data": "OTP sent to mail!"})


class VerifyOTPView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow access to all

    def post(self, request):
        email = request.data.get("email", None)
        otp = request.data.get("otp", None)
        if not email:
            return Response(dict(status=0, data="Email is required!"), 400)
        if not otp:
            return Response(dict(staut=0, data="OTP is required!"), 400)

        # validate email
        try:
            validate_email(email)
        except ValidationError:
            return Response(dict(status=0, data="Enter valid email!"), 400)

        user_otp = UserOTP.objects.filter(email=email).first()
        if not user_otp:
            return Response(dict(status=0, data="OTP not generated"), 400)
        elif user_otp.otp_code != otp:
            return Response(
                dict(status=0, data="OTP is incorrect. Please try again"), 400
            )
        else:
            link = generate_firebase_link_for_auth(email=email)

        return Response(dict(status=1, data=link))


class VerifyTokenView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow access to all

    def post(self, request):
        token = request.data.get("token", None)
        if not token:
            return Response(dict(status=0, data="Email is required!"), 400)
        token_credentials = get_credentails_from_id_token(token)

        if not token_credentials:
            raise Response(dict(status=0, data="Token expired!"), 400)

        firebase_user_id = token_credentials["firebase_user_id"]
        photo_url = token_credentials["photo_url"]
        email = token_credentials["email"]
        first_name = token_credentials["first_name"]
        last_name = token_credentials["last_name"]

        user_instance, created = User.objects.get_or_create(
            firebase_user_id=firebase_user_id
        )

        if created:
            user_instance.username = create_username()
            user_instance.email = email
            user_instance.first_name = first_name
            user_instance.last_name = last_name
            user_instance.photo_url = photo_url
            user_instance.is_email_verified = token_credentials["email_verified"]

        user_instance.save()

        token_instance = UserLoginToken.objects.create(
            user=user_instance,
        )

        user_instance.last_login = token_instance.created
        user_instance.save()

        user_data = {
            "firebase_user_id": user_instance.firebase_user_id,
            "username": user_instance.username,
            "email": user_instance.email,
            "first_name": user_instance.first_name,
            "last_name": user_instance.last_name,
            "photo_url": user_instance.photo_url,
            "token": token_instance.key,
        }
        return Response(dict(status=1, data=user_data))


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_instance = request.user
        user_data = {
            "firebase_user_id": user_instance.firebase_user_id,
            "email": user_instance.email,
            "first_name": user_instance.first_name,
            "last_name": user_instance.last_name,
            "photo_url": user_instance.photo_url,
        }

        return Response(dict(status=1, data=user_data))


class KYCUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        save_kyc_data_to_db(request.user, request.data)

        payload = prepare_payload_for_bse_call(request.user)

        # create user on bse
        response = register_client_on_bse(payload)
        if response.json().get("Status") == "1":
            return Response(dict(status=0, data=response.json()), 400)
        print(response.json())
        response = authenticate_nominee(request.user)
        if response.json().get("StatusCode") == "101":
            return Response(dict(status=0, data=response.json()), 400)
        print(response.json())

        message = (
            "Your account has been successfully registered with BSE! "
            "You'll soon recieve an authentication email from BSE!"
        )
        return Response(dict(status=1, data=message))
