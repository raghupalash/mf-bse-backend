from django import forms

from .models import TransactionBSE
from django.core.validators import RegexValidator


# Used in validating fields when preparing new order entry
class NewOrderForm(forms.ModelForm):
    class Meta:
        model = TransactionBSE
        exclude = "dp_txn", "kyc_status", "euin", "euin_val", "dpc"


# Used in validating fields when preparing cancellation order entry
class CxlOrderForm(forms.ModelForm):
    order_id = forms.CharField(validators=[RegexValidator(r"^[0-9]*$")], max_length=8)

    class Meta:
        model = TransactionBSE
        fields = (
            "trans_code",
            "trans_no",
            "order_id",
            "user_id",
            "password",
            "pass_key",
            "internal_transaction",
            "client_code",
            "member_id",
        )
