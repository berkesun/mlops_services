
from django.contrib import admin
from django.urls import path
from mlops_services import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crawler/liveactivity/', views.crawl_liveA, name='Live Activity Crawler')

]
