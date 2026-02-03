# Ejemplos de Uso de la API LIMS

Esta guía proporciona ejemplos prácticos de cómo usar cada endpoint de la API.

## 🔧 Configuración Inicial

### Asegúrate de que el servidor esté corriendo:

```bash
python manage.py runserver
```

La API estará disponible en: `http://localhost:8000/api/`

### Autenticación

Para desarrollo, la autenticación está deshabilitada. En producción, necesitarás incluir tokens de autenticación en tus peticiones.

---

## 👥 Clientes (NUMERAL 2)

### 1. Crear un nuevo cliente

```bash
curl -X POST http://localhost:8000/api/clientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_empresa": "Laboratorios Innovación S.A.S.",
    "nit": "900800700-6",
    "direccion": "Avenida 68 #45-23, Oficina 301",
    "ciudad": "Bogotá",
    "pais": "Colombia",
    "persona_contacto": "María Isabel Torres",
    "cargo_contacto": "Gerente de Calidad",
    "email": "maria.torres@innovacion.com",
    "telefono": "+57 1 456 7890",
    "tipo_cliente": "NUEVO",
    "activo": true
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "nombre_empresa": "Laboratorios Innovación S.A.S.",
  "nit": "900800700-6",
  "direccion": "Avenida 68 #45-23, Oficina 301",
  "ciudad": "Bogotá",
  "pais": "Colombia",
  "persona_contacto": "María Isabel Torres",
  "cargo_contacto": "Gerente de Calidad",
  "email": "maria.torres@innovacion.com",
  "telefono": "+57 1 456 7890",
  "tipo_cliente": "NUEVO",
  "activo": true,
  "fecha_registro": "2026-02-03T10:30:00-05:00",
  "fecha_actualizacion": "2026-02-03T10:30:00-05:00"
}
```

### 2. Listar todos los clientes

```bash
curl http://localhost:8000/api/clientes/
```

### 3. Buscar clientes por nombre o NIT

```bash
curl "http://localhost:8000/api/clientes/?buscar=Innovación"
```

### 4. Filtrar clientes activos

```bash
curl "http://localhost:8000/api/clientes/?activo=true"
```

### 5. Ver un cliente específico

```bash
curl http://localhost:8000/api/clientes/1/
```

### 6. Actualizar un cliente

```bash
curl -X PATCH http://localhost:8000/api/clientes/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_cliente": "RECURRENTE",
    "telefono": "+57 1 456 7899"
  }'
```

### 7. Ver todas las muestras de un cliente

```bash
curl http://localhost:8000/api/clientes/1/muestras/
```

---

## 🧪 Muestras (NUMERALES 1, 3, 4, 7)

### 1. Crear una nueva muestra

```bash
curl -X POST http://localhost:8000/api/muestras/ \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": 1,
    "tipo_muestra": "FARMACEUTICO",
    "matriz": "Cápsula",
    "descripcion_muestra": "Cápsulas de paracetamol 500mg, lote PAR-2026-045",
    "cantidad_enviada": "150.00",
    "unidad_cantidad": "unidades",
    "lote": "PAR-2026-045",
    "fecha_envio": "2026-02-02T08:00:00-05:00",
    "fecha_muestreo": "2026-02-01T14:30:00-05:00",
    "responsable_muestreo": "Técnico de Producción",
    "medio_entrega": "MENSAJERIA",
    "condiciones_recepcion": "OPTIMAS",
    "condiciones_almacenamiento": "AMBIENTE",
    "riesgo_asociado": "NINGUNO",
    "observaciones_recepcion": "Muestra recibida en perfecto estado, empaque intacto"
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "codigo_muestra": "LIMS-20260203-A3F4B8C1",
  "cliente": 1,
  "tipo_muestra": "FARMACEUTICO",
  "matriz": "Cápsula",
  "estado": "REGISTRADA",
  "muestra_aceptada": false,
  "fecha_registro": "2026-02-03T10:45:00-05:00",
  ...
}
```

### 2. Listar todas las muestras

```bash
curl http://localhost:8000/api/muestras/
```

### 3. Filtrar muestras por estado

```bash
curl "http://localhost:8000/api/muestras/?estado=REGISTRADA"
```

### 4. Filtrar muestras por rango de fechas

```bash
curl "http://localhost:8000/api/muestras/?fecha_desde=2026-02-01&fecha_hasta=2026-02-03"
```

### 5. Buscar muestra por código

```bash
curl "http://localhost:8000/api/muestras/?codigo=LIMS-20260203"
```

### 6. Ver detalle completo de una muestra

```bash
curl http://localhost:8000/api/muestras/1/
```

### 7. Aceptar una muestra (NUMERAL 7: Aceptación y Cadena de Custodia)

```bash
curl -X POST http://localhost:8000/api/muestras/1/aceptar/ \
  -H "Content-Type: application/json" \
  -d '{
    "aceptada": true,
    "observaciones": "Muestra verificada y aceptada. Todas las condiciones conformes."
  }'
```

**Respuesta:**
```json
{
  "mensaje": "Muestra aceptada exitosamente",
  "codigo_muestra": "LIMS-20260203-A3F4B8C1",
  "fecha_aceptacion": "2026-02-03T11:00:00-05:00"
}
```

### 8. Cambiar estado de una muestra

```bash
curl -X POST http://localhost:8000/api/muestras/1/actualizar_estado/ \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "EN_ANALISIS",
    "observaciones": "Muestra enviada al área de análisis"
  }'
```

### 9. Validar suficiencia de cantidad (NUMERAL 6)

```bash
curl -X POST http://localhost:8000/api/muestras/1/validar_suficiencia/ \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad_requerida": 100.00
  }'
```

**Respuesta si es suficiente:**
```json
{
  "suficiente": true,
  "cantidad_enviada": 150.0,
  "cantidad_requerida": 100.0,
  "unidad": "unidades",
  "mensaje": "La cantidad es suficiente para el análisis"
}
```

**Respuesta si NO es suficiente:**
```json
{
  "suficiente": false,
  "cantidad_enviada": 150.0,
  "cantidad_requerida": 200.0,
  "unidad": "unidades",
  "error": {
    "cantidad_insuficiente": "Se requieren 200.0 unidades, pero solo se recibieron 150.0 unidades."
  }
}
```

### 10. Ver historial completo de cambios de una muestra (NUMERAL 7: Trazabilidad)

```bash
curl http://localhost:8000/api/muestras/1/historial/
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "muestra": 1,
    "estado_anterior": "REGISTRADA",
    "estado_nuevo": "ACEPTADA",
    "usuario": 1,
    "usuario_info": {
      "id": 1,
      "username": "recepcion1",
      "first_name": "María",
      "last_name": "González",
      "email": "recepcion@lab.com"
    },
    "fecha_cambio": "2026-02-03T11:00:00-05:00",
    "observaciones": "Muestra verificada y aceptada. Todas las condiciones conformes."
  },
  {
    "id": 2,
    "muestra": 1,
    "estado_anterior": "ACEPTADA",
    "estado_nuevo": "EN_ANALISIS",
    "usuario": 2,
    "usuario_info": {
      "id": 2,
      "username": "analista1",
      "first_name": "Carlos",
      "last_name": "Ramírez",
      "email": "analista1@lab.com"
    },
    "fecha_cambio": "2026-02-03T11:15:00-05:00",
    "observaciones": "Muestra enviada al área de análisis"
  }
]
```

---

## 🧪 Ensayos (NUMERAL 5)

### 1. Ver todos los ensayos de una muestra

```bash
curl http://localhost:8000/api/muestras/1/ensayos/
```

### 2. Agregar ensayos a una muestra

```bash
curl -X POST http://localhost:8000/api/muestras/1/agregar_ensayos/ \
  -H "Content-Type: application/json" \
  -d '{
    "ensayos": [
      {
        "nombre_analisis": "Disolución",
        "norma_metodo": "USP <711>",
        "prioridad": "ALTA",
        "fecha_resultados_requerida": "2026-02-10"
      },
      {
        "nombre_analisis": "Uniformidad de contenido",
        "norma_metodo": "USP <905>",
        "prioridad": "NORMAL",
        "fecha_resultados_requerida": "2026-02-12"
      }
    ]
  }'
```

**Respuesta:**
```json
{
  "mensaje": "2 ensayo(s) agregado(s) exitosamente",
  "ensayos": [
    {
      "id": 1,
      "muestra": 1,
      "nombre_analisis": "Disolución",
      "norma_metodo": "USP <711>",
      "prioridad": "ALTA",
      "estado_ensayo": "PENDIENTE",
      "fecha_resultados_requerida": "2026-02-10",
      "analista_asignado": null
    },
    {
      "id": 2,
      "muestra": 1,
      "nombre_analisis": "Uniformidad de contenido",
      "norma_metodo": "USP <905>",
      "prioridad": "NORMAL",
      "estado_ensayo": "PENDIENTE",
      "fecha_resultados_requerida": "2026-02-12",
      "analista_asignado": null
    }
  ]
}
```

### 3. Listar todos los ensayos

```bash
curl http://localhost:8000/api/ensayos/
```

### 4. Filtrar ensayos pendientes

```bash
curl "http://localhost:8000/api/ensayos/?estado_ensayo=PENDIENTE"
```

### 5. Filtrar ensayos por prioridad

```bash
curl "http://localhost:8000/api/ensayos/?prioridad=URGENTE"
```

### 6. Asignar analista a un ensayo

```bash
curl -X POST http://localhost:8000/api/ensayos/1/asignar_analista/ \
  -H "Content-Type: application/json" \
  -d '{
    "analista_id": 2
  }'
```

**Respuesta:**
```json
{
  "mensaje": "Analista asignado exitosamente",
  "analista": "analista1"
}
```

### 7. Registrar resultados de un ensayo

```bash
curl -X POST http://localhost:8000/api/ensayos/1/registrar_resultados/ \
  -H "Content-Type: application/json" \
  -d '{
    "resultados": "Q = 87% a los 30 minutos. Especificación: NMT 80% en 30 min. CUMPLE",
    "observaciones": "Ensayo realizado según procedimiento PNT-QC-001. Equipo: Disolutor Hanson SR8-Plus"
  }'
```

**Respuesta:**
```json
{
  "mensaje": "Resultados registrados exitosamente",
  "ensayo": {
    "id": 1,
    "muestra": 1,
    "nombre_analisis": "Disolución",
    "norma_metodo": "USP <711>",
    "prioridad": "ALTA",
    "estado_ensayo": "COMPLETADO",
    "fecha_resultados_requerida": "2026-02-10",
    "analista_asignado": 2,
    "fecha_inicio": null,
    "fecha_finalizacion": "2026-02-03T14:30:00-05:00",
    "resultados": "Q = 87% a los 30 minutos. Especificación: NMT 80% en 30 min. CUMPLE",
    "observaciones_ensayo": "Ensayo realizado según procedimiento PNT-QC-001. Equipo: Disolutor Hanson SR8-Plus"
  }
}
```

---

## 📈 Historial (NUMERAL 7: Trazabilidad Completa)

### 1. Ver todo el historial del sistema

```bash
curl http://localhost:8000/api/historial/
```

### 2. Filtrar historial por muestra específica

```bash
curl "http://localhost:8000/api/historial/?muestra=1"
```

---

## 🔍 Ejemplos de Flujo Completo

### Flujo 1: Recepción completa de una muestra

```bash
# 1. Crear cliente (si no existe)
curl -X POST http://localhost:8000/api/clientes/ \
  -H "Content-Type: application/json" \
  -d '{...datos del cliente...}'

# 2. Registrar muestra
curl -X POST http://localhost:8000/api/muestras/ \
  -H "Content-Type: application/json" \
  -d '{...datos de la muestra...}'

# 3. Validar cantidad suficiente
curl -X POST http://localhost:8000/api/muestras/1/validar_suficiencia/ \
  -H "Content-Type: application/json" \
  -d '{"cantidad_requerida": 100.00}'

# 4. Aceptar muestra
curl -X POST http://localhost:8000/api/muestras/1/aceptar/ \
  -H "Content-Type: application/json" \
  -d '{"aceptada": true, "observaciones": "Muestra conforme"}'

# 5. Agregar ensayos
curl -X POST http://localhost:8000/api/muestras/1/agregar_ensayos/ \
  -H "Content-Type: application/json" \
  -d '{"ensayos": [{...}, {...}]}'

# 6. Cambiar estado a EN_ANALISIS
curl -X POST http://localhost:8000/api/muestras/1/actualizar_estado/ \
  -H "Content-Type: application/json" \
  -d '{"estado": "EN_ANALISIS", "observaciones": "Iniciando análisis"}'
```

---

## 🖥️ Usando el Navegador Web (DRF Browsable API)

También puedes usar la interfaz web interactiva de Django REST Framework:

1. Abre tu navegador
2. Ve a: `http://localhost:8000/api/`
3. Navega a cualquier endpoint
4. Usa los formularios para probar POST/PUT/PATCH
5. Los resultados se muestran en formato JSON legible

**Ventajas:**
- Interfaz visual amigable
- No necesitas curl
- Validación en tiempo real
- Documentación autogenerada

---

## 🐞 Manejo de Errores

### Error de validación:

**Request:**
```bash
curl -X POST http://localhost:8000/api/muestras/ \
  -H "Content-Type: application/json" \
  -d '{"cantidad_enviada": -10}'
```

**Response (400 Bad Request):**
```json
{
  "cantidad_enviada": [
    "La cantidad enviada debe ser mayor a cero."
  ]
}
```

### Recurso no encontrado:

**Request:**
```bash
curl http://localhost:8000/api/muestras/999/
```

**Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

## 📊 Paginación

Por defecto, las listas están paginadas a 50 resultados por página:

```bash
# Primera página
curl "http://localhost:8000/api/muestras/"

# Segunda página
curl "http://localhost:8000/api/muestras/?page=2"

# Cambiar tamaño de página (máximo 100)
curl "http://localhost:8000/api/muestras/?page_size=10"
```

**Estructura de respuesta paginada:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/muestras/?page=2",
  "previous": null,
  "results": [
    {...},
    {...}
  ]
}
```

---

## 🔐 Notas de Seguridad

**Para producción:**

1. Habilitar autenticación (Token o JWT)
2. Incluir token en headers:
   ```bash
   curl -H "Authorization: Token abc123xyz..." http://localhost:8000/api/muestras/
   ```
3. Configurar CORS apropiadamente
4. Usar HTTPS en vez de HTTP

---

**¡Listo para usar la API! 🎉**

Para más información, consulta el [README.md](README.md)
