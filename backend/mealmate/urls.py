from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({"message": "Welcome to MealMate API. The frontend is running on http://localhost:5173/"})

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path('api/', include('restaurants.urls')),
    path('api/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
