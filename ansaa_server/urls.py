from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path('admin/', admin.site.urls),
    path('api/', include("authentication.urls")),
    path('api/', include('todo.urls')),
    path('api/', include('report.urls')),
    path('api/', include("media_asset.urls")),
    path('api/', include("ansa_target.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



# server {
#     server_name ansaa.duckdns.org;

#     location = /favicon.ico { access_log off; log_not_found off; }

#     location /static/ {
#         root /root/ansaa-bknd; 
#     }

#     location /media/ {
#         root /root/ansaa-bknd;
#     }

#     location / {
#         include proxy_params;
#         proxy_pass http://unix:/root/ansaa-bknd/gunicorn.sock;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#     }

#     error_page 500 502 503 504 /50x.html;
#     location = /50x.html {
#         root /usr/share/nginx/html;
#     }

#     listen 443 ssl; # managed by Certbot
#     ssl_certificate /etc/letsencrypt/live/ansaa.duckdns.org/fullchain.pem; # managed by Certbot
#     ssl_certificate_key /etc/letsencrypt/live/ansaa.duckdns.org/privkey.pem; # managed by Certbot
#     include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
#     ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

# }
# server {
#     if ($host = ansaa.duckdns.org) {
#         return 301 https://$host$request_uri;
#     } # managed by Certbot


#     listen 80;
#     server_name ansaa.duckdns.org;
#     return 404; # managed by Certbot


# }