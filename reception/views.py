from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from django.db import models
from .models import Cliente, Muestra, Ensayo, HistorialEstado
from .serializers import (
    ClienteSerializer, ClienteListSerializer,
    MuestraSerializer, MuestraCreateSerializer, MuestraListSerializer,
    EnsayoSerializer, HistorialEstadoSerializer,
    AceptarMuestraSerializer, ActualizarEstadoSerializer,
    AgregarEnsayoSerializer, ValidacionSuficienciaSerializer
)

# =============================================================================
# VIEWSET PARA CLIENTES (NUMERAL 2)
# =============================================================================
class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de clientes.
    Endpoints generados automáticamente:
    - GET /api/clientes/ → Listar todos los clientes
    - POST /api/clientes/ → Crear nuevo cliente
    - GET /api/clientes/{id}/ → Ver detalle de un cliente
    - PUT /api/clientes/{id}/ → Actualizar cliente completo
    - PATCH /api/clientes/{id}/ → Actualizar cliente parcial
    - DELETE /api/clientes/{id}/ → Eliminar cliente
    """
    queryset = Cliente.objects.all()
    
    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == 'list':
            return ClienteListSerializer
        return ClienteSerializer
    
    def get_queryset(self):
        """
        Permite filtrar clientes según parámetros de URL.
        Ejemplos:
        - /api/clientes/?activo=true
        - /api/clientes/?tipo_cliente=RECURRENTE
        """
        queryset = Cliente.objects.all()
        
        # Filtro por activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        # Filtro por tipo de cliente
        tipo_cliente = self.request.query_params.get('tipo_cliente', None)
        if tipo_cliente:
            queryset = queryset.filter(tipo_cliente=tipo_cliente)
        
        # Búsqueda por nombre o NIT
        busqueda = self.request.query_params.get('buscar', None)
        if busqueda:
            queryset = queryset.filter(
                models.Q(nombre_empresa__icontains=busqueda) |
                models.Q(nit__icontains=busqueda)
            )
        
        return queryset.order_by('nombre_empresa')
    
    @action(detail=True, methods=['get'])
    def muestras(self, request, pk=None):
        """
        Endpoint personalizado: GET /api/clientes/{id}/muestras/
        Retorna todas las muestras de un cliente específico.
        """
        cliente = self.get_object()
        muestras = cliente.muestras.all()
        serializer = MuestraListSerializer(muestras, many=True)
        return Response(serializer.data)

# =============================================================================
# VIEWSET PARA MUESTRAS (NUMERALES 1, 3, 4, 7)
# =============================================================================
class MuestraViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de muestras.
    Implementa todos los numerales del PDF.
    """
    queryset = Muestra.objects.all()
    
    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == 'create':
            return MuestraCreateSerializer
        elif self.action == 'list':
            return MuestraListSerializer
        return MuestraSerializer
    
    def get_queryset(self):
        """
        Permite filtrar muestras según parámetros de URL.
        Ejemplos:
        - /api/muestras/?estado=REGISTRADA
        - /api/muestras/?cliente=1
        - /api/muestras/?tipo_muestra=FARMACEUTICO
        - /api/muestras/?fecha_desde=2024-01-01&fecha_hasta=2024-12-31
        - /api/muestras/?aceptada=true
        """
        queryset = Muestra.objects.select_related('cliente', 'usuario_recepcion').all()
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por cliente
        cliente = self.request.query_params.get('cliente', None)
        if cliente:
            queryset = queryset.filter(cliente_id=cliente)
        
        # Filtro por tipo de muestra
        tipo_muestra = self.request.query_params.get('tipo_muestra', None)
        if tipo_muestra:
            queryset = queryset.filter(tipo_muestra=tipo_muestra)
        
        # Filtro por aceptada
        aceptada = self.request.query_params.get('aceptada', None)
        if aceptada is not None:
            queryset = queryset.filter(muestra_aceptada=aceptada.lower() == 'true')
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            queryset = queryset.filter(fecha_registro__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_registro__lte=fecha_hasta)
        
        # Búsqueda por código
        codigo = self.request.query_params.get('codigo', None)
        if codigo:
            queryset = queryset.filter(codigo_muestra__icontains=codigo)
        
        return queryset.order_by('-fecha_registro')
    
    def perform_create(self, serializer):
        """
        Se ejecuta al crear una muestra.
        Asigna automáticamente el usuario que registra.
        """
        serializer.save(usuario_recepcion=self.request.user)
    
    # -------------------------------------------------------------------------
    # NUMERAL 7: ACEPTACIÓN DE MUESTRA
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        """
        Endpoint personalizado: POST /api/muestras/{id}/aceptar/
        Acepta formalmente una muestra y activa su cadena de custodia.
        Payload:
        {
            "aceptada": true,
            "observaciones": "Muestra en condiciones óptimas"
        }
        """
        muestra = self.get_object()
        serializer = AceptarMuestraSerializer(data=request.data)
        
        if serializer.is_valid():
            if muestra.muestra_aceptada:
                return Response(
                    {'error': 'Esta muestra ya fue aceptada previamente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar transacción para garantizar atomicidad
            with transaction.atomic():
                estado_anterior = muestra.estado
                
                # Actualizar muestra
                muestra.muestra_aceptada = True
                muestra.fecha_aceptacion = timezone.now()
                muestra.usuario_aceptacion = request.user
                muestra.estado = 'ACEPTADA'
                muestra.save()
                
                # Crear registro en historial
                HistorialEstado.objects.create(
                    muestra=muestra,
                    estado_anterior=estado_anterior,
                    estado_nuevo='ACEPTADA',
                    usuario=request.user,
                    observaciones=serializer.validated_data.get('observaciones',
                                                                'Muestra aceptada formalmente')
                )
            
            return Response({
                'mensaje': 'Muestra aceptada exitosamente',
                'codigo_muestra': muestra.codigo_muestra,
                'fecha_aceptacion': muestra.fecha_aceptacion
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # -------------------------------------------------------------------------
    # NUMERAL 7: ACTUALIZACIÓN DE ESTADO CON HISTORIAL
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['post'])
    def actualizar_estado(self, request, pk=None):
        """
        Endpoint personalizado: POST /api/muestras/{id}/actualizar_estado/
        Cambia el estado de una muestra y registra en historial.
        Payload:
        {
            "estado": "EN_ANALISIS",
            "observaciones": "Iniciando análisis de pH"
        }
        """
        muestra = self.get_object()
        serializer = ActualizarEstadoSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                estado_anterior = muestra.estado
                nuevo_estado = serializer.validated_data['estado']
                
                # Validar transición de estado
                if nuevo_estado == 'ACEPTADA' and not muestra.muestra_aceptada:
                    return Response(
                        {'error': 'Use el endpoint /aceptar/ para aceptar muestras.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Actualizar estado
                muestra.estado = nuevo_estado
                muestra.save()
                
                # Registrar en historial
                HistorialEstado.objects.create(
                    muestra=muestra,
                    estado_anterior=estado_anterior,
                    estado_nuevo=nuevo_estado,
                    usuario=request.user,
                    observaciones=serializer.validated_data.get('observaciones', '')
                )
            
            return Response({
                'mensaje': 'Estado actualizado exitosamente',
                'estado_anterior': estado_anterior,
                'estado_nuevo': nuevo_estado
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # -------------------------------------------------------------------------
    # NUMERAL 5: ENSAYOS
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['get'])
    def ensayos(self, request, pk=None):
        """
        Endpoint: GET /api/muestras/{id}/ensayos/
        Retorna todos los ensayos de una muestra.
        """
        muestra = self.get_object()
        ensayos = muestra.ensayos.all()
        serializer = EnsayoSerializer(ensayos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_ensayos(self, request, pk=None):
        """
        Endpoint: POST /api/muestras/{id}/agregar_ensayos/
        Agrega uno o más ensayos a una muestra existente.
        Payload:
        {
            "ensayos": [
                {
                    "nombre_analisis": "pH",
                    "norma_metodo": "USP <791>",
                    "prioridad": "ALTA",
                    "fecha_resultados_requerida": "2024-03-01"
                },
                {
                    "nombre_analisis": "Viscosidad",
                    "prioridad": "NORMAL",
                    "fecha_resultados_requerida": "2024-03-05"
                }
            ]
        }
        """
        muestra = self.get_object()
        serializer = AgregarEnsayoSerializer(data=request.data)
        
        if serializer.is_valid():
            ensayos_creados = []
            with transaction.atomic():
                for ensayo_data in serializer.validated_data['ensayos']:
                    ensayo_data['muestra'] = muestra.id
                    ensayo_serializer = EnsayoSerializer(data=ensayo_data)
                    if ensayo_serializer.is_valid():
                        ensayo = ensayo_serializer.save()
                        ensayos_creados.append(ensayo)
                    else:
                        return Response(
                            {'error': f'Error en ensayo: {ensayo_serializer.errors}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            return Response({
                'mensaje': f'{len(ensayos_creados)} ensayo(s) agregado(s) exitosamente',
                'ensayos': EnsayoSerializer(ensayos_creados, many=True).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # -------------------------------------------------------------------------
    # NUMERAL 6: VALIDACIÓN DE SUFICIENCIA
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['post'])
    def validar_suficiencia(self, request, pk=None):
        """
        Endpoint: POST /api/muestras/{id}/validar_suficiencia/
        Valida si la cantidad enviada es suficiente para los análisis.
        Payload:
        {
            "cantidad_requerida": 250.50
        }
        """
        muestra = self.get_object()
        serializer = ValidacionSuficienciaSerializer(
            data=request.data,
            context={'muestra': muestra}
        )
        
        if serializer.is_valid():
            return Response({
                'suficiente': True,
                'cantidad_enviada': float(muestra.cantidad_enviada),
                'cantidad_requerida': float(serializer.validated_data['cantidad_requerida']),
                'unidad': muestra.unidad_cantidad,
                'mensaje': 'La cantidad es suficiente para el análisis'
            })
        
        # Si la validación falla, retornar detalles
        return Response({
            'suficiente': False,
            'cantidad_enviada': float(muestra.cantidad_enviada),
            'cantidad_requerida': float(request.data.get('cantidad_requerida', 0)),
            'unidad': muestra.unidad_cantidad,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # -------------------------------------------------------------------------
    # NUMERAL 7: HISTORIAL COMPLETO
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """
        Endpoint: GET /api/muestras/{id}/historial/
        Retorna todo el historial de cambios de estado de una muestra.
        """
        muestra = self.get_object()
        historial = muestra.historial.all()
        serializer = HistorialEstadoSerializer(historial, many=True)
        return Response(serializer.data)

# =============================================================================
# VIEWSET PARA ENSAYOS (NUMERAL 5)
# =============================================================================
class EnsayoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de ensayos individuales.
    """
    queryset = Ensayo.objects.all()
    serializer_class = EnsayoSerializer
    
    def get_queryset(self):
        """
        Permite filtrar ensayos.
        Ejemplos:
        - /api/ensayos/?estado_ensayo=PENDIENTE
        - /api/ensayos/?prioridad=URGENTE
        - /api/ensayos/?muestra=1
        """
        queryset = Ensayo.objects.select_related('muestra', 'analista_asignado').all()
        
        # Filtro por estado
        estado = self.request.query_params.get('estado_ensayo', None)
        if estado:
            queryset = queryset.filter(estado_ensayo=estado)
        
        # Filtro por prioridad
        prioridad = self.request.query_params.get('prioridad', None)
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)
        
        # Filtro por muestra
        muestra = self.request.query_params.get('muestra', None)
        if muestra:
            queryset = queryset.filter(muestra_id=muestra)
        
        # Filtro por analista
        analista = self.request.query_params.get('analista', None)
        if analista:
            queryset = queryset.filter(analista_asignado_id=analista)
        
        return queryset.order_by('prioridad', 'fecha_resultados_requerida')
    
    @action(detail=True, methods=['post'])
    def asignar_analista(self, request, pk=None):
        """
        Endpoint: POST /api/ensayos/{id}/asignar_analista/
        Asigna un analista a un ensayo.
        Payload:
        {
            "analista_id": 2
        }
        """
        ensayo = self.get_object()
        analista_id = request.data.get('analista_id')
        
        if not analista_id:
            return Response(
                {'error': 'Debe proporcionar analista_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth.models import User
            analista = User.objects.get(id=analista_id)
            ensayo.analista_asignado = analista
            ensayo.save()
            
            return Response({
                'mensaje': 'Analista asignado exitosamente',
                'analista': analista.username
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'Analista no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def registrar_resultados(self, request, pk=None):
        """
        Endpoint: POST /api/ensayos/{id}/registrar_resultados/
        Registra los resultados de un ensayo.
        Payload:
        {
            "resultados": "pH: 7.2, Viscosidad: 1500 cPs",
            "observaciones": "Ensayo realizado según USP <791>"
        }
        """
        ensayo = self.get_object()
        resultados = request.data.get('resultados')
        observaciones = request.data.get('observaciones', '')
        
        if not resultados:
            return Response(
                {'error': 'Debe proporcionar los resultados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ensayo.resultados = resultados
        ensayo.observaciones_ensayo = observaciones
        ensayo.estado_ensayo = 'COMPLETADO'
        ensayo.fecha_finalizacion = timezone.now()
        ensayo.save()
        
        return Response({
            'mensaje': 'Resultados registrados exitosamente',
            'ensayo': EnsayoSerializer(ensayo).data
        })

# =============================================================================
# VIEWSET PARA HISTORIAL (Solo lectura)
# =============================================================================
class HistorialEstadoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para historial de estados.
    No permite crear/actualizar/eliminar directamente.
    """
    queryset = HistorialEstado.objects.all()
    serializer_class = HistorialEstadoSerializer
    
    def get_queryset(self):
        """
        Permite filtrar historial por muestra.
        Ejemplo:
        - /api/historial/?muestra=1
        """
        queryset = HistorialEstado.objects.select_related('muestra', 'usuario').all()
        
        muestra = self.request.query_params.get('muestra', None)
        if muestra:
            queryset = queryset.filter(muestra_id=muestra)
        
        return queryset.order_by('-fecha_cambio')
