from django.urls import path
#from .views import scraping_data, basket_view
from .views import CreateBasketTaskView, GetBasketsView

urlpatterns = [
    path("",CreateBasketTaskView.as_view(),name="scraping"),
    path("basket/",GetBasketsView.as_view({'get':'list'}),name="data"),
    path("basket/<int:pk>/",GetBasketsView.as_view({'get':'retrieve'}), name="ranking")
]