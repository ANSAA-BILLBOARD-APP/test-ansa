from django.urls import path
from . import views

urlpatterns = [
    path('detect-and-predict-billboard/', views.process_images, name='detect_and_predict_billboard'),
    path('validate-reference-image/', views.detect_book_in_image, name='validate_reference_image'),
]
