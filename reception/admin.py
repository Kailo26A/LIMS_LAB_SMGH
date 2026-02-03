from django.contrib import admin
from .models import Cliente, Muestra, Ensayo, HistorialEstado

# =============================================================================
# CONFIGURACIÓN DEL PANEL ADMIN PARA CLIENTES
# =============================================================================

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para Clientes
    """
    list_display = ['nombre_empresa', 'nit', 'ciudad', 'tipo_cliente', 'activo', 'persona_contacto', 'email']
    list_filter = ['tipo_cliente', 'activo', 'ciudad', 'pais']
    search_fields = ['nombre_empresa', 'nit', 'persona_contacto', 'email']
    ordering = ['nombre_empresa']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_empresa', 'nit', 'tipo_cliente', 'activo')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'pais')
        }),
        ('Contacto', {
            'fields': ('persona_contacto', 'cargo_contacto', 'email', 'telefono')
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)  # Sección colapsable
        }),
    )
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']


# =============================================================================
# CONFIGURACIÓN DEL PANEL ADMIN PARA MUESTRAS
# =============================================================================

class EnsayoInline(admin.TabularInline):
    """
    Permite ver y editar ensayos directamente desde la muestra
    """
    model = Ensayo
    extra = 1  # Muestra 1 fila vacía para agregar ensayos
    fields = ['nombre_analisis', 'norma_metodo', 'prioridad', 'fecha_resultados_requerida', 'estado_ensayo', 'analista_asignado']


class HistorialInline(admin.TabularInline):
    """
    Muestra el historial de cambios directamente en la muestra
    """
    model = HistorialEstado
    extra = 0  # No mostrar filas vacías
    can_delete = False  # No permitir eliminar registros de historial
    readonly_fields = ['estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio', 'observaciones']
    fields = ['estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio', 'observaciones']


@admin.register(Muestra)
class MuestraAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para Muestras
    """
    list_display = [
        'codigo_muestra', 'cliente', 'tipo_muestra', 'estado', 
        'muestra_aceptada', 'fecha_registro', 'usuario_recepcion'
    ]
    list_filter = [
        'estado', 'tipo_muestra', 'muestra_aceptada', 
        'condiciones_recepcion', 'riesgo_asociado', 'fecha_registro'
    ]
    search_fields = ['codigo_muestra', 'cliente__nombre_empresa', 'descripcion_muestra', 'lote']
    ordering = ['-fecha_registro']
    date_hierarchy = 'fecha_registro'
    
    # Mostrar ensayos e historial en la misma página de la muestra
    inlines = [EnsayoInline, HistorialInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo_muestra', 'cliente', 'estado', 'version_plataforma')
        }),
        ('Recepción', {
            'fields': (
                'usuario_recepcion', 'fecha_envio', 'fecha_recepcion',
                'medio_entrega', 'condiciones_recepcion', 'observaciones_recepcion'
            )
        }),
        ('Información de la Muestra', {
            'fields': (
                'tipo_muestra', 'matriz', 'descripcion_muestra',
                'cantidad_enviada', 'unidad_cantidad', 'lote'
            )
        }),
        ('Muestreo', {
            'fields': ('fecha_muestreo', 'responsable_muestreo')
        }),
        ('Condiciones', {
            'fields': ('condiciones_almacenamiento', 'riesgo_asociado')
        }),
        ('Aceptación', {
            'fields': (
                'muestra_aceptada', 'fecha_aceptacion', 
                'usuario_aceptacion', 'firma_digital_cliente'
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'codigo_muestra', 'fecha_registro', 'fecha_recepcion', 
        'fecha_actualizacion', 'version_plataforma'
    ]
    
    # Acciones masivas personalizadas
    actions = ['marcar_como_aceptadas', 'cambiar_estado_a_analisis']
    
    def marcar_como_aceptadas(self, request, queryset):
        """
        Acción para marcar múltiples muestras como aceptadas
        """
        from django.utils import timezone
        updated = 0
        for muestra in queryset:
            if not muestra.muestra_aceptada:
                muestra.muestra_aceptada = True
                muestra.fecha_aceptacion = timezone.now()
                muestra.usuario_aceptacion = request.user
                muestra.estado = 'ACEPTADA'
                muestra.save()
                
                # Registrar en historial
                HistorialEstado.objects.create(
                    muestra=muestra,
                    estado_anterior=muestra.estado,
                    estado_nuevo='ACEPTADA',
                    usuario=request.user,
                    observaciones='Aceptación masiva desde panel admin'
                )
                updated += 1
        
        self.message_user(request, f'{updated} muestra(s) marcada(s) como aceptadas.')
    
    marcar_como_aceptadas.short_description = "Marcar como aceptadas"
    
    def cambiar_estado_a_analisis(self, request, queryset):
        """
        Acción para cambiar estado de múltiples muestras a "En Análisis"
        """
        updated = 0
        for muestra in queryset:
            if muestra.muestra_aceptada:
                estado_anterior = muestra.estado
                muestra.estado = 'EN_ANALISIS'
                muestra.save()
                
                # Registrar en historial
                HistorialEstado.objects.create(
                    muestra=muestra,
                    estado_anterior=estado_anterior,
                    estado_nuevo='EN_ANALISIS',
                    usuario=request.user,
                    observaciones='Cambio masivo de estado desde panel admin'
                )
                updated += 1
        
        self.message_user(request, f'{updated} muestra(s) cambiadas a estado "En Análisis".')
    
    cambiar_estado_a_analisis.short_description = "Cambiar estado a En Análisis"


# =============================================================================
# CONFIGURACIÓN DEL PANEL ADMIN PARA ENSAYOS
# =============================================================================

@admin.register(Ensayo)
class EnsayoAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para Ensayos
    """
    list_display = [
        'nombre_analisis', 'muestra', 'prioridad', 'estado_ensayo',
        'analista_asignado', 'fecha_resultados_requerida'
    ]
    list_filter = [
        'estado_ensayo', 'prioridad', 'analista_asignado',
        'fecha_resultados_requerida', 'fecha_creacion'
    ]
    search_fields = [
        'nombre_analisis', 'norma_metodo', 'muestra__codigo_muestra',
        'resultados', 'observaciones_ensayo'
    ]
    ordering = ['prioridad', 'fecha_resultados_requerida']
    date_hierarchy = 'fecha_resultados_requerida'
    
    fieldsets = (
        ('Información del Ensayo', {
            'fields': ('muestra', 'nombre_analisis', 'norma_metodo', 'prioridad', 'fecha_resultados_requerida')
        }),
        ('Ejecución', {
            'fields': (
                'estado_ensayo', 'analista_asignado',
                'fecha_inicio', 'fecha_finalizacion'
            )
        }),
        ('Resultados', {
            'fields': ('resultados', 'observaciones_ensayo'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    # Filtros rápidos en la barra lateral
    list_per_page = 50


# =============================================================================
# CONFIGURACIÓN DEL PANEL ADMIN PARA HISTORIAL
# =============================================================================

@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para Historial de Estados
    """
    list_display = [
        'muestra', 'estado_anterior', 'estado_nuevo',
        'usuario', 'fecha_cambio'
    ]
    list_filter = ['estado_nuevo', 'estado_anterior', 'fecha_cambio', 'usuario']
    search_fields = ['muestra__codigo_muestra', 'observaciones']
    ordering = ['-fecha_cambio']
    date_hierarchy = 'fecha_cambio'
    
    # Historial es solo lectura
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    # Todos los campos son de solo lectura
    readonly_fields = ['muestra', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio', 'observaciones']
    
    fieldsets = (
        ('Información del Cambio', {
            'fields': (
                'muestra', 'estado_anterior', 'estado_nuevo',
                'usuario', 'fecha_cambio', 'observaciones'
            )
        }),
    )
