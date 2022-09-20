from rest_framework import serializers
from .models import Basket

class TestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = '__all__'
