#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo.
Ejecute: python populate_data.py
"""
import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from reception.models import Cliente, Muestra, Ensayo, HistorialEstado

def create_users():
    """Crear usuarios de ejemplo"""
    print("Creando usuarios...")
    
    # Crear superusuario si no existe
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@laboratorio.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        print("  - Superusuario 'admin' creado (password: admin123)")
    
    # Crear usuarios regulares
    usuarios = [
        {'username': 'recepcion1', 'email': 'recepcion@lab.com', 'first_name': 'María', 'last_name': 'González'},
        {'username': 'analista1', 'email': 'analista1@lab.com', 'first_name': 'Carlos', 'last_name': 'Ramírez'},
        {'username': 'analista2', 'email': 'analista2@lab.com', 'first_name': 'Ana', 'last_name': 'Martínez'},
    ]
    
    for user_data in usuarios:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(
                password='password123',
                **user_data
            )
            print(f"  - Usuario '{user_data['username']}' creado (password: password123)")

def create_clientes():
    """Crear clientes de ejemplo"""
    print("\nCreando clientes...")
    
    clientes_data = [
        {
            'nombre_empresa': 'Farmacéutica ABC S.A.S.',
            'nit': '900123456-7',
            'direccion': 'Carrera 10 #20-30, Piso 5',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'persona_contacto': 'Sofía Hernández',
            'cargo_contacto': 'Jefe de Control de Calidad',
            'email': 'sofia.hernandez@farmabc.com',
            'telefono': '+57 1 234 5678',
            'tipo_cliente': 'RECURRENTE',
            'activo': True
        },
        {
            'nombre_empresa': 'Cosméticos Naturales Ltda.',
            'nit': '800987654-3',
            'direccion': 'Calle 50 #45-67',
            'ciudad': 'Medellín',
            'pais': 'Colombia',
            'persona_contacto': 'Juan Pérez',
            'cargo_contacto': 'Gerente de Producción',
            'email': 'juan.perez@cosmeticosnaturales.com',
            'telefono': '+57 4 567 8901',
            'tipo_cliente': 'NUEVO',
            'activo': True
        },
        {
            'nombre_empresa': 'Alimentos del Valle S.A.',
            'nit': '900555666-1',
            'direccion': 'Zona Industrial Km 5',
            'ciudad': 'Cali',
            'pais': 'Colombia',
            'persona_contacto': 'Laura Gómez',
            'cargo_contacto': 'Directora de Calidad',
            'email': 'laura.gomez@alimentosvalle.com',
            'telefono': '+57 2 345 6789',
            'tipo_cliente': 'RECURRENTE',
            'activo': True
        }
    ]
    
    for cliente_data in clientes_data:
        if not Cliente.objects.filter(nit=cliente_data['nit']).exists():
            Cliente.objects.create(**cliente_data)
            print(f"  - Cliente '{cliente_data['nombre_empresa']}' creado")

def create_muestras():
    """Crear muestras de ejemplo"""
    print("\nCreando muestras...")
    
    usuario_recepcion = User.objects.get(username='recepcion1')
    clientes = Cliente.objects.all()
    
    if not clientes:
        print("  - No hay clientes. Saltando muestras.")
        return
    
    muestras_data = [
        {
            'cliente': clientes[0],
            'tipo_muestra': 'FARMACEUTICO',
            'matriz': 'Tableta',
            'descripcion_muestra': 'Tabletas recubiertas de paracetamol 500mg',
            'cantidad_enviada': Decimal('200.00'),
            'unidad_cantidad': 'unidades',
            'lote': 'PAR-2026-001',
            'fecha_envio': timezone.now() - timedelta(days=2),
            'fecha_muestreo': timezone.now() - timedelta(days=3),
            'responsable_muestreo': 'Técnico de Producción',
            'medio_entrega': 'MENSAJERIA',
            'condiciones_recepcion': 'OPTIMAS',
            'condiciones_almacenamiento': 'AMBIENTE',
            'riesgo_asociado': 'NINGUNO',
            'usuario_recepcion': usuario_recepcion,
            'muestra_aceptada': True,
            'estado': 'ACEPTADA'
        },
        {
            'cliente': clientes[1] if len(clientes) > 1 else clientes[0],
            'tipo_muestra': 'COSMETICO',
            'matriz': 'Crema',
            'descripcion_muestra': 'Crema facial hidratante con extracto de aloe vera',
            'cantidad_enviada': Decimal('500.00'),
            'unidad_cantidad': 'g',
            'lote': 'CREM-2026-045',
            'fecha_envio': timezone.now() - timedelta(days=1),
            'fecha_muestreo': timezone.now() - timedelta(days=1),
            'responsable_muestreo': 'Laura Martínez',
            'medio_entrega': 'PERSONAL',
            'condiciones_recepcion': 'OPTIMAS',
            'condiciones_almacenamiento': 'AMBIENTE',
            'riesgo_asociado': 'BAJO',
            'usuario_recepcion': usuario_recepcion,
            'muestra_aceptada': False,
            'estado': 'REGISTRADA'
        },
        {
            'cliente': clientes[2] if len(clientes) > 2 else clientes[0],
            'tipo_muestra': 'ALIMENTO',
            'matriz': 'Líquido',
            'descripcion_muestra': 'Jugo de naranja pasteurizado',
            'cantidad_enviada': Decimal('1000.00'),
            'unidad_cantidad': 'mL',
            'lote': 'JUG-2026-122',
            'fecha_envio': timezone.now(),
            'fecha_muestreo': timezone.now() - timedelta(hours=6),
            'responsable_muestreo': 'Supervisor de Planta',
            'medio_entrega': 'CORREO',
            'condiciones_recepcion': 'ACEPTABLES',
            'condiciones_almacenamiento': 'REFRIGERACION',
            'riesgo_asociado': 'NINGUNO',
            'usuario_recepcion': usuario_recepcion,
            'muestra_aceptada': True,
            'estado': 'EN_ANALISIS'
        }
    ]
    
    for muestra_data in muestras_data:
        muestra = Muestra.objects.create(**muestra_data)
        print(f"  - Muestra '{muestra.codigo_muestra}' creada")

def create_ensayos():
    """Crear ensayos de ejemplo"""
    print("\nCreando ensayos...")
    
    muestras = Muestra.objects.all()
    if not muestras:
        print("  - No hay muestras. Saltando ensayos.")
        return
    
    analista1 = User.objects.get(username='analista1')
    analista2 = User.objects.get(username='analista2')
    
    ensayos_data = [
        # Ensayos para muestra farmacéutica
        {
            'muestra': muestras[0],
            'nombre_analisis': 'Disolución',
            'norma_metodo': 'USP <711>',
            'prioridad': 'ALTA',
            'fecha_resultados_requerida': timezone.now().date() + timedelta(days=5),
            'estado_ensayo': 'COMPLETADO',
            'analista_asignado': analista1,
            'resultados': 'Q = 85% a los 30 minutos (Especificación: NMT 80% en 30 min). CUMPLE'
        },
        {
            'muestra': muestras[0],
            'nombre_analisis': 'Friabilidad',
            'norma_metodo': 'USP <1216>',
            'prioridad': 'NORMAL',
            'fecha_resultados_requerida': timezone.now().date() + timedelta(days=7),
            'estado_ensayo': 'EN_PROCESO',
            'analista_asignado': analista2
        },
        # Ensayos para muestra cosmético
        {
            'muestra': muestras[1] if len(muestras) > 1 else muestras[0],
            'nombre_analisis': 'pH',
            'norma_metodo': 'USP <791>',
            'prioridad': 'ALTA',
            'fecha_resultados_requerida': timezone.now().date() + timedelta(days=3),
            'estado_ensayo': 'PENDIENTE',
            'analista_asignado': None
        },
        # Ensayos para muestra de alimento
        {
            'muestra': muestras[2] if len(muestras) > 2 else muestras[0],
            'nombre_analisis': 'Microbiología - Recuento de mesofílicos',
            'norma_metodo': 'NTC 4519',
            'prioridad': 'URGENTE',
            'fecha_resultados_requerida': timezone.now().date() + timedelta(days=2),
            'estado_ensayo': 'EN_PROCESO',
            'analista_asignado': analista1
        }
    ]
    
    for ensayo_data in ensayos_data:
        Ensayo.objects.create(**ensayo_data)
        print(f"  - Ensayo '{ensayo_data['nombre_analisis']}' creado")

def main():
    print("="*60)
    print("POBLANDO BASE DE DATOS CON DATOS DE EJEMPLO")
    print("="*60)
    
    create_users()
    create_clientes()
    create_muestras()
    create_ensayos()
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print("\nCredenciales de acceso:")
    print("  - Admin: username=admin, password=admin123")
    print("  - Otros usuarios: password=password123")
    print("\nInicia el servidor con: python manage.py runserver")
    print("Accede al panel admin en: http://localhost:8000/admin/")
    print("Accede a la API en: http://localhost:8000/api/")

if __name__ == '__main__':
    main()
