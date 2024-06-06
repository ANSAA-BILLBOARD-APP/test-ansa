from django.urls import path
from . import views

urlpatterns = [
    path('download-report/', views.ReportDownloadView.as_view(), name='download-report'),
    path('count-assets/', views.CountReportView.as_view(), name='count-assets'),
]
