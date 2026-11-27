# LabControl — Sistema Integral de Laboratorio Clínico

> **UABC | Universidad Autónoma de Baja California**  
> **Facultad de Ciencias Químicas e Ingeniería (FCQI)**  
> **Carrera:** Ingeniería en Software y Tecnologías Emergentes  
> **Materia:** Herramientas de Desarrollo de Software (HDS)  
> **Proyecto Integrador Final — Entrega final: jueves 26 de noviembre de 2026**  
> **Integrantes:** Gareth Castro · Adrián Gómez

---

## 🔬 Descripción del Proyecto

**LabControl** es una aplicación web para administrar las solicitudes de estudios de un laboratorio clínico pequeño. Permite registrar pacientes, armar órdenes con uno o varios estudios del catálogo (con cotización automática), marcar la recepción de la muestra, capturar resultados, validarlos con firma médica y que el paciente consulte sus resultados con su folio.

Todos los datos del sistema son **ficticios** y solo sirven para la demostración.

---

## 📋 Requerimientos de la Guía y Cómo se Cumplen

| Requerimiento (guía del proyecto) | Estado | Implementación en LabControl |
| :--- | :---: | :--- |
| **Framework web** | ✅ | **Flask 3.1** (Python 3.10+). |
| **Base de datos relacional** | ✅ | **SQLite** (sin instalar nada) o **MariaDB / MySQL** opcional. Si MariaDB no está disponible, el sistema cambia solo a SQLite. Claves foráneas e índices. |
| **Inicio y cierre de sesión con roles** | ✅ | Contraseñas cifradas con Werkzeug. **4 roles:** administrador, recepción, químico y médico (la guía pide mínimo 2). |
| **Módulos para registrar, consultar y modificar** | ✅ | Pacientes, catálogo de estudios y órdenes/muestras. |
| **Proceso de negocio completo** | ✅ | `Registrar paciente → Crear orden → Marcar muestra recibida → Análisis y captura → Dictamen médico → Resultados con hoja oficial imprimible`. |
| **Consulta de resultados por código** | ✅ | Página de inicio (`/`) y `/consultar`: el paciente escribe su folio (ej. `ORD-2026-1001`). |
| **API externa** | ✅ | Código postal con **Zippopotam.us**. Si la API falla o no hay internet, usa un respaldo local y el formulario sigue funcionando. |
| **API REST interna (extra)** | ✅ | Endpoints JSON en `/api/v1/...` (ver tabla abajo). |
| **Validaciones y mensajes de error** | ✅ | CURP con formato oficial, sin duplicados, email, teléfono de 10 dígitos y reglas de estados de la orden. |
| **Pruebas unitarias automatizadas** | ✅ | **17 pruebas** con `pytest` (la guía pide 5). |
| **Medición de rendimiento antes/después** | ✅ | `cProfile` + `time.perf_counter`: consulta de orden **≈3 veces más rápida** (0.30 → 0.10 ms) con un solo JOIN e índices. |
| **Uso de IA** | ✅ | Se usó **Claude (Anthropic)** para programar, diseñar, documentar y corregir errores. El equipo revisó el código y comprobó que las pruebas pasaran. |

---

## 👥 Usuarios de Demostración (datos ficticios)

La pantalla de inicio de sesión tiene botones de acceso rápido.

| Rol | Usuario | Contraseña | Perfil | Qué puede hacer |
| :--- | :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | QFB. Carlos Méndez | Todo: catálogo, estados, resultados y dictamen. |
| **Recepción** (usuario) | `recepcion` | `recepcion123` | Laura Morales | Alta de pacientes (con API de C.P.), creación de órdenes y recepción de muestras. |
| **Químico** | `quimico` | `quimico123` | Q.F.B. Roberto Salcedo | Procesar muestras y capturar resultados. |
| **Médico** | `doctor` | `doctor123` | Dr. Alejandro Peña | Revisar resultados, escribir el dictamen y firmar la orden. |

---

## ✅ Requisitos Previos

Solo necesitas dos programas:

| Programa | Versión | Cómo comprobarlo |
| :--- | :--- | :--- |
| **Python** | 3.10 o más nuevo | Mac: `python3 --version` · Windows: `python --version` |
| **Git** | Cualquiera reciente | `git --version` |

- **Mac:** instala Python desde [python.org](https://www.python.org/downloads/) o con `brew install python`.
- **Windows:** descarga Python desde [python.org](https://www.python.org/downloads/). Durante la instalación **marca la casilla "Add Python to PATH"**.

**No hace falta instalar ninguna base de datos.** Con SQLite (incluido en Python) todo se guarda en `instance/labcontrol.db`.

---

## 🚀 Instalación y Ejecución

Abre una terminal (Mac: app **Terminal** · Windows: **PowerShell** o **Símbolo del sistema**).

### 🍎 Mac (y Linux)

```bash
# 1. Descargar el proyecto y entrar a la carpeta
git clone https://github.com/Neraaaauu/labcontrol.git
cd labcontrol

# 2. Crear el entorno virtual (solo la primera vez)
python3 -m venv .venv

# 3. Activar el entorno virtual (cada vez que abras una terminal nueva)
source .venv/bin/activate

# 4. Instalar las librerías (solo la primera vez)
pip install -r requirements.txt

# 5. Usar SQLite como base de datos
export DB_ENGINE=sqlite

# 6. Arrancar (crea la base de datos con datos de prueba y abre el servidor)
./run.sh
```

> Si `./run.sh` dice "Permission denied", ejecuta una vez `chmod +x run.sh` y vuelve a intentarlo.  
> También puedes arrancar a mano: `python3 seed_data.py` y luego `python3 app.py`.

### 🪟 Windows

```powershell
# 1. Descargar el proyecto y entrar a la carpeta
git clone https://github.com/Neraaaauu/labcontrol.git
cd labcontrol

# 2. Crear el entorno virtual (solo la primera vez)
python -m venv .venv

# 3. Activar el entorno virtual (cada vez que abras una terminal nueva)
#    En PowerShell:
.venv\Scripts\Activate.ps1
#    En Símbolo del sistema (cmd):
.venv\Scripts\activate.bat

# 4. Instalar las librerías (solo la primera vez)
pip install -r requirements.txt

# 5. Usar SQLite como base de datos
#    En PowerShell:
$env:DB_ENGINE = "sqlite"
#    En Símbolo del sistema (cmd):
set DB_ENGINE=sqlite

# 6. Arrancar
run.bat
```

> También puedes arrancar a mano: `python seed_data.py` y luego `python app.py`.

### 🌐 Abrir el sistema

Cuando la terminal muestre `Running on http://127.0.0.1:5000`, abre en tu navegador:

**`http://127.0.0.1:5000`**

Para apagar el servidor, regresa a la terminal y presiona **Ctrl + C**.

> 💡 El entorno virtual está activo cuando tu terminal muestra `(.venv)` al inicio de la línea.

---

## 🧪 Pruebas Unitarias y Medición de Rendimiento

Con el entorno virtual activado, desde la carpeta del proyecto:

| Qué | Mac / Linux | Windows |
| :--- | :--- | :--- |
| Pruebas unitarias (17) | `python3 -m pytest -v` | `python -m pytest -v` |
| Medición de rendimiento antes/después | `python3 scripts/benchmark_performance.py` | `python scripts/benchmark_performance.py` |

Las 17 pruebas deben aparecer en verde (`PASSED`).

---

## 🛠️ Si algo falla

| Problema | Solución |
| :--- | :--- |
| **Mac:** el navegador muestra "403 Forbidden" o el puerto 5000 está ocupado | macOS usa el puerto 5000 para AirPlay. Ve a **Ajustes del Sistema → General → AirDrop y Handoff** y desactiva **"Receptor AirPlay"**. O arranca en otro puerto con `flask --app app run --port 5001` y abre `http://127.0.0.1:5001`. |
| **Windows:** `'python' no se reconoce como un comando` | Python no quedó en el PATH. Reinstálalo marcando **"Add Python to PATH"**, o usa `py` en lugar de `python`. |
| **Windows:** PowerShell no deja activar el entorno | Ejecuta una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y responde **S**. O usa cmd con `.venv\Scripts\activate.bat`. |
| `ModuleNotFoundError: No module named 'flask'` | El entorno virtual no está activado. Repite el paso 3. |
| Quiero reiniciar los datos de prueba | Borra `instance/labcontrol.db` y vuelve a ejecutar `seed_data.py` (o `run.sh` / `run.bat`). |
| La API de código postal no autocompleta | No pasa nada: hay respaldo sin conexión y puedes escribir el domicilio a mano. |

---

## 🧭 Demostración del Flujo Principal

1. **Recepción** (`recepcion` / `recepcion123`): ve a `Pacientes → Registrar Paciente`, escribe el código postal `22000` o `22400` y observa cómo la API llena Estado, Municipio y Colonias. Guarda.
2. **Crear orden:** en la ficha del paciente pulsa `Nueva Orden de Estudio`, marca uno o más estudios (el total se actualiza solo) y confirma.
3. **Marcar muestra recibida:** en la orden, pulsa **"Marcar Muestra Recibida"**.
4. **Químico** (`quimico` / `quimico123`): pulsa **"Iniciar Análisis"** y captura los resultados.
5. **Médico** (`doctor` / `doctor123`): escribe el dictamen y firma. La orden queda **Completada**.
6. **Consulta pública:** cierra sesión, ve a la página de inicio y escribe el folio (o el demo `ORD-2026-1001`) para ver los resultados y la hoja oficial imprimible.

---

## 🌐 Endpoints de la API REST Interna (JSON)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/ordenes/<codigo>` | Estado, paciente y estudios de un folio (ej. `ORD-2026-1001`). 404 si no existe. |
| `GET` | `/api/v1/estudios` | Catálogo de estudios activos con precios y tipo de muestra. |
| `POST` | `/api/v1/pacientes/validar-curp` | Valida el formato de la CURP y revisa si ya está registrada. |
| `GET` | `/api/v1/metricas` | Conteo de órdenes, pacientes y estados. |
| `GET` | `/api/codigo-postal/<cp>` | Consulta a la API externa de código postal, con respaldo sin conexión. |

---

## 🗄️ Opcional: Usar MariaDB / MySQL

SQLite basta para ejecutar y demostrar el sistema. Para usar MariaDB o MySQL:

1. Instala MariaDB/MySQL y crea una base de datos llamada `labcontrol`.
2. Configura estas variables de entorno antes de arrancar:
   - `DB_ENGINE=mariadb`
   - `MARIADB_USER=<tu_usuario>`
   - `MARIADB_DB=labcontrol`
   - `MARIADB_SOCKET=<ruta_del_socket>` (solo si te conectas por socket; si no, se usa `127.0.0.1:3306`)
3. Arranca normalmente. Si no logra conectarse, el sistema **cambia solo a SQLite**.

---

## 📁 Estructura del Repositorio

```text
labcontrol/
├── app.py                     # Rutas Flask, sesiones, roles, validaciones y API REST
├── database.py                # Capa de datos: SQLite (por defecto) u opcional MariaDB/MySQL
├── seed_data.py               # Datos ficticios de demostración
├── run.sh / run.bat           # Arranque rápido en Mac-Linux / Windows
├── requirements.txt           # Librerías de Python
├── MANUAL_DE_USUARIO.md       # Manual de uso por rol
├── instance/labcontrol.db     # Base de datos SQLite (se crea sola)
├── templates/                 # Vistas Jinja2 con Bootstrap 5
│   ├── index.html             # Portal público con consulta por folio
│   ├── login.html, dashboard.html, consulta_publica.html, base.html
│   ├── pacientes/             # Lista, alta, edición y detalle
│   ├── ordenes/               # Lista, nueva, detalle y reporte_impreso
│   └── estudios/              # Catálogo de estudios
├── static/                    # CSS y JS
├── tests/test_labcontrol.py   # 17 pruebas unitarias (pytest)
├── scripts/
│   └── benchmark_performance.py   # Medición de rendimiento antes/después
├── screenshots/               # Capturas y datos de rendimiento
└── docs/                      # Reportes (Avances 1-3, Reporte Final, presentación y guion de demo)
```

---

## 📄 Documentos de Entrega (`docs/`)

| Entrega | Archivo |
| :--- | :--- |
| Avance 1 — Análisis y diseño | `Avance_1_LabControl_Analisis_y_Diseno.docx` |
| Avance 2 — Prototipo | `Avance_2_LabControl_Prototipo_Funcional.docx` |
| Avance 3 — Integración y calidad | `Avance_3_LabControl_Integracion_y_Calidad.docx` |
| **Entrega final — Reporte** | `Reporte_Final_LabControl.docx` |
| **Entrega final — Presentación** | `Presentacion_LabControl.pptx` |
| **Entrega final — Guion de demo** | `Guion_Demo_LabControl.md` |

**Figma:** _(pendiente — agregar enlace)_
