from django.db import models


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
