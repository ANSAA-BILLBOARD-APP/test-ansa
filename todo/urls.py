from django.urls import path
from . import views

urlpatterns = [
    path('task/devices/', views.DeviceListAPIView.as_view(), name='device_list'),
    path('devices/verify/', views.DeviceCreateAPIView.as_view(), name='create_device'),
    path('devices/<int:pk>/', views.DeviceUpdateAPIView.as_view(), name='update device'),
    path('task/', views.TaskAPIView.as_view(), name="assigned_asset"),
]