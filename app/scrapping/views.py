from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework import viewsets

from .tasks import compare
from .models import Basket
from .serializers import PostBasketSerializer, ListBasketSerializer, BasketResultsSerializer


class CreateBasketTaskView(
    GenericAPIView,
    CreateModelMixin,
    UpdateModelMixin
):
    queryset = Basket.objects.all()
    serializer_class = PostBasketSerializer

    def post(self, request,*args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if serializer.is_valid():
            basket_id = instance.id

            task = compare.delay(basket_id)

            self.patch(basket_id, {"task_id":task.id})

        return Response({"tasks_id":task.id},status=status.HTTP_201_CREATED)
    
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
    viewsets.GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Basket.objects.all()
    serializer_class = ListBasketSerializer

    def get(self, request,*args, **kwargs):
        pk = kwargs.get("pk")
        if pk is not None:
            return self.retrieve(self, request, *args, **kwargs)
        return self.list(self, request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return ListBasketSerializer
        return BasketResultsSerializer
       
