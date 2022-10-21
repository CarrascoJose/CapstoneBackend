from rest_framework import serializers
from .models import Basket

class PostBasketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = ['basket','task_id']

    def save(self, **kwargs):
        if self.instance is not None:
            self.instance = self.update(self.instance, self.validated_data)
            return self.instance
        basket = Basket.objects.create(**self.validated_data)
        return basket


class ListBasketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = '__all__'

class BasketResultsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = [
            'basket',
            'ranking'
        ]
