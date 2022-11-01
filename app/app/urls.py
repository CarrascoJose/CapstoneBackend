
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/",include("scrapping.urls")),
    path("users/",include("users.urls")),
    re_path(r'^celery-progress/',include('celery_progress.urls'))
]
