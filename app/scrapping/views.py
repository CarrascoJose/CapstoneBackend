from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import CheckIfAnonymousUser

from .tasks import compare
from .models import Basket
from .serializers import PostBasketSerializer, ListBasketSerializer, BasketResultsSerializer


class CreateBasketTaskView(
    CreateModelMixin,
    UpdateModelMixin,
    GenericAPIView
):
    queryset = Basket.objects.all()
    serializer_class = PostBasketSerializer

    def post(self, request,*args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            user = request.user
            if user.is_authenticated:
                instance = serializer.save(user=request.user)
            else:
                instance = serializer.save()

            basket_id = instance.id

            task = compare.delay(basket_id)

            self.patch(basket_id, {"task_id":task.id})

            return Response({"basket_id":basket_id,"task_id":task.id},status=status.HTTP_201_CREATED)
        return Response({"error":"Something go wrong"},status=status.HTTP_400)
    
    def patch(self, pk, taksid):
        instance = self.get_object(pk)
        serializer = PostBasketSerializer(
            instance, data=taksid, partial=True
        )

        if serializer.is_valid():
            serializer.save()

    def get_object(self,pk):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        obj = Basket.objects.filter(id=pk).first()
        return obj

class GetUserBasketsView(
    ListModelMixin,
    GenericAPIView
):
    queryset = Basket.objects.all()
    serializer_class = ListBasketSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.basket_set.all()


class GetBasketResultsView(
    RetrieveModelMixin,
    GenericAPIView
):
    queryset = Basket.objects.all()
    serializer_class = BasketResultsSerializer
    permission_classes = [CheckIfAnonymousUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

       
