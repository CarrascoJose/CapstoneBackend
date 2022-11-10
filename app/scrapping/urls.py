from django.urls import path
#from .views import scraping_data, basket_view
from .views import CreateBasketTaskView, GetBasketResultsView, GetExternalUserBaskets

urlpatterns = [
    path("",CreateBasketTaskView.as_view(),name="scraping"),


    # Returns the specific basket
    path("basket/<int:pk>/",GetBasketResultsView.as_view(), name="ranking"),

    # Returns the baskets of specific user
    path("users/<int:pk>/basket/",GetExternalUserBaskets.as_view(), name="user_baskets")
]