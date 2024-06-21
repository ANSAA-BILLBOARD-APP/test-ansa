from django.urls import path
from . import views

urlpatterns = [
    path('monthly-stats', views.MonthlyTarget.as_view())
]
