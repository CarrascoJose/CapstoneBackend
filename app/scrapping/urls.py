from django.urls import path
#from .views import scraping_data, basket_view
from .views import CreateBasketTaskView, GetUserBasketsView, GetBasketResultsView

urlpatterns = [
    path("",CreateBasketTaskView.as_view(),name="scraping"),
    path("basket/",GetUserBasketsView.as_view(),name="my_baskets"),
    path("basket/<int:pk>/",GetBasketResultsView.as_view(), name="ranking")
]