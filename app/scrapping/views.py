from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .tasks import compare
from .models import Basket
from .serializers import TestSerializer

@api_view(['GET','POST'])
def test_celery(request):

    if request.method == 'POST':
        product_json = request.data
        basket = Basket.objects.create(
            basket = product_json
        )
        compare.delay(basket.id)
        return Response({"message":"Processing"},status=status.HTTP_200_OK)

    if request.method == 'GET':
        baskets = Basket.objects.all()
        serializer = TestSerializer(baskets, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


