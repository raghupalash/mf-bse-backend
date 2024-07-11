from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

from rest_framework.authtoken.models import Token


class UserOTP(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)
    email = models.EmailField(max_length=100, unique=True)
    otp_code = models.CharField(max_length=10)
    failed_attempts = models.IntegerField(default=0)
    lockout_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_otp"

    def __str__(self):
        return self.email


class User(AbstractUser):
    firebase_user_id = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(max_length=256)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    middle_name = models.CharField(max_length=200, default="", blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    photo_url = models.URLField(max_length=200, null=True, blank=True)


class UserLoginToken(Token):
    # relation to user is a ForeignKey, so each user can have more than one token
    user = models.ForeignKey(User, related_name="auth_tokens", on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    is_connected = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_logged_out = models.BooleanField(default=False)

    class Meta:
        db_table = "user_login_token"

    @staticmethod
    def get_valid_messaging_tokens():
        return (
            UserLoginToken.objects.filter(
                is_logged_out=False, is_deleted=False, is_connected=True
            )
            .exclude(fcm_token__isnull=1)
            .order_by("-last_login")
        )

    @classmethod
    def get_valid_token_for_user(cls, username, device=None):
        filter_q = Q(user__username=username) & Q(is_logged_out=False)
        if device:
            filter_q &= Q(device=device)
        instance = UserLoginToken.objects.filter(filter_q).first()
        if instance:
            return instance.key
        return None


class KycDetail(models.Model):
    """
    Stores all kyc details of user
    Written as per BSEStar API documentation for user creation endpoint
    """

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, related_name="kycdetail"
    )

    OCCUPATION = (
        ("01", "Business"),
        ("02", "Services"),
    )
    GENDER = (
        ("M", "Male"),
        ("F", "Female"),
    )
    STATE = (
        ("AN", "Andaman & Nicobar"),
        ("AR", "Arunachal Pradesh"),
        ("AP", "Andhra Pradesh"),
        ("AS", "Assam"),
        ("BH", "Bihar"),
        ("CH", "Chandigarh"),
        ("CG", "Chhattisgarh"),
        ("DL", "Delhi"),
        ("GO", "GOA"),
        ("GU", "Gujarat"),
        ("HA", "Haryana"),
        ("HP", "Himachal Pradesh"),
        ("JM", "Jammu & Kashmir"),
        ("JK", "Jharkhand"),
        ("KA", "Karnataka"),
        ("KE", "Kerala"),
        ("MP", "Madhya Pradesh"),
        ("MA", "Maharashtra"),
        ("MN", "Manipur"),
        ("ME", "Meghalaya"),
        ("MI", "Mizoram"),
        ("NA", "Nagaland"),
        ("ND", "New Delhi"),
        ("OR", "Orissa"),
        ("PO", "Pondicherry"),
        ("PU", "Punjab"),
        ("RA", "Rajasthan"),
        ("SI", "Sikkim"),
        ("TG", "Telengana"),
        ("TN", "Tamil Nadu"),
        ("TR", "Tripura"),
        ("UP", "Uttar Pradesh"),
        ("UC", "Uttaranchal"),
        ("WB", "West Bengal"),
        ("DN", "Dadra and Nagar Haveli"),
        ("DD", "Daman and Diu"),
    )

    # most imp field
    pan = models.CharField(max_length=10, help_text="", blank=True)

    # fields required by bsestar client creation
    tax_status = models.CharField(max_length=2, default="01", blank=True)
    occ_code = models.CharField(
        max_length=2, default="02", choices=OCCUPATION, blank=True
    )
    dob = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER, blank=True)
    address = models.CharField(
        max_length=120, help_text="sample: 10, Mg Road, New Delhi - 11001", blank=True
    )
    city = models.CharField(max_length=35, blank=True)
    state = models.CharField(max_length=2, choices=STATE, blank=True)
    pincode = models.CharField(max_length=6, help_text="sample: 110049", blank=True)
    country = models.CharField(max_length=2, blank=True)
    phone = models.CharField(max_length=10, help_text="sample: 9999999999", blank=True)
    paperless_flag = models.CharField(max_length=1)

    nominee_name = models.CharField(max_length=40, blank=True, null=True)
    nominee_relation = models.CharField(max_length=13, blank=True, null=True)
    kyc_type = models.CharField(max_length=1)
    ckyc_number = models.CharField(max_length=14, blank=True, null=True)

    # Addl KYC and fatca details
    ## there are a bunch of fields that can be filled based on above fields or hard-coded which
    ## have not been included here like country of citizenship, politically exposed etc

    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now_add=True)


class BankDetail(models.Model):
    """
    Stores bank details of user
    Written as per BSEStar API documentation for user creation endpoint
    """

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bankdetail",
        related_query_name="bankdetail",
    )

    bank = models.CharField(max_length=100, blank=False)
    ifsc_code = models.CharField(max_length=11, blank=False)

    ACCOUNTTYPE = (
        ("SB", "Savings"),
        ("CB", "Current"),
        ("NE", "NRE"),
        ("NO", "NRO"),
    )

    account_number = models.CharField(max_length=20, blank=False)
    account_type = models.CharField(
        max_length=2, choices=ACCOUNTTYPE, default="SB", blank=False
    )

    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now_add=True)
