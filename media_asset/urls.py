from django.urls import path
from . import views

urlpatterns = [
    path('asset/post-assets/', views.CreateAssetAPIView.as_view(), name='post_assets'),
    path('asset/list-assets/', views.AssetListAPIView.as_view(), name="list_assets"),
    path('asset/<int:pk>/', views.AssetRetrieveUpdateAPIView.as_view(), name='update_retrieve_asset'),
    path('asset/search/', views.AssetSearchAPIView.as_view(), name='asset_search'),
    path('asset/zones/', views.ZonesListView.as_view(), name='zones-list'),
    path('asset/dimensions/', views.DimensionsListView.as_view(), name='dimensions-list'),
    path('asset/<int:pk>/delete/', views.AssetDeleteAPIView.as_view(), name='asset-delete'),

    # oasis endpoints
    path('billboards/<str:asset_name>/update-payment/', views.UpdatePaymentView.as_view(), name='update-payment'),
    path('asset/assets-list/', views.AssetDetailsListAPIView.as_view(), name="list_assets"),
]
