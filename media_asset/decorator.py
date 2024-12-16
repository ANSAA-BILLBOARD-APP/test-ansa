from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def apikey_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key != settings.API_KEY:
            return Response({"detail": "Invalid or missing API key."}, status=status.HTTP_403_FORBIDDEN)
        return view_func(request, *args, **kwargs)
    return wrapped_view
