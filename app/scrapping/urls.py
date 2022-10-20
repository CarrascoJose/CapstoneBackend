from django.urls import path
from .views import scraping_data, basket_view

urlpatterns = [
    path("",scraping_data,name="scraping"),
    path("basket/<int:pk>/",basket_view, name="ranking")
]