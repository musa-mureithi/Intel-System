from django.urls import path
from .views import get_logs

urlpatterns = [
    path("get_logs/", get_logs),
]