from django.contrib import admin
from .models import Cliente, Muestra, Ensayo, HistorialEstado

# =============================================================================
# CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN PARA CLIENTE
# =============================================================================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Cliente.
    """
    # Campos a mostrar en la lista
    list_display = [
        'nombre_empresa',
        'nit',
        'ciudad',
        'pais',
        'persona_contacto',
        'email',
        'tipo_cliente',
        'activo'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = ['tipo_cliente', 'activo', 'pais', 'ciudad']
    
    # Campos de búsqueda
    search_fields = ['nombre_empresa', 'nit', 'persona_contacto', 'email']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    
    # Orden por defecto
    ordering = ['nombre_empresa']
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información General', {
            'fields': ('nombre_empresa', 'nit', 'tipo_cliente', 'activo')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'pais')
        }),
        ('Información de Contacto', {
            'fields': ('persona_contacto', 'cargo_contacto', 'email', 'telefono')
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)  # Inicia colapsado
        }),
    )

# =============================================================================
# CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN PARA MUESTRA
# =============================================================================
@admin.register(Muestra)
class MuestraAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Muestra.
    """
    # Campos a mostrar en la lista
    list_display = [
        'codigo_muestra',
        'cliente',
        'tipo_muestra',
        'estado',
        'fecha_registro',
        'muestra_aceptada',
        'usuario_recepcion'
    ]
    
    # Filtros
    list_filter = [
        'estado',
        'tipo_muestra',
        'muestra_aceptada',
        'condiciones_recepcion',
        'riesgo_asociado',
        'fecha_registro',
    ]
    
    # Búsqueda
    search_fields = [
        'codigo_muestra',
        'cliente__nombre_empresa',
        'descripcion_muestra',
        'lote'
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'codigo_muestra',
        'fecha_registro',
        'fecha_recepcion',
        'fecha_actualizacion',
        'version_plataforma'
    ]
    
    # Orden
    ordering = ['-fecha_registro']
    
    # Fecha de jerarquía (permite navegar por fechas)
    date_hierarchy = 'fecha_registro'
    
    # Campos que se pueden editar directamente en la lista
    list_editable = ['estado']
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Identificación', {
            'fields': (
                'codigo_muestra',
                'version_plataforma',
                'estado',
                'cliente',
                'usuario_recepcion'
            )
        }),
        ('Información del Envío', {
            'fields': (
                'fecha_envio',
                'fecha_recepcion',
                'medio_entrega',
                'condiciones_recepcion',
                'observaciones_recepcion'
            )
        }),
        ('Información de la Muestra', {
            'fields': (
                'tipo_muestra',
                'matriz',
                'descripcion_muestra',
                'cantidad_enviada',
                'unidad_cantidad',
                'lote',
                'fecha_muestreo',
                'responsable_muestreo',
                'condiciones_almacenamiento',
                'riesgo_asociado'
            )
        }),
        ('Aceptación', {
            'fields': (
                'muestra_aceptada',
                'fecha_aceptacion',
                'usuario_aceptacion',
                'firma_digital_cliente'
            )
        }),
        ('Auditoría', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )
    
    # Acciones personalizadas
    actions = ['marcar_como_aceptada', 'marcar_como_rechazada']
    
    def marcar_como_aceptada(self, request, queryset):
        """Acción para marcar muestras como aceptadas"""
        from django.utils import timezone
        updated = queryset.update(
            muestra_aceptada=True,
            fecha_aceptacion=timezone.now(),
            estado='ACEPTADA'
        )
        self.message_user(request, f'{updated} muestra(s) marcada(s) como aceptada(s).')
    marcar_como_aceptada.short_description = "Marcar como aceptada(s)"
    
    def marcar_como_rechazada(self, request, queryset):
        """Acción para marcar muestras como rechazadas"""
        updated = queryset.update(estado='RECHAZADA')
        self.message_user(request, f'{updated} muestra(s) marcada(s) como rechazada(s).')
    marcar_como_rechazada.short_description = "Marcar como rechazada(s)"

# =============================================================================
# CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN PARA ENSAYO
# =============================================================================
@admin.register(Ensayo)
class EnsayoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Ensayo.
    """
    # Campos a mostrar
    list_display = [
        'id',
        'muestra',
        'nombre_analisis',
        'prioridad',
        'estado_ensayo',
        'analista_asignado',
        'fecha_resultados_requerida'
    ]
    
    # Filtros
    list_filter = [
        'estado_ensayo',
        'prioridad',
        'fecha_resultados_requerida',
        'analista_asignado'
    ]
    
    # Búsqueda
    search_fields = [
        'nombre_analisis',
        'norma_metodo',
        'muestra__codigo_muestra'
    ]
    
    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    # Orden
    ordering = ['prioridad', 'fecha_resultados_requerida']
    
    # Jerarquía de fecha
    date_hierarchy = 'fecha_resultados_requerida'
    
    # Campos editables en lista
    list_editable = ['prioridad', 'estado_ensayo', 'analista_asignado']
    
    # Organización de campos
    fieldsets = (
        ('Información General', {
            'fields': (
                'muestra',
                'nombre_analisis',
                'norma_metodo',
                'prioridad',
                'fecha_resultados_requerida'
            )
        }),
        ('Ejecución', {
            'fields': (
                'estado_ensayo',
                'analista_asignado',
                'fecha_inicio',
                'fecha_finalizacion'
            )
        }),
        ('Resultados', {
            'fields': (
                'resultados',
                'observaciones_ensayo'
            )
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

# =============================================================================
# CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN PARA HISTORIAL
# =============================================================================
@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo HistorialEstado.
    Solo lectura.
    """
    # Campos a mostrar
    list_display = [
        'id',
        'muestra',
        'estado_anterior',
        'estado_nuevo',
        'usuario',
        'fecha_cambio'
    ]
    
    # Filtros
    list_filter = ['estado_anterior', 'estado_nuevo', 'fecha_cambio']
    
    # Búsqueda
    search_fields = ['muestra__codigo_muestra', 'observaciones']
    
    # Todos los campos son de solo lectura
    readonly_fields = [
        'muestra',
        'estado_anterior',
        'estado_nuevo',
        'usuario',
        'fecha_cambio',
        'observaciones'
    ]
    
    # Orden
    ordering = ['-fecha_cambio']
    
    # Jerarquía de fecha
    date_hierarchy = 'fecha_cambio'
    
    # No permitir agregar, editar o eliminar
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Configuración del sitio admin
admin.site.site_header = "Administración LIMS - Laboratorio de Control de Calidad"
admin.site.site_title = "LIMS Admin"
admin.site.index_title = "Panel de Administración"
