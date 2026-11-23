# 📘 Guía Maestra y Manual de Demostración: LabControl (Avance 3)

Esta guía está diseñada paso a paso para presentar y defender el sistema **LabControl** ante el profesor con total seguridad.

---

## 🔑 1. Credenciales de Acceso (Los 2 Roles Obligatorios)

| Rol | Usuario | Contraseña | Permisos y Alcance |
| :--- | :--- | :--- | :--- |
| **Administrador / Bioquímico** | `admin` | `admin123` | Control total: altas de pacientes, creación de órdenes, catálogo de estudios, métricas globales, captura de resultados analíticos y cambio de estados. |
| **Recepcionista / Usuario** | `recepcion` | `recepcion123` | Operación de ventanilla: alta y edición de pacientes, creación de órdenes clínicas y cobro. Acceso denegado a catálogo y tarifas. |

---

## 🚀 2. Cómo Levantar el Sistema

Abre tu terminal y ejecuta:

```bash
cd /home/adrian/proyectos/labcontrol
python3 app.py
```
Abre en tu navegador:
👉 **`http://127.0.0.1:5000`**

*(El sistema funciona en automático tanto con MariaDB como con SQLite local como respaldo).*

---

## 🎬 3. Guion de la Demostración para el Profesor (Paso a Paso)

### Paso 1: El Portal Público del Paciente (Rediseño del Index)
1. **Entra a la raíz:** `http://127.0.0.1:5000/`.
2. **Qué explicarle:** *"Profesor, la primera pantalla del sistema no es un login aburrido, sino un portal web corporativo orientado al paciente (inspirado en BioSignal Lab de UABC). Aquí el paciente consulta sus análisis sin registrarse ni ver datos ajenos."*
3. **Pruébalo en vivo:**
   * En la barra de búsqueda escribe: **`ORD-2026-1001`** (o dale clic al chip de prueba rápida abajo).
   * Clic en **"Consultar Folio"**.
   * Se despliega el **Timeline Clínico** interactivo de 4 etapas:
     $$\text{Registrada} \longrightarrow \text{Muestra Recibida} \longrightarrow \text{En Análisis} \longrightarrow \text{Completada}$$
   * Muestra la tabla de analitos y da clic en **"Descargar / Imprimir Reporte Oficial"** para ver la hoja membretada con código QR.

---

### Paso 2: El Acceso al Panel Administrativo y Roles
1. Baja hasta el final de la página o da clic en el botón superior **"Acceso Personal"** (`/login`).
2. **Prueba de Rol Limitado (Recepcionista):**
   * Ingresa con `recepcion` / `recepcion123`.
   * Muestra que puede registrar órdenes y pacientes, pero si intenta ir a `/estudios/nuevo` el sistema le deniega el acceso (`403 Forbidden`).
3. **Prueba de Administrador:**
   * Cierra sesión (`/logout`) y entra con `admin` / `admin123`.
   * Muestra el Dashboard principal con las tarjetas de métricas en tiempo real.

---

### Paso 3: El Proceso de Negocio Completo (Flujo de Vida de una Orden)
Demuestra el ciclo clínico completo:

#### A. Registro de Paciente con Validaciones:
1. Ve a **Pacientes $\rightarrow$ Nuevo Paciente**.
2. **Validación de Código Postal:** En Código Postal escribe `22000` o `22400` y muestra cómo autocompleta la colonia, municipio y estado mediante la API externa.
3. **Validación de CURP:** Escribe una CURP errónea (ej. `HOLA123`) para mostrar el rechazo. Luego ingresa una válida de 18 caracteres (ej. `GOMA010101HBCRLA01`).
4. Guarda el paciente.

#### B. Generación de Orden Clínica:
1. Ve a **Órdenes $\rightarrow$ Nueva Orden**.
2. Selecciona al paciente recién creado.
3. Marca varios estudios (ej. *Biometría Hemática* y *Examen General de Orina*).
4. Muestra cómo el subtotal y total se calculan solos dinámicamente.
5. Selecciona método de pago (*Efectivo / Tarjeta / Transferencia*) y crea la orden.

#### C. Trazabilidad de Muestra Biológica:
1. En el detalle de la orden recién creada, muestra el estado inicial: **`Pendiente`**.
2. Clic en **"Recibir Muestra en Laboratorio"** $\rightarrow$ El sistema marca la fecha y hora exacta de recepción y avanza a **`Muestra Recibida`**.
3. Clic en **"Iniciar Análisis Clínico"** $\rightarrow$ El estado avanza a **`En Análisis`**.

#### D. Captura de Resultados Analíticos:
1. En la parte inferior aparece el formulario de captura exclusivo para el Bioquímico.
2. Ingresa los valores de prueba (ej. `14.2 g/dL`).
3. Guarda los resultados y cambia el estado a **`Completada`**.
4. Clic en **"Imprimir Reporte"** para mostrar la hoja membretada con los resultados finales.

---

### Paso 4: La API REST Integrada
Si el profesor pide ver los endpoints de la API, abre una pestaña nueva y muéstrale las respuestas JSON:
* **Consulta de orden por folio:**
  `http://127.0.0.1:5000/api/v1/ordenes/ORD-2026-1001`
* **Catálogo maestro de estudios:**
  `http://127.0.0.1:5000/api/v1/estudios`
* **Métricas operativas del laboratorio:**
  `http://127.0.0.1:5000/api/v1/metricas`

---

### Paso 5: Pruebas Unitarias y Medición de Rendimiento (En Terminal)
Abre una terminal y corre frente a él:

1. **Pruebas Unitarias (15 tests automatizados):**
   ```bash
   cd /home/adrian/proyectos/labcontrol
   pytest -v --tb=short
   ```
   *Explica:* *"Se implementaron 15 pruebas automatizadas con pytest que verifican login, roles, prevención de SQLi, validaciones de CURP y el ciclo de vida de las muestras"*.

2. **Medición y Perfilado (Profiling):**
   ```bash
   python3 scripts/benchmark_performance.py
   ```
   *Explica:* *"Medimos el cuello de botella más común: la consulta de órdenes con múltiples estudios. Identificamos el problema de consultas $N+1$ y lo optimizamos usando un único `JOIN` relacional e índices `B-Tree`, logrando una aceleración de **3.0x** (reducción del 66% de latencia)"*.

---

## 🛡️ 4. Acordeón para Preguntas Difíciles del Profesor

| Pregunta del Profesor | Respuesta recomendada |
| :--- | :--- |
| **¿Dónde están las validaciones?** | *"Se aplicó validación en dos capas: en cliente con HTML5 y expresiones regulares para experiencia de usuario, y en backend en Flask mediante validadores propios para evitar inyección SQL (consultas parametrizadas `?`), verificación de unicidad de CURP y formato de 18 caracteres."* |
| **¿Cómo garantizan que un recepcionista no modifique precios?** | *"Mediante un decorador personalizado `@login_required` y verificación estricta de sesión en la ruta `/estudios/nuevo`. Si el usuario no tiene `rol == 'admin'`, la aplicación interrumpe la petición con un error HTTP 403 Forbidden."* |
| **¿Por qué MariaDB y SQLite?** | *"MariaDB 10.11+ es el motor relacional de producción en Linux para garantizar integridad referencial y claves foráneas. Implementamos una capa de abstracción para fallback automático a SQLite3, garantizando que el software sea 100% portable y ejecutable en cualquier máquina sin dependencias externas complejas."* |
| **¿Qué herramienta usaron para medir?** | *"Usamos el módulo nativo de perfilado `cProfile` y `time.perf_counter()` de Python para medir 120 iteraciones continuas antes y después de refactorizar las sentencias SQL."* |
