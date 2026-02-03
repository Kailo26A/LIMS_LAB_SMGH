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
"""
CLIENTES:
  GET    /api/clientes/                    → Listar todos los clientes
  POST   /api/clientes/                    → Crear nuevo cliente
  GET    /api/clientes/{id}/               → Ver un cliente específico
  PUT    /api/clientes/{id}/               → Actualizar cliente completo
  PATCH  /api/clientes/{id}/               → Actualizar cliente parcial
  DELETE /api/clientes/{id}/               → Eliminar cliente
  GET    /api/clientes/{id}/muestras/      → Ver muestras de un cliente

MUESTRAS:
  GET    /api/muestras/                    → Listar todas las muestras
  POST   /api/muestras/                    → Crear nueva muestra
  GET    /api/muestras/{id}/               → Ver una muestra específica
  PUT    /api/muestras/{id}/               → Actualizar muestra completa
  PATCH  /api/muestras/{id}/               → Actualizar muestra parcial
  DELETE /api/muestras/{id}/               → Eliminar muestra
  POST   /api/muestras/{id}/aceptar/       → Aceptar muestra
  POST   /api/muestras/{id}/actualizar_estado/ → Actualizar estado
  GET    /api/muestras/{id}/ensayos/       → Ver ensayos de una muestra
  POST   /api/muestras/{id}/agregar_ensayos/ → Agregar ensayos
  POST   /api/muestras/{id}/validar_suficiencia/ → Validar cantidad
  GET    /api/muestras/{id}/historial/     → Ver historial de cambios

ENSAYOS:
  GET    /api/ensayos/                     → Listar todos los ensayos
  POST   /api/ensayos/                     → Crear nuevo ensayo
  GET    /api/ensayos/{id}/                → Ver un ensayo específico
  PUT    /api/ensayos/{id}/                → Actualizar ensayo completo
  PATCH  /api/ensayos/{id}/                → Actualizar ensayo parcial
  DELETE /api/ensayos/{id}/                → Eliminar ensayo
  POST   /api/ensayos/{id}/asignar_analista/ → Asignar analista
  POST   /api/ensayos/{id}/registrar_resultados/ → Registrar resultados

HISTORIAL:
  GET    /api/historial/                   → Listar todo el historial
  GET    /api/historial/{id}/              → Ver un registro específico
"""

# =============================================================================
urlpatterns = [
    path('', include(router.urls)),
]
