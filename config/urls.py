"""
URL configuration for Retro Cassette Music Generator project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse

def api_status(request):
    """Simple API status endpoint for health checks"""
    return JsonResponse({'status': 'ok', 'message': 'API is running'})

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', api_status, name='api-status'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/songs/', include('apps.songs.urls')),
    path('api/library/', include('apps.library.urls')),
    path('api/generation/', include('apps.generation.urls')),
    
    # Frontend
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
