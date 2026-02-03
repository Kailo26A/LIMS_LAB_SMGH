from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cliente, Muestra, Ensayo, HistorialEstado
from django.utils import timezone

# =============================================================================
# SERIALIZER PARA USUARIOS
# =============================================================================
class UserSerializer(serializers.ModelSerializer):
    """
    Serializa información básica de usuarios para mostrar en respuestas.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = fields

# =============================================================================
# SERIALIZER PARA CLIENTES
# =============================================================================
class ClienteSerializer(serializers.ModelSerializer):
    """
    Maneja la conversión de datos de Cliente entre Python y JSON.
    Incluye validación de NIT único.
    """
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['fecha_registro', 'fecha_actualizacion']
    
    def validate_nit(self, value):
        """
        Valida que el NIT sea único al crear o actualizar.
        """
        # Si estamos actualizando, excluimos el cliente actual de la verificación
        if self.instance:
            if Cliente.objects.exclude(pk=self.instance.pk).filter(nit=value).exists():
                raise serializers.ValidationError("Ya existe un cliente con este NIT.")
        else:
            # Si estamos creando, simplemente verificamos existencia
            if Cliente.objects.filter(nit=value).exists():
                raise serializers.ValidationError("Ya existe un cliente con este NIT.")
        return value

# Versión simplificada para listados
class ClienteListSerializer(serializers.ModelSerializer):
    """
    Versión resumida para listados de clientes (mejor rendimiento).
    """
    class Meta:
        model = Cliente
        fields = ['id', 'nombre_empresa', 'nit', 'persona_contacto', 'email', 'tipo_cliente', 'activo']

# =============================================================================
# SERIALIZER PARA ENSAYOS
# =============================================================================
class EnsayoSerializer(serializers.ModelSerializer):
    """
    Serializa los ensayos solicitados para una muestra.
    """
    analista_asignado_info = UserSerializer(source='analista_asignado', read_only=True)
    
    class Meta:
        model = Ensayo
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def validate_fecha_resultados_requerida(self, value):
        """
        Valida que la fecha requerida no sea en el pasado.
        """
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha requerida de resultados no puede estar en el pasado."
            )
        return value

# Versión simplificada para cuando se incluye en Muestra
class EnsayoSimpleSerializer(serializers.ModelSerializer):
    """
    Versión resumida de ensayo para incluir en respuestas de muestra.
    """
    class Meta:
        model = Ensayo
        fields = ['id', 'nombre_analisis', 'norma_metodo', 'prioridad',
                  'estado_ensayo', 'fecha_resultados_requerida']

# =============================================================================
# SERIALIZER PARA HISTORIAL DE ESTADOS
# =============================================================================
class HistorialEstadoSerializer(serializers.ModelSerializer):
    """
    Serializa el historial de cambios de estado de una muestra.
    """
    usuario_info = UserSerializer(source='usuario', read_only=True)
    
    class Meta:
        model = HistorialEstado
        fields = '__all__'
        read_only_fields = ['fecha_cambio']

# =============================================================================
# SERIALIZER PARA MUESTRAS
# =============================================================================
class MuestraSerializer(serializers.ModelSerializer):
    """
    Serializer principal para muestras.
    Incluye toda la información y relaciones.
    """
    # Campos de solo lectura (generados automáticamente)
    codigo_muestra = serializers.CharField(read_only=True)
    fecha_registro = serializers.DateTimeField(read_only=True)
    fecha_recepcion = serializers.DateTimeField(read_only=True)
    
    # Información expandida de relaciones
    cliente_info = ClienteListSerializer(source='cliente', read_only=True)
    usuario_recepcion_info = UserSerializer(source='usuario_recepcion', read_only=True)
    usuario_aceptacion_info = UserSerializer(source='usuario_aceptacion', read_only=True)
    
    # Ensayos asociados
    ensayos = EnsayoSimpleSerializer(many=True, read_only=True)
    
    # Historial de cambios
    historial = HistorialEstadoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Muestra
        fields = '__all__'
    
    def validate_fecha_envio(self, value):
        """
        Valida que la fecha de envío no sea futura.
        """
        if value > timezone.now():
            raise serializers.ValidationError(
                "La fecha de envío no puede ser futura."
            )
        return value
    
    def validate_fecha_muestreo(self, value):
        """
        Valida que la fecha de muestreo no sea futura.
        """
        if value > timezone.now():
            raise serializers.ValidationError(
                "La fecha de muestreo no puede ser futura."
            )
        return value
    
    def validate_cantidad_enviada(self, value):
        """
        Valida que la cantidad sea positiva.
        """
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad enviada debe ser mayor a cero."
            )
        return value
    
    def validate(self, data):
        """
        Validación de nivel de objeto (entre múltiples campos).
        """
        # NUMERAL 6: Validación de cliente autorizado
        cliente = data.get('cliente')
        if cliente and not cliente.activo:
            raise serializers.ValidationError({
                'cliente': 'Este cliente no está autorizado para enviar muestras.'
            })
        
        # Validar que fecha de envío no sea posterior a fecha de muestreo
        fecha_muestreo = data.get('fecha_muestreo')
        fecha_envio = data.get('fecha_envio')
        if fecha_muestreo and fecha_envio:
            if fecha_envio < fecha_muestreo:
                raise serializers.ValidationError({
                    'fecha_envio': 'La fecha de envío no puede ser anterior a la fecha de muestreo.'
                })
        
        return data

# Versión para creación de muestra (sin campos de solo lectura expandidos)
class MuestraCreateSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para crear muestras.
    No incluye información expandida para mejor rendimiento.
    """
    class Meta:
        model = Muestra
        exclude = ['codigo_muestra', 'fecha_registro', 'fecha_recepcion',
                   'fecha_actualizacion', 'muestra_aceptada', 'fecha_aceptacion',
                   'usuario_aceptacion']
    
    def validate(self, data):
        """
        Validaciones al crear muestra.
        """
        # NUMERAL 6: Cliente autorizado
        cliente = data.get('cliente')
        if cliente and not cliente.activo:
            raise serializers.ValidationError({
                'cliente': 'Este cliente no está autorizado para enviar muestras.'
            })
        
        # Validaciones de fechas
        fecha_muestreo = data.get('fecha_muestreo')
        fecha_envio = data.get('fecha_envio')
        
        if fecha_muestreo and fecha_muestreo > timezone.now():
            raise serializers.ValidationError({
                'fecha_muestreo': 'La fecha de muestreo no puede ser futura.'
            })
        
        if fecha_envio and fecha_envio > timezone.now():
            raise serializers.ValidationError({
                'fecha_envio': 'La fecha de envío no puede ser futura.'
            })
        
        if fecha_muestreo and fecha_envio and fecha_envio < fecha_muestreo:
            raise serializers.ValidationError({
                'fecha_envio': 'La fecha de envío no puede ser anterior a la fecha de muestreo.'
            })
        
        return data

# Versión simplificada para listados
class MuestraListSerializer(serializers.ModelSerializer):
    """
    Versión resumida para listados de muestras (mejor rendimiento).
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre_empresa', read_only=True)
    
    class Meta:
        model = Muestra
        fields = ['id', 'codigo_muestra', 'cliente_nombre', 'tipo_muestra',
                  'estado', 'fecha_registro', 'fecha_recepcion', 'muestra_aceptada']

# =============================================================================
# SERIALIZERS PARA ACCIONES ESPECÍFICAS
# =============================================================================

class AceptarMuestraSerializer(serializers.Serializer):
    """
    Serializer para la acción de aceptar una muestra.
    NUMERAL 7: Aceptación y cadena de custodia.
    """
    aceptada = serializers.BooleanField(required=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    
    def validate_aceptada(self, value):
        """
        Solo permitimos marcar como aceptada (True), no rechazar por este endpoint.
        """
        if not value:
            raise serializers.ValidationError(
                "Use el endpoint de actualización de estado para rechazar muestras."
            )
        return value

class ActualizarEstadoSerializer(serializers.Serializer):
    """
    Serializer para actualizar el estado de una muestra.
    Crea automáticamente registro en historial.
    """
    estado = serializers.ChoiceField(choices=Muestra.ESTADO_CHOICES)
    observaciones = serializers.CharField(required=False, allow_blank=True)

class AgregarEnsayoSerializer(serializers.Serializer):
    """
    Serializer para agregar ensayos a una muestra existente.
    NUMERAL 5: Ensayos solicitados.
    """
    ensayos = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        help_text="Lista de ensayos a agregar"
    )
    
    def validate_ensayos(self, value):
        """
        Valida que cada ensayo tenga los campos mínimos requeridos.
        """
        campos_requeridos = ['nombre_analisis', 'fecha_resultados_requerida']
        for i, ensayo in enumerate(value):
            for campo in campos_requeridos:
                if campo not in ensayo:
                    raise serializers.ValidationError(
                        f"El ensayo {i+1} requiere el campo '{campo}'."
                    )
        return value

class ValidacionSuficienciaSerializer(serializers.Serializer):
    """
    NUMERAL 6: Validación automática de cantidad suficiente.
    """
    cantidad_requerida = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate(self, data):
        """
        Compara cantidad enviada vs cantidad requerida.
        """
        muestra = self.context.get('muestra')
        if not muestra:
            raise serializers.ValidationError("No se proporcionó la muestra.")
        
        cantidad_requerida = data['cantidad_requerida']
        if muestra.cantidad_enviada < cantidad_requerida:
            raise serializers.ValidationError({
                'cantidad_insuficiente': f'Se requieren {cantidad_requerida} {muestra.unidad_cantidad}, '
                                        f'pero solo se recibieron {muestra.cantidad_enviada} {muestra.unidad_cantidad}.'
            })
        
        return data
