from rest_framework import serializers
from .models import Basket
from users.models import CustomUser

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


class BasketSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    class Meta:
        model = Basket
        fields = [
            'basket',
            'ranking',
            'created_at'
        ]


class UserBasketsSerializer(serializers.ModelSerializer):
    baskets = BasketSerializer(many=True)
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'baskets'
        ]



class BasketResultsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = [
            'basket',
            'ranking',
            'task_id'
        ]


class GetAllBaskets(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = [
            'basket',
            'search_duration'
        ]

class GetTotalThrift(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = [
            'ranking',
        ]
