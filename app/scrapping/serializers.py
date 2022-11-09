from rest_framework import serializers
from .models import Basket

class PostBasketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = ['user','basket','task_id']
        extra_kwargs = {"user": {"required": False, "allow_null": True}}

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data)
            return self.instance
        else:
            self.instance = self.create(validated_data)

        return self.instance


class ListBasketSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    class Meta:
        model = Basket
        fields = [
            'id',
            'basket',
            'ranking',
            'created_at'
        ]

class BasketResultsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = [
            'basket',
            'ranking',
            'task_id'
        ]
