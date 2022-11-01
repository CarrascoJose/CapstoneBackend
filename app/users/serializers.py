from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings

class RegisterSerializer(ModelSerializer):

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['email','password','username','first_name','last_name']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username

        return token



