from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .admin import AnsaaUserAdmin
from django.contrib import admin
from .models import AnsaaUser


admin_site = admin.site
ansaa_user_admin = AnsaaUserAdmin(model=AnsaaUser, admin_site=admin_site)

urlpatterns = [
    path('auth/logout/', views.LogoutView.as_view()),
    path('auth/profile/', views.UserProfileViews.as_view()),
    path('auth/login/', views.LoginAPIView.as_view()),
    path("auth/api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema")),
    path('authentication/', include(ansaa_user_admin.get_urls())),
]
