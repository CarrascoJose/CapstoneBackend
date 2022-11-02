from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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

        if serializer.is_valid():
            instance = serializer.save(user=request.user)
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




class GetBasketsView(
    RetrieveModelMixin,
    ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Basket.objects.all()
    serializer_class = ListBasketSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        print(self.request.user)
        return self.request.user.basket_set.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BasketResultsSerializer
        return super().get_serializer_class()
       
