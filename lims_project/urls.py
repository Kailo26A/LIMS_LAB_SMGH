"""
URLs principales del proyecto LIMS.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # API de recepción de muestras
    path('api/', include('reception.urls')),
    
    # Autenticación de Django REST Framework (para login/logout en el navegador)
    path('api-auth/', include('rest_framework.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
