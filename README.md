# LIMS - Sistema de Recepción de Muestras de Laboratorio

Sistema de información para la gestión y recepción de muestras en laboratorios de control de calidad. Cumple con los requisitos de trazabilidad y documentación de ISO/IEC 17025.

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración Inicial](#configuración-inicial)
- [Ejecución](#ejecución)
- [Uso de la API](#uso-de-la-api)
- [Panel de Administración](#panel-de-administración)
- [Estructura del Proyecto](#estructura-del-proyecto)

---

## 🔧 Requisitos

- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)

### Verificar instalación de Python:

```bash
python --version
# o
python3 --version
```

Si no tienes Python instalado, descárgalo desde: https://www.python.org/downloads/

---

## 📥 Instalación

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/Kailo26A/LIMS_LAB_SMGH.git
cd LIMS_LAB_SMGH
```

### Paso 2: Crear entorno virtual (RECOMENDADO)

Un entorno virtual aísla las dependencias del proyecto.

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu terminal.

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- Django 5.0
- Django REST Framework
- django-cors-headers
- Pillow

**⏱️ Esto puede tomar 2-3 minutos**

---

## ⚙️ Configuración Inicial

### Paso 1: Crear la base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

**¿Qué hace esto?**
- `makemigrations`: Detecta cambios en los modelos y crea "instrucciones" de migración
- `migrate`: Aplica esas instrucciones y crea las tablas en la base de datos

### Paso 2: Crear usuario administrador

```bash
python manage.py createsuperuser
```

Te pedirá:
- **Username**: Tu nombre de usuario (ej: admin)
- **Email**: Tu correo electrónico
- **Password**: Tu contraseña (NO se mostrará al escribir)

**Ejemplo:**
```
Username: admin
Email address: admin@laboratorio.com
Password: ********
Password (again): ********
Superuser created successfully.
```

### Paso 3: (Opcional) Poblar base de datos con datos de ejemplo

```bash
python populate_data.py
```

Esto creará:
- Usuarios de ejemplo (admin, recepcion1, analista1, analista2)
- 3 clientes de ejemplo
- 3 muestras de ejemplo
- Varios ensayos

---

## 🚀 Ejecución

### Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

Verás algo como:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
February 03, 2026 - 10:30:00
Django version 5.0, using settings 'lims_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**El servidor está corriendo en:** `http://localhost:8000`

---

## 🌐 Uso de la API

### Acceder a la API en el navegador

Abre tu navegador y ve a:

```
http://localhost:8000/api/
```

Verás la interfaz web de Django REST Framework (DRF Browsable API).

### Endpoints principales

#### **Clientes**
- `GET /api/clientes/` - Listar todos los clientes
- `POST /api/clientes/` - Crear nuevo cliente
- `GET /api/clientes/{id}/` - Ver cliente específico
- `PUT /api/clientes/{id}/` - Actualizar cliente
- `DELETE /api/clientes/{id}/` - Eliminar cliente

#### **Muestras**
- `GET /api/muestras/` - Listar todas las muestras
- `POST /api/muestras/` - Crear nueva muestra
- `GET /api/muestras/{id}/` - Ver muestra específica
- `POST /api/muestras/{id}/aceptar/` - Aceptar muestra
- `POST /api/muestras/{id}/actualizar_estado/` - Cambiar estado
- `GET /api/muestras/{id}/ensayos/` - Ver ensayos de una muestra
- `POST /api/muestras/{id}/agregar_ensayos/` - Agregar ensayos
- `GET /api/muestras/{id}/historial/` - Ver historial de cambios

#### **Ensayos**
- `GET /api/ensayos/` - Listar todos los ensayos
- `POST /api/ensayos/` - Crear nuevo ensayo
- `GET /api/ensayos/{id}/` - Ver ensayo específico
- `POST /api/ensayos/{id}/asignar_analista/` - Asignar analista
- `POST /api/ensayos/{id}/registrar_resultados/` - Registrar resultados

Para más ejemplos detallados, consulta el archivo [EJEMPLOS_API.md](EJEMPLOS_API.md)

---

## 👨‍💼 Panel de Administración

El panel de administración de Django te permite gestionar datos de forma visual.

### Acceder al panel

1. Asegúrate de que el servidor está corriendo
2. Ve a: `http://localhost:8000/admin/`
3. Inicia sesión con las credenciales del superusuario que creaste

### ¿Qué puedes hacer?

- ✅ Ver, crear, editar y eliminar clientes
- ✅ Gestionar muestras
- ✅ Administrar ensayos
- ✅ Ver historial completo de cambios
- ✅ Filtrar y buscar registros
- ✅ Exportar datos
- ✅ Acciones masivas (marcar múltiples muestras como aceptadas, etc.)

---

## 📁 Estructura del Proyecto

```
LIMS_LAB_SMGH/
│
├── manage.py                      # Comando principal de Django
├── requirements.txt               # Dependencias
├── README.md                      # Este archivo
├── EJEMPLOS_API.md                # Ejemplos detallados de uso de la API
├── populate_data.py               # Script para datos de ejemplo
├── .gitignore                     # Archivos ignorados por Git
├── db.sqlite3                     # Base de datos (se crea automáticamente)
│
├── lims_project/                  # Configuración del proyecto
│   ├── __init__.py
│   ├── settings.py               # Configuración general
│   ├── urls.py                   # URLs principales
│   └── wsgi.py                   # Para despliegue
│
└── reception/                     # Aplicación de recepción
    ├── __init__.py
    ├── models.py                 # Modelos de datos (BD)
    ├── serializers.py            # Conversión Python ↔ JSON
    ├── views.py                  # Lógica de negocio
    ├── urls.py                   # URLs de la API
    ├── admin.py                  # Configuración del panel admin
    ├── apps.py                   # Configuración de la app
    └── migrations/               # Historial de cambios en BD
        ├── __init__.py
        └── 0001_initial.py
```

---

## 📊 Funcionalidades Implementadas

### ✅ Numeral 1: Identificación General
- Código único automático (LIMS-YYYYMMDD-UUID)
- Fecha/hora de registro automático
- Estado de la muestra con historial completo
- Versión de plataforma
- Usuario responsable de recepción

### ✅ Numeral 2: Información del Cliente
- Gestión completa de clientes
- Clasificación (nuevo/recurrente)
- Validación de clientes autorizados
- Información de contacto completa

### ✅ Numeral 3: Envío y Recepción
- Fechas de envío y recepción
- Medio de entrega
- Condiciones de recepción
- Observaciones

### ✅ Numeral 4: Información de la Muestra
- Tipos y matrices predefinidos
- Cantidad y unidades
- Lote y trazabilidad
- Condiciones de almacenamiento
- Evaluación de riesgos

### ✅ Numeral 5: Ensayos Solicitados
- Gestión de múltiples ensayos por muestra
- Priorización
- Asignación de analistas
- Registro de resultados
- Seguimiento de plazos

### ✅ Numeral 6: Validaciones Automáticas
- Cantidad suficiente para análisis
- Cliente autorizado
- Fechas coherentes
- Unicidad de códigos

### ✅ Numeral 7: Aceptación y Cadena de Custodia
- Confirmación formal de aceptación
- Historial completo de cambios
- Trazabilidad de usuarios
- Timestamps en todos los cambios

---

## 🔐 Seguridad y Producción

**⚠️ IMPORTANTE:** Este proyecto está configurado para desarrollo. Para producción:

1. **Cambiar SECRET_KEY** en `settings.py`
2. **Establecer DEBUG = False**
3. **Configurar ALLOWED_HOSTS** con tu dominio
4. **Habilitar autenticación:**
   ```python
   # En settings.py
   REST_FRAMEWORK = {
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ]
   }
   ```
5. **Usar base de datos robusta** (PostgreSQL o MySQL en vez de SQLite)
6. **Configurar HTTPS**
7. **Implementar respaldos automáticos**

---

## 🆘 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'django'"

**Solución:** Asegúrate de haber activado el entorno virtual y haber ejecutado `pip install -r requirements.txt`

### Error: "CSRF verification failed"

**Solución:** Si usas la API desde otra aplicación, asegúrate de incluir el token CSRF o deshabilitarlo temporalmente para pruebas.

### Error: "port is already in use"

**Solución:** Usa otro puerto: `python manage.py runserver 8001`

### No puedo ver los cambios en la base de datos

**Solución:** Ejecuta migraciones: `python manage.py makemigrations` y `python manage.py migrate`

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisa la documentación de Django: https://docs.djangoproject.com/
2. Revisa la documentación de DRF: https://www.django-rest-framework.org/
3. Consulta el archivo [EJEMPLOS_API.md](EJEMPLOS_API.md) para ejemplos prácticos

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 👤 Autor

Desarrollado por [Juan C. Arias Sanchez](https://github.com/Kailo26A)

---

**¡Listo para usar! 🎉**

Ejecuta `python manage.py runserver` y comienza a gestionar tus muestras.
