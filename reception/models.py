from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

# =============================================================================
# NUMERAL 2: INFORMACIÓN DEL CLIENTE
# =============================================================================

class Cliente(models.Model):
    """
    Almacena la información de los clientes que envían muestras al laboratorio.
    Permite tener un registro centralizado y reutilizable de clientes.
    """
    # Campos básicos del cliente
    nombre_empresa = models.CharField(
        max_length=255,
        verbose_name="Nombre de la empresa/cliente",
        help_text="Razón social o nombre del cliente"
    )
    nit = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="NIT o identificación",
        help_text="Número de identificación tributaria o documento"
    )
    direccion = models.TextField(
        verbose_name="Dirección",
        help_text="Dirección completa del cliente"
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name="Ciudad"
    )
    pais = models.CharField(
        max_length=100,
        default="Colombia",
        verbose_name="País"
    )
    
    # Información de contacto
    persona_contacto = models.CharField(
        max_length=255,
        verbose_name="Persona de contacto",
        help_text="Nombre del contacto principal"
    )
    cargo_contacto = models.CharField(
        max_length=100,
        verbose_name="Cargo del contacto",
        blank=True
    )
    email = models.EmailField(
        verbose_name="Correo electrónico",
        help_text="Canal principal para notificaciones"
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        help_text="Canal alterno para comunicaciones urgentes"
    )
    
    # Clasificación del cliente
    TIPO_CLIENTE_CHOICES = [
        ('NUEVO', 'Cliente Nuevo'),
        ('RECURRENTE', 'Cliente Recurrente'),
    ]
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        default='NUEVO',
        verbose_name="Tipo de cliente"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Cliente activo",
        help_text="Indica si el cliente está autorizado para enviar muestras"
    )
    
    # Auditoría
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre_empresa']
    
    def __str__(self):
        return f"{self.nombre_empresa} - {self.nit}"


# =============================================================================
# NUMERALES 1, 3, 4: INFORMACIÓN DE LA MUESTRA
# =============================================================================

class Muestra(models.Model):
    """
    Modelo principal que representa una muestra recibida en el laboratorio.
    Integra toda la información de recepción, trazabilidad y estado.
    """
    
    # -----------------------------------------------------------------
    # NUMERAL 1: IDENTIFICACIÓN GENERAL
    # -----------------------------------------------------------------
    codigo_muestra = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="Código único de muestra",
        help_text="Generado automáticamente al crear la muestra"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora de registro automático",
        help_text="Momento exacto de ingreso al sistema"
    )
    ESTADO_CHOICES = [
        ('REGISTRADA', 'Registrada'),
        ('ACEPTADA', 'Aceptada'),
        ('EN_ANALISIS', 'En Análisis'),
        ('ANALIZADA', 'Analizada'),
        ('COMPLETADA', 'Completada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='REGISTRADA',
        verbose_name="Estado de la muestra"
    )
    version_plataforma = models.CharField(
        max_length=20,
        default="1.0",
        editable=False,
        verbose_name="Versión del formato/plataforma",
        help_text="Control documental del sistema"
    )
    usuario_recepcion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='muestras_recibidas',
        verbose_name="Usuario que valida la recepción",
        help_text="Responsable del proceso de recepción"
    )
    
    # -----------------------------------------------------------------
    # NUMERAL 2: RELACIÓN CON CLIENTE
    # -----------------------------------------------------------------
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='muestras',
        verbose_name="Cliente"
    )
    
    # -----------------------------------------------------------------
    # NUMERAL 3: INFORMACIÓN DEL ENVÍO Y RECEPCIÓN
    # -----------------------------------------------------------------
    fecha_envio = models.DateTimeField(
        verbose_name="Fecha de envío de la muestra",
        help_text="Permite evaluar tiempos de transporte"
    )
    fecha_recepcion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora de recepción",
        help_text="Clave para cálculo de tiempos de respuesta"
    )
    MEDIO_ENTREGA_CHOICES = [
        ('CORREO', 'Correo/Courier'),
        ('MENSAJERIA', 'Mensajería'),
        ('PERSONAL', 'Entrega Personal'),
        ('OTRO', 'Otro'),
    ]
    medio_entrega = models.CharField(
        max_length=20,
        choices=MEDIO_ENTREGA_CHOICES,
        verbose_name="Medio de entrega",
        help_text="Permite evaluar riesgos asociados al transporte"
    )
    CONDICIONES_RECEPCION_CHOICES = [
        ('OPTIMAS', 'Óptimas'),
        ('ACEPTABLES', 'Aceptables'),
        ('NO_CONFORMES', 'No Conformes'),
    ]
    condiciones_recepcion = models.CharField(
        max_length=20,
        choices=CONDICIONES_RECEPCION_CHOICES,
        default='OPTIMAS',
        verbose_name="Condiciones de recepción",
        help_text="Verificación de integridad de la muestra"
    )
    observaciones_recepcion = models.TextField(
        blank=True,
        verbose_name="Observaciones de recepción",
        help_text="Anomalías o comentarios relevantes"
    )
    
    # -----------------------------------------------------------------
    # NUMERAL 4: INFORMACIÓN DE LA MUESTRA
    # -----------------------------------------------------------------
    TIPO_MUESTRA_CHOICES = [
        ('AGUA', 'Agua'),
        ('ALIMENTO', 'Alimento'),
        ('COSMETICO', 'Cosmético'),
        ('FARMACEUTICO', 'Farmacéutico'),
        ('QUIMICO', 'Químico'),
        ('AMBIENTAL', 'Ambiental'),
        ('OTRO', 'Otro'),
    ]
    tipo_muestra = models.CharField(
        max_length=50,
        choices=TIPO_MUESTRA_CHOICES,
        verbose_name="Tipo de muestra",
        help_text="Define el tratamiento analítico adecuado"
    )
    matriz = models.CharField(
        max_length=100,
        verbose_name="Matriz",
        help_text="Esencial para validar aplicabilidad del método (ej: líquido, sólido, gel)"
    )
    descripcion_muestra = models.TextField(
        verbose_name="Descripción de la muestra",
        help_text="Contexto adicional para correcta identificación"
    )
    cantidad_enviada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Cantidad enviada",
        help_text="Permite verificar suficiencia para análisis"
    )
    unidad_cantidad = models.CharField(
        max_length=20,
        default="mL",
        verbose_name="Unidad de medida",
        help_text="ej: mL, g, kg, unidades"
    )
    lote = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Lote/Batch",
        help_text="Trazabilidad del producto del cliente"
    )
    fecha_muestreo = models.DateTimeField(
        verbose_name="Fecha de muestreo",
        help_text="Permite evaluar estabilidad y validez de resultados"
    )
    responsable_muestreo = models.CharField(
        max_length=255,
        verbose_name="Responsable del muestreo",
        help_text="Trazabilidad del origen"
    )
    ALMACENAMIENTO_CHOICES = [
        ('AMBIENTE', 'Temperatura ambiente'),
        ('REFRIGERACION', 'Refrigeración (2-8°C)'),
        ('CONGELACION', 'Congelación (-20°C)'),
        ('ULTRACONGELACION', 'Ultracongelación (-80°C)'),
    ]
    condiciones_almacenamiento = models.CharField(
        max_length=30,
        choices=ALMACENAMIENTO_CHOICES,
        verbose_name="Condiciones de almacenamiento recomendadas",
        help_text="Conserva integridad de la muestra"
    )
    RIESGO_CHOICES = [
        ('NINGUNO', 'Sin riesgo'),
        ('BAJO', 'Riesgo bajo'),
        ('MEDIO', 'Riesgo medio'),
        ('ALTO', 'Riesgo alto'),
    ]
    riesgo_asociado = models.CharField(
        max_length=20,
        choices=RIESGO_CHOICES,
        default='NINGUNO',
        verbose_name="Riesgo asociado",
        help_text="Permite aplicar medidas de bioseguridad"
    )
    
    # -----------------------------------------------------------------
    # NUMERAL 7: ACEPTACIÓN Y CADENA DE CUSTODIA
    # -----------------------------------------------------------------
    muestra_aceptada = models.BooleanField(
        default=False,
        verbose_name="Confirmación de aceptación",
        help_text="Formaliza inicio de responsabilidad del laboratorio"
    )
    fecha_aceptacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de aceptación",
        help_text="Cierra proceso de recepción y activa flujo analítico"
    )
    usuario_aceptacion = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='muestras_aceptadas',
        verbose_name="Usuario que acepta la muestra",
        help_text="Asigna responsabilidad técnica"
    )
    firma_digital_cliente = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Firma digital o conformidad del cliente",
        help_text="Demuestra acuerdo con condiciones del servicio"
    )
    
    # Auditoría
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Muestra"
        verbose_name_plural = "Muestras"
        ordering = ['-fecha_registro']
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para generar automáticamente el código de muestra
        """
        if not self.codigo_muestra:
            # Genera código único: LIMS-YYYYMMDD-UUID
            fecha_actual = timezone.now().strftime('%Y%m%d')
            codigo_uuid = str(uuid.uuid4())[:8].upper()
            self.codigo_muestra = f"LIMS-{fecha_actual}-{codigo_uuid}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.codigo_muestra} - {self.cliente.nombre_empresa}"


# =============================================================================
# NUMERAL 5: ENSAYOS SOLICITADOS
# =============================================================================

class Ensayo(models.Model):
    """
    Representa los análisis o pruebas solicitadas para una muestra.
    Una muestra puede tener múltiples ensayos.
    """
    muestra = models.ForeignKey(
        Muestra,
        on_delete=models.CASCADE,
        related_name='ensayos',
        verbose_name="Muestra"
    )
    nombre_analisis = models.CharField(
        max_length=255,
        verbose_name="Análisis solicitado",
        help_text="Define alcance técnico del servicio"
    )
    norma_metodo = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Norma o método aplicable",
        help_text="Alinea expectativas técnicas entre cliente y laboratorio"
    )
    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('NORMAL', 'Normal'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='NORMAL',
        verbose_name="Prioridad del análisis",
        help_text="Gestiona carga de trabajo del laboratorio"
    )
    fecha_resultados_requerida = models.DateField(
        verbose_name="Fecha requerida de resultados",
        help_text="Permite comprometer plazos de entrega realistas"
    )
    
    # Campos de ejecución
    ESTADO_ENSAYO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]
    estado_ensayo = models.CharField(
        max_length=20,
        choices=ESTADO_ENSAYO_CHOICES,
        default='PENDIENTE',
        verbose_name="Estado del ensayo"
    )
    analista_asignado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ensayos_asignados',
        verbose_name="Analista asignado"
    )
    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de inicio del análisis"
    )
    fecha_finalizacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de finalización del análisis"
    )
    resultados = models.TextField(
        blank=True,
        verbose_name="Resultados del ensayo"
    )
    observaciones_ensayo = models.TextField(
        blank=True,
        verbose_name="Observaciones del ensayo"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ensayo"
        verbose_name_plural = "Ensayos"
        ordering = ['prioridad', 'fecha_resultados_requerida']
    
    def __str__(self):
        return f"{self.nombre_analisis} - {self.muestra.codigo_muestra}"


# =============================================================================
# NUMERAL 7: HISTORIAL DE CAMBIOS (Trazabilidad completa)
# =============================================================================

class HistorialEstado(models.Model):
    """
    Registra todos los cambios de estado de una muestra para trazabilidad completa.
    Cumple con requisitos de auditoría ISO/IEC 17025.
    """
    muestra = models.ForeignKey(
        Muestra,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name="Muestra"
    )
    estado_anterior = models.CharField(
        max_length=20,
        verbose_name="Estado anterior"
    )
    estado_nuevo = models.CharField(
        max_length=20,
        verbose_name="Estado nuevo"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Usuario que realizó el cambio"
    )
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora del cambio"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones del cambio"
    )
    
    class Meta:
        verbose_name = "Historial de Estado"
        verbose_name_plural = "Historial de Estados"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.muestra.codigo_muestra}: {self.estado_anterior} → {self.estado_nuevo}"
