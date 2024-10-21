from rest_framework import serializers
from .models import MutualFundList, Transaction


class MutualFundListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MutualFundList
        fields = "__all__"

class TransactionSerailizer(serializers.ModelSerializer):
    scheme_name = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        exclude = ["user", "created_at", "updated_at", "bse_trans_no", "is_deleted"]

    def get_scheme_name(self, obj):
        return obj.scheme_plan.scheme_name