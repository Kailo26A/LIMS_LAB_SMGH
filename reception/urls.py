from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, MuestraViewSet, EnsayoViewSet, HistorialEstadoViewSet

# =============================================================================
# ROUTER - Genera automáticamente las URLs para los ViewSets
# =============================================================================

router = DefaultRouter()

# Registrar ViewSets
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'muestras', MuestraViewSet, basename='muestra')
router.register(r'ensayos', EnsayoViewSet, basename='ensayo')
router.register(r'historial', HistorialEstadoViewSet, basename='historial')

# =============================================================================
# URLs GENERADAS AUTOMÁTICAMENTE:
# =============================================================================
# 
# CLIENTES:
# - GET    /api/clientes/                 - Listar todos
# - POST   /api/clientes/                 - Crear nuevo
# - GET    /api/clientes/{id}/            - Ver detalle
# - PUT    /api/clientes/{id}/            - Actualizar completo
# - PATCH  /api/clientes/{id}/            - Actualizar parcial
# - DELETE /api/clientes/{id}/            - Eliminar
# - GET    /api/clientes/{id}/muestras/   - Ver muestras del cliente (custom action)
#
# MUESTRAS:
# - GET    /api/muestras/                 - Listar todas
# - POST   /api/muestras/                 - Crear nueva
# - GET    /api/muestras/{id}/            - Ver detalle
# - PUT    /api/muestras/{id}/            - Actualizar completa
# - PATCH  /api/muestras/{id}/            - Actualizar parcial
# - DELETE /api/muestras/{id}/            - Eliminar
# - POST   /api/muestras/{id}/aceptar/    - Aceptar muestra (custom action)
# - POST   /api/muestras/{id}/actualizar_estado/ - Cambiar estado (custom action)
# - GET    /api/muestras/{id}/ensayos/    - Ver ensayos (custom action)
# - POST   /api/muestras/{id}/agregar_ensayos/ - Agregar ensayos (custom action)
# - POST   /api/muestras/{id}/validar_suficiencia/ - Validar cantidad (custom action)
# - GET    /api/muestras/{id}/historial/  - Ver historial (custom action)
#
# ENSAYOS:
# - GET    /api/ensayos/                  - Listar todos
# - POST   /api/ensayos/                  - Crear nuevo
# - GET    /api/ensayos/{id}/             - Ver detalle
# - PUT    /api/ensayos/{id}/             - Actualizar completo
# - PATCH  /api/ensayos/{id}/             - Actualizar parcial
# - DELETE /api/ensayos/{id}/             - Eliminar
# - POST   /api/ensayos/{id}/asignar_analista/ - Asignar analista (custom action)
# - POST   /api/ensayos/{id}/registrar_resultados/ - Registrar resultados (custom action)
#
# HISTORIAL:
# - GET    /api/historial/                - Listar todo el historial
# - GET    /api/historial/{id}/           - Ver detalle de un cambio
# =============================================================================

urlpatterns = [
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]
