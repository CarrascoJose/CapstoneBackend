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
from users.models import CustomUser
from .serializers import PostBasketSerializer, UserBasketsSerializer, BasketResultsSerializer, GetAllBaskets, GetTotalThrift


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
            if len(serializer.data['basket'])>20:
                return Response({"error":"¡Porfavor, por el momento introduzca menos de 25 productos!"},status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            if user.is_authenticated:
                instance = serializer.save(user=request.user)
            else:
                instance = serializer.save()

            basket_id = instance.id

            task = compare.delay(basket_id)

            self.patch(basket_id, {"task_id":task.id})

            return Response({"basket_id":basket_id,"task_id":task.id},status=status.HTTP_201_CREATED)
        return Response({"error":"Something go wrong"},status=status.HTTP_400_BAD_REQUEST)
    
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


class GetExternalUserBaskets(
    RetrieveModelMixin,
    GenericAPIView
):

    queryset = CustomUser.objects.all()
    serializer_class = UserBasketsSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class GetBasketResultsView(
    RetrieveModelMixin,
    GenericAPIView
):
    queryset = Basket.objects.all()
    serializer_class = BasketResultsSerializer
    permission_classes = [CheckIfAnonymousUser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

       
class GetAllBasketsForPlotting(
    ListModelMixin,
    GenericAPIView
):
    queryset = Basket.objects.all()
    serializer_class = GetAllBaskets
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class GetBasketPricesSum(
    GenericAPIView
):
    serializer_class = GetTotalThrift
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(),many=True)
        data = serializer.data

        total_thrift = 0
        for el in data:

            ranking = el['ranking']
            if(len(ranking)>0):
                total_thrift += (ranking[len(ranking)-1][1]-ranking[0][1])

        return Response({"total_thrift":total_thrift},status=status.HTTP_200_OK)
    def get_queryset(self):
        return Basket.objects.all()
    