from django.urls import path
from .views import predict_performance, index

urlpatterns = [
    path('', index, name='index'),
    path('predict/', predict_performance, name='predict'),
]