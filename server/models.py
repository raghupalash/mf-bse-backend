from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models import Q

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
    last_name = models.CharField(max_length=200, null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    photo_url = models.URLField(max_length=200, null=True, blank=True)

class UserLoginToken(Token):
    # relation to user is a ForeignKey, so each user can have more than one token
    user = models.ForeignKey(User, related_name='auth_tokens', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    is_connected = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_logged_out = models.BooleanField(default=False)
    class Meta:
        db_table = 'user_login_token'

    @staticmethod
    def get_valid_messaging_tokens():
        return UserLoginToken.objects\
            .filter(is_logged_out=False, is_deleted=False, is_connected=True)\
            .exclude(fcm_token__isnull=1)\
            .order_by('-last_login')

    @classmethod
    def get_valid_token_for_user(cls, username, device=None):
        filter_q = Q(user__username=username) & Q(is_logged_out=False)
        if device:
            filter_q &= Q(device=device)
        instance = UserLoginToken.objects.filter(filter_q).first()
        if instance:
            return instance.key
        return None
