# LabControl — Sistema Integral de Laboratorio Clínico

> **UABC | Universidad Autónoma de Baja California**  
> **Facultad de Ciencias Químicas e Ingeniería (FCQI)**  
> **Carrera:** Ingeniería en Software y Tecnologías Emergentes  
> **Materia:** Herramientas de Desarrollo de Software (HDS)  
> **Proyecto Integrador Final — Entregas: Avance 1, Avance 2 & Avance 3 (Integración y Calidad)**

---

## 🔬 Descripción del Proyecto

**LabControl** es una aplicación web desarrollada para optimizar la administración y trazabilidad operativa de un laboratorio de análisis clínicos pequeño. Resuelve de manera integral el registro de expedientes de pacientes, la selección de estudios médicos del catálogo con cotización automática, la recepción física y control de estados de muestras biológicas (sangre, orina, heces), la captura de resultados analíticos por químicos certificados y la consulta transparente de resultados mediante un portal público para pacientes con folio único e impresión oficial.

---

## 📋 Requerimientos Oficiales Cumplidos (Avance 3: 100% Completo)

| Requerimiento Oficial (PDF de la Materia) | Estado | Implementación en LabControl |
| :--- | :---: | :--- |
| **Framework Web** | ✅ | **Flask 3.1.3 (Python 3.12)** con arquitectura modular y limpia. |
| **Base de Datos Relacional** | ✅ | **MariaDB 10.11+ / MySQL** (como motor principal de usuario en Linux) con fallback transparente a SQLite3. Claves foráneas e índices B-Tree de optimización. |
| **Inicio y Cierre de Sesión con 2 Roles** | ✅ | Sesiones firmadas y contraseñas seguras con Werkzeug. Roles: **admin** y **usuario**. |
| **Portal Público / Rediseño del Index** | ✅ | Nueva página de inicio (`/`) con buscador interactivo por folio, catálogo de especialidades, preparación de muestra y bloque inferior al panel administrativo. |
| **Proceso de Negocio Completo** | ✅ | Flujo de 5 fases: `Registrar paciente → Crear orden → Marcar muestra recibida → Análisis y captura → Resultados listos con hoja oficial imprimible`. |
| **Integración de APIs** | ✅ | **API Externa** (Código Postal Zippopotam con respaldo tolerante a fallos) + **API REST Interna JSON** (`/api/v1/ordenes/<codigo>`, `/api/v1/estudios`, `/api/v1/pacientes/validar-curp`, `/api/v1/metricas`). |
| **Validaciones Robustas** | ✅ | Expresión regular oficial de CURP (RENAPO), prevención de duplicados, validación de emails/teléfonos y máquina de estados clínica. |
| **Pruebas Unitarias Automatizadas** | ✅ | **15 pruebas unitarias** con `pytest` (100% aprobadas, cubriendo modelos, API, cálculo financiero y transiciones). |
| **Medición de Rendimiento y Mejora** | ✅ | Perfilado con `cProfile` y `time.perf_counter` comparando Antes vs Después: **2.38x más rápido (57.9% menor tiempo)** gracias a índices y single JOIN. |
| **Reportes Oficiales (.docx y .pdf)** | ✅ | Documentos formales listos en `docs/`: **Avance 1**, **Avance 2** y **Avance 3** (en Word y PDF). |

---

## 👥 Credenciales de Demostración (2 Roles)

El sistema incluye botones de acceso rápido en la pantalla de inicio de sesión:

| Rol | Usuario | Contraseña | Nombre / Perfil | Alcance / Permisos |
| :--- | :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | QFB. Carlos Méndez (Bioquímico) | Control total, cambio de estados, captura de resultados analíticos, emisión de hojas clínicas y gestión del catálogo. |
| **Usuario Operativo** | `recepcion` | `recepcion123` | Laura Morales (Recepción) | Alta de pacientes con API de C.P., creación de órdenes y recepción de muestras en ventanilla. |

---

## 🚀 Guía de Instalación y Ejecución Rápida

### 1. Clonar o acceder a la carpeta del proyecto
```bash
cd /home/adrian/proyectos/labcontrol
```

### 2. Inicializar la Base de Datos con Datos Semilla (Opcional si ya existe)
```bash
python3 seed_data.py
```

### 3. Ejecutar la Suite de Pruebas Unitarias
```bash
pytest -v
```

### 4. Ejecutar la Medición de Rendimiento y Profiling
```bash
python3 scripts/benchmark_performance.py
```

### 5. Iniciar la Aplicación Web
```bash
./run.sh
# o directamente: python3 app.py
```
Abre en tu navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🌐 Endpoints de la API REST Interna (JSON)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/ordenes/<codigo>` | Retorna el expediente clínico, estado, paciente y estudios asociados de un folio (ej. `ORD-2026-1001`). Responde 404 si no existe. |
| `GET` | `/api/v1/estudios` | Catálogo público completo de pruebas activas, precios, tipos de muestra e indicaciones. |
| `POST` | `/api/v1/pacientes/validar-curp` | Valida el formato de CURP con regex oficial, comprueba duplicidad en MariaDB y extrae fecha/sexo. |
| `GET` | `/api/v1/metricas` | Expone telemetría y métricas operativas del laboratorio en tiempo real. |
| `GET` | `/api/codigo-postal/<cp>` | Consumo de API externa de códigos postales con fallback offline tolerante a fallos. |
# O directamente con:
python3 app.py
```
Abre tu navegador en: **`http://127.0.0.1:5000`**

### 4. Ejecutar la Suite de Pruebas Unitarias
```bash
pytest -v
```

---

## 🧪 Demostración del Flujo Principal Paso a Paso

Para evaluar la demostración solicitada por la materia:
1. **Iniciar Sesión:** Entra con `recepcion` / `recepcion123` o con `admin` / `admin123`.
2. **Registrar Paciente (Módulo 1 + API):** Ve a `Pacientes → Registrar Paciente`. Ingresa nombre, CURP y escribe el código postal `22000` o `22400`. Observa cómo la API autocompleta Estado, Municipio y Colonias. Guarda el expediente.
3. **Crear Orden (Módulo 2):** En la ficha del paciente, haz clic en `Nueva Orden de Estudio`. Marca uno o más estudios (ej. *Biometría Hemática* y *Química Sanguínea*). Verifica que el total se actualice dinámicamente y presiona *Confirmar y Crear Orden*.
4. **Marcar Muestra Recibida:** En la orden generada, pulsa el botón **"Marcar Muestra Recibida"**. La línea de tiempo avanzará registrando el timestamp.
5. **Actualizar Estado de la Orden:** Pulsa **"Iniciar Análisis Bioquímico"** y posteriormente **"Completar Orden"**, capturando los valores analíticos.
6. **Consultar por Código:** Haz clic en *Buscar Folio* en la barra superior o ve a `/consultar` e ingresa el código generado (o prueba con el demo `ORD-2026-1001`) para ver el reporte de resultados liberado.

---

## 📁 Estructura del Repositorio

```text
labcontrol/
├── app.py                     # Controlador central Flask, rutas, sesiones y decoradores de rol
├── database.py                # Capa de datos MariaDB (Linux) / Fallback SQLite y esquema relacional
├── seed_data.py               # Generador de datos semilla ficticios realistas
├── run.sh                     # Script ejecutable de inicio rápido (inicia MariaDB y servidor)
├── instance/
│   └── labcontrol.db          # Respaldo portable SQLite relacional
├── templates/                 # Vistas Jinja2 responsivas con Bootstrap 5
│   ├── base.html              # Plantilla base con navbar y notificaciones flash
│   ├── login.html             # Pantalla de acceso con botones demo de rol
│   ├── dashboard.html         # Panel de control con contadores y órdenes recientes
│   ├── consulta_publica.html  # Buscador de análisis por folio/código
│   ├── pacientes/             # Vistas de pacientes (lista, nuevo, editar, detalle)
│   ├── ordenes/               # Vistas de órdenes y muestras (lista, nueva, detalle)
│   └── estudios/              # Catálogo maestro de análisis clínicos
├── static/
│   ├── css/custom.css         # Estilos personalizados y reglas de impresión
│   └── js/main.js             # Lógica frontend
├── tests/
│   └── test_labcontrol.py     # Suite de 8 pruebas unitarias con pytest
├── docs/                      # Documentación oficial de entrega
│   ├── Avance_1_LabControl_Analisis_y_Diseno.docx       # Reporte oficial Avance 1 (2 a 3 páginas)
│   ├── Avance_2_LabControl_Prototipo_Funcional.docx    # Reporte oficial Avance 2 con evidencias
│   └── esquema_base_datos.png                          # Diagrama Entidad-Relación relacional
└── screenshots/               # Evidencias visuales de pantallas y pruebas
```

---

## 📄 Documentos de Entrega Generados (.docx)

- **Avance 1 (Análisis y Diseño):** `docs/Avance_1_LabControl_Analisis_y_Diseno.docx`  
  Cumple con la extensión orientativa de 2 a 3 páginas con el sistema seleccionado, objetivo, funciones, diagrama relacional de base de datos, justificación del framework y especificación de las 3 pantallas.
- **Avance 2 (Prototipo Funcional):** `docs/Avance_2_LabControl_Prototipo_Funcional.docx`  
  Reporte exhaustivo con portada institucional, descripción del prototipo ejecutable, base de datos con integridad referencial, roles de usuario, tolerancia a fallos de la API, capturas de pantalla de cada pantalla funcionando y reporte de pruebas automatizadas.
