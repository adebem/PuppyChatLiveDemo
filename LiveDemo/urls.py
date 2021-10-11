from django.urls import path, register_converter
from .views import home

urlpatterns = [
    path('', home, name='home')
]
