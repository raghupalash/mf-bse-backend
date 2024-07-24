from rest_framework import serializers
from .models import MutualFundList

class MutualFundListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MutualFundList
        fields = '__all__'