from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import MyTokenObtainPairSerializer, RegisterSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterUserView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            if new_user:
                return Response(status=status.HTTP_201_CREATED)
        return Response({"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)