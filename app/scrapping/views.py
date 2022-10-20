from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .tasks import compare
from .models import Basket
from .serializers import TestSerializer, BasketResultsSerializer

@api_view(['GET','POST'])
def scraping_data(request):

    if request.method == 'POST':
        product_json = request.data
        basket = Basket.objects.create(
            basket = product_json
        )
        compare.delay(basket.id)
        return Response({"basket_id":basket.id},status=status.HTTP_200_OK)

    if request.method == 'GET':
        baskets = Basket.objects.all()
        serializer = TestSerializer(baskets, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['GET'])
def basket_view(request, pk):
    try:
        basket = Basket.objects.get(pk=pk)
    except basket.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = BasketResultsSerializer(basket)
        return Response(serializer.data)
