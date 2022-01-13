from django.http import JsonResponse
from django.urls import path, include

urlpatterns = [
    path('health-check/', lambda x: JsonResponse(dict(status='ok'), status=200)),
    path('', include('chatApplication.apis.urls'))
]
