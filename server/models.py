from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

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
        ("02", "Services"),
        ("03", "Professional"),
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
    INCOME = (
        ("31", "Below 1 Lakh"),
        ("32", "> 1 <=5 Lacs"),
        ("33", ">5 <=10 Lacs"),
        ("34", ">10 <= 25 Lacs"),
        ("35", "> 25 Lacs < = 1 Crore"),
        ("36", "Above 1 Crore"),
    )

    CITIZEN_TYPE = (
        ("RI", "Resident Indian"),
        ("NRI", "Non-Resident Indian"),
    )

    client_code = models.CharField(max_length=50)
    # most imp field
    pan = models.CharField(max_length=10, help_text="", blank=True)
    citizen_type = models.CharField(max_length=10, choices=CITIZEN_TYPE, blank=True)

    # fields required by bsestar client creation
    tax_status = models.CharField(max_length=2, default="01", blank=True)
    income_slab = models.CharField(max_length=10, choices=INCOME)
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


class MutualFundList(models.Model):
    unique_no = models.IntegerField()

    scheme_code = models.CharField(max_length=10)
    rta_scheme_code = models.CharField(max_length=10)
    amc_scheme_code = models.CharField(max_length=10)

    isin = models.CharField(max_length=12)
    amc_code = models.CharField(max_length=50)
    scheme_type = models.CharField(max_length=20)
    scheme_plan = models.CharField(max_length=20)
    scheme_name = models.CharField(max_length=200)

    purchase_allowed = models.CharField(max_length=1)
    purchase_transaction_mode = models.CharField(max_length=5)
    minimum_purchase_amount = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    additional_purchase_amount = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    maximum_purchase_amount = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    purchase_amount_multiplier = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    purchase_cutoff_time = models.TimeField(null=True)

    redemption_allowed = models.CharField(max_length=1)
    redemption_transaction_mode = models.CharField(max_length=5)
    minimum_redemption_qty = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    redemption_qty_multiplier = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    maximum_redemption_qty = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    redemption_amount_minimum = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    redemption_amount_maximum = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    redemption_amount_multiple = models.DecimalField(
        max_digits=25, decimal_places=10, null=True
    )
    redemption_cutoff_time = models.TimeField(null=True)

    rta_agent_code = models.CharField(max_length=10)
    amc_active_flag = models.IntegerField(null=True)
    dividend_reinvestment_flag = models.CharField(max_length=1)

    sip_flag = models.CharField(max_length=1)
    stp_flag = models.CharField(max_length=1)
    swp_flag = models.CharField(max_length=1)
    switch_flag = models.CharField(max_length=1)

    settlement_type = models.CharField(max_length=5)
    amc_ind = models.CharField(max_length=10, blank=True)
    face_value = models.DecimalField(max_digits=25, decimal_places=10, null=True)

    start_date = models.DateField()
    end_date = models.DateField()
    exit_load_flag = models.CharField(max_length=1)
    exit_load = models.IntegerField(null=True)
    lock_in_period_flag = models.CharField(max_length=1)
    lock_in_period = models.IntegerField(null=True)
    channel_partner_code = models.CharField(max_length=10)
    reopening_date = models.DateField(null=True, blank=True)


# Internal transaction table

class CustomTransactionManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)

class Transaction(models.Model):
    """
    Saves each transaction's details for internal record
    Used to create records of TransactionBSE and TransactionXsipBSE
            that are sent to BSEStar's API endpoints
    """

    # status of the transaction. most imp states are 1, 2 and 6 for bse
    STATUS = (
        ("0", "Requested internally"),  # bse order not placed yet
        ("1", "Cancelled/Failed- refer to status_comment for reason"),
        ("2", "Order successfully placed at BSE"),
        ("4", "Redirected after payment"),
        ("5", "Payment provisionally made"),
        ("6", "Order sucessfully completed at BSE"),
        ("7", "Reversed"),  # when investment has been redeemed
        ("8", "Concluded"),  # valid for SIP only when SIP completed/stopped
    )
    TRANSACTIONTYPE = (
        ("P", "Purchase"),
        ("R", "Redemption"),
        ("A", "Additional Purchase"),
    )
    TRANCATIONCODE = (("NEW", "NEW"), ("CXL", "CANCELLATION"))
    ORDERTYPE = (
        ("1", "Lumpsum"),
        ("2", "SIP"),
    )

    objects = CustomTransactionManager()
    all_objects = models.Manager()

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="transactions",
        related_query_name="transaction",
    )
    scheme_plan = models.ForeignKey(
        MutualFundList,
        on_delete=models.PROTECT,
        related_name="transactions",
        related_query_name="transaction",
    )

    transaction_code = models.CharField(
        max_length=15, blank=False, choices=TRANCATIONCODE, default="NEW"
    )
    transaction_type = models.CharField(
        max_length=1, blank=False, choices=TRANSACTIONTYPE, default="P"
    )  ##purchase redemption etc
    order_type = models.CharField(
        max_length=1, blank=False, choices=ORDERTYPE, default="1"
    )  ##lumpsum or sip

    # track status of transaction and comments if any from bse or rta
    status = models.CharField(max_length=1, choices=STATUS, default="0")
    status_comment = models.CharField(max_length=1000, blank=True)

    amount = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1000000)],
        blank=True,
        null=True,
    )

    # for redeem transactions
    all_redeem = models.BooleanField(
        blank=True, null=True
    )  ## Null means not redeem transaction, True means redeem all, False means redeem 'amount'

    # datetimes of importance
    ## datetime when order was placed on bsestar
    datetime_at_mf = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True
    )

    # datetime of purchase of units on mf
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # set these fields after the transaction is successfully PLACED
    ## this is the trans_no of the order on bsestar
    ## that has successfully placed this transaction
    bse_trans_no = models.CharField(max_length=20)
    order_id = models.CharField(max_length=20)

    # set these fields after the transaction is successfully COMPLETED
    folio_number = models.CharField(max_length=25, blank=True)

    # Returns - set these fields daily after transaction is COMPLETED
    return_till_date = models.FloatField(
        blank=True, null=True
    )  # annualised compounded annually. make it absolute return
    return_date = models.DateField(
        auto_now=False, auto_now_add=False, blank=True, null=True
    )  # date as of return calculated
    return_grade = models.CharField(max_length=200)

    is_deleted = models.BooleanField(default=False)


class KFintechPortfolio(models.Model):
    sno = models.CharField(max_length=20)
    fmcode = models.CharField(max_length=20)
    td_fund = models.CharField(max_length=4)
    td_acno = models.CharField(max_length=15)
    schpln = models.CharField(max_length=4)
    divopt = models.CharField(max_length=1)
    funddesc = models.CharField(max_length=200)
    td_purred = models.CharField(max_length=1)
    td_trno = models.CharField(max_length=10)
    smcode = models.CharField(max_length=10)
    chqno = models.CharField(max_length=20)
    invname = models.CharField(max_length=120)
    jtname1 = models.CharField(max_length=80)
    jtname2 = models.CharField(max_length=80)
    add1 = models.CharField(max_length=80)
    add2 = models.CharField(max_length=80)
    add3 = models.CharField(max_length=80)
    city = models.CharField(max_length=60)
    pin = models.CharField(max_length=10)
    state = models.CharField(max_length=60)
    country = models.CharField(max_length=40)
    dob = models.DateField(null=True, blank=True)
    rphone = models.CharField(max_length=40)
    rphone1 = models.CharField(max_length=1)
    rphone2 = models.CharField(max_length=1)
    mobile = models.CharField(max_length=40)
    ophone = models.CharField(max_length=40)
    ophone1 = models.CharField(max_length=1)
    ophone2 = models.CharField(max_length=1)
    fax = models.CharField(max_length=40)
    faxoff = models.CharField(max_length=1)
    status = models.CharField(max_length=2)
    occpn = models.CharField(max_length=10)
    email = models.EmailField(max_length=150)
    bnkacno = models.CharField(max_length=50)
    bname = models.CharField(max_length=80)
    bnkactype = models.CharField(max_length=40)
    branch = models.CharField(max_length=5)
    badd1 = models.CharField(max_length=80)
    badd2 = models.CharField(max_length=80)
    badd3 = models.CharField(max_length=80)
    bcity = models.CharField(max_length=60)
    bphone = models.CharField(max_length=40)
    pangno = models.CharField(max_length=50)
    trnmode = models.CharField(max_length=1)
    trnstat = models.CharField(max_length=1)
    td_branch = models.CharField(max_length=80)
    isctrno = models.CharField(max_length=10)
    td_trdt = models.DateField(null=True, blank=True)
    td_prdt = models.DateField(null=True, blank=True)
    td_pop = models.CharField(max_length=30)
    loadper = models.DecimalField(max_digits=18, decimal_places=4)
    td_units = models.DecimalField(max_digits=20, decimal_places=3)
    td_amt = models.DecimalField(max_digits=20, decimal_places=2)
    load1 = models.DecimalField(max_digits=20, decimal_places=2)
    td_agent = models.CharField(max_length=50)
    td_broker = models.CharField(max_length=50)
    brokper = models.CharField(max_length=9)
    brokcomm = models.DecimalField(max_digits=15, decimal_places=2)
    invid = models.CharField(max_length=1)
    crdate = models.DateField(null=True, blank=True)
    crtime = models.CharField(max_length=6)
    trnsub = models.CharField(max_length=1)
    td_appno = models.CharField(max_length=20)
    unqno = models.CharField(max_length=50)
    trdesc = models.CharField(max_length=40)
    td_trtype = models.CharField(max_length=10)
    purdate = models.DateField(null=True, blank=True)
    puramt = models.DecimalField(max_digits=20, decimal_places=2)
    purunits = models.DecimalField(max_digits=20, decimal_places=3)
    trflag = models.CharField(max_length=2)
    sfunddt = models.DateField(null=True, blank=True)
    chqdate = models.DateField(null=True, blank=True)
    chqbank = models.CharField(max_length=80)
    nctremarks = models.CharField(max_length=200)
    td_scheme = models.CharField(max_length=2)
    td_plan = models.CharField(max_length=2)
    td_nav = models.CharField(max_length=30)
    annper = models.CharField(max_length=10)
    annamt = models.CharField(max_length=10)
    td_ptrno = models.CharField(max_length=10)
    td_pbranch = models.CharField(max_length=5)
    oldacno = models.CharField(max_length=10)
    ihno = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.invname} - {self.funddesc}'
    

class BSERequest(models.Model):
    payload = models.JSONField()
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SIPScheme(models.Model):
    amc_code = models.CharField(max_length=100, default="")
    amc_name = models.CharField(max_length=255, default="")
    scheme_code = models.CharField(max_length=100, default="")
    scheme_name = models.CharField(max_length=255, default="")
    sip_transaction_mode = models.CharField(max_length=50, default="")
    sip_frequency = models.CharField(max_length=50, default="")
    sip_dates = models.CharField(max_length=255, default="")
    sip_minimum_gap = models.CharField(max_length=100, default="")
    sip_maximum_gap = models.CharField(max_length=100, default="")
    sip_installment_gap = models.CharField(max_length=100, default="")
    sip_status = models.CharField(max_length=50, default="")
    sip_minimum_installment_amount = models.CharField(max_length=100, default="")
    sip_maximum_installment_amount = models.CharField(max_length=100, default="", null=True, blank=True)
    sip_multiplier_amount = models.CharField(max_length=100, default="")
    sip_minimum_installment_numbers = models.CharField(max_length=100, default="")
    sip_maximum_installment_numbers = models.CharField(max_length=100, default="", null=True, blank=True)
    scheme_isin = models.CharField(max_length=50, default="")
    scheme_type = models.CharField(max_length=50, default="")
    pause_flag = models.CharField(max_length=1, default="")
    pause_minimum_installments = models.CharField(max_length=100, default="", null=True, blank=True)
    pause_maximum_installments = models.CharField(max_length=100, default="", null=True, blank=True)
    pause_modification_count = models.CharField(max_length=100, default="", null=True, blank=True)
    filler_1 = models.CharField(max_length=255, default="", null=True, blank=True)
    filler_2 = models.CharField(max_length=255, default="", null=True, blank=True)
    filler_3 = models.CharField(max_length=255, default="", null=True, blank=True)
    filler_4 = models.CharField(max_length=255, default="", null=True, blank=True)
    filler_5 = models.CharField(max_length=255, default="", null=True, blank=True)

    def __str__(self):
        return f'{self.scheme_name} ({self.amc_code})'