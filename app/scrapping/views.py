from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework import viewsets

from .tasks import compare
from .models import Basket
from .serializers import PostBasketSerializer, ListBasketSerializer, BasketResultsSerializer

# @api_view(['GET','POST'])
# def scraping_data(request):

#     if request.method == 'POST':
#         product_json = request.data
#         basket = Basket.objects.create(
#             basket = product_json
#         )
#         compare.delay(basket.id)
#         return Response({"basket_id":basket.id},status=status.HTTP_200_OK)

#     if request.method == 'GET':
#         baskets = Basket.objects.all()
#         serializer = PostBasketSerializer(baskets, many=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)

class CreateBasketTaskView(GenericAPIView, CreateModelMixin):
    queryset = Basket.objects.all()
    serializer_class = PostBasketSerializer

    def post(self, request,*args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if serializer.is_valid():
            data = serializer.data
            basket_id = instance.id
            task = compare.delay(basket_id)

        return Response({"tasks_id":task.id},status=status.HTTP_201_CREATED)


class GetBasketsView(viewsets.GenericViewSet, ListModelMixin, RetrieveModelMixin):
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
       


# @api_view(['GET'])
# def basket_view(request, pk):
#     try:
#         basket = Basket.objects.get(pk=pk)
#     except basket.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == "GET":
#         serializer = BasketResultsSerializer(basket)
#         return Response(serializer.data)
