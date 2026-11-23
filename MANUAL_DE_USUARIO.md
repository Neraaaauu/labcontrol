# 📘 Guía Maestra y Manual de Demostración: LabControl (Avance 3)

Esta guía está diseñada paso a paso para presentar y defender el sistema **LabControl** ante el profesor con total seguridad.

---

## 🔑 1. Credenciales de Acceso (4 Roles Clínicos Específicos NOM-007)

El sistema implementa separación de responsabilidades clínicas y control de acceso basado en roles (**RBAC**):

| Rol Clínico | Usuario | Contraseña | Nombre y Cédula | Funciones Específicas en el Laboratorio |
| :--- | :--- | :--- | :--- | :--- |
| **Médico Patólogo / Validador (El Doctor)** | `doctor` | `doctor123` | **Dr. Alejandro Peña Treviño**<br>Ced. Méd. `5629143`<br>Esp. Patología `928371` | **Revisión, Dictamen y Liberación:** Evalúa los hallazgos capturados por el químico, escribe la **Interpretación Diagnóstica / Dictamen Médico** y firma oficialmente la orden para autorizar su entrega. |
| **Químico Analista (Q.F.B. / Laboratorista)** | `quimico` | `quimico123` | **Q.F.B. Roberto Salcedo García**<br>Ced. Prof. `9384721` UABC | **Procesamiento de Muestras:** Recibe la muestra biológica en laboratorio, opera los analizadores y captura los valores analíticos medidos (analitos, unidades y rangos de referencia). |
| **Recepcionista / Admisión y Caja** | `recepcion` | `recepcion123` | **Laura Morales**<br>Turno: `Matutino (Ventanilla 1)`<br>No. Emp: `EMP-0412` | **Ventanilla y Cobro:** Registro de pacientes, validación de CURP y domicilio, generación de órdenes clínicas, cobro y entrega de folio al paciente. Acceso denegado a catálogo y dictámenes. |
| **Director General / Administrador** | `admin` | `admin123` | **QFB. Carlos Méndez**<br>Dirección General | **Administración Global:** Gestión del catálogo de estudios clínicos, tarifas, altas de personal, configuración y visualización de métricas generales. |

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

### Paso 2: El Acceso al Panel y Demostración de Roles
1. Baja hasta el final de la página o da clic en el botón superior **"Acceso Personal"** (`/login`).
2. **Los 4 Roles Disponibles:** En la pantalla de login verás los 4 botones de acceso rápido:
   * **Recepcionista (`recepcion`):** Crea órdenes y pacientes, pero no puede modificar precios ni dictaminar (`403 Forbidden`).
   * **Químico (`quimico`):** Recibe muestras y captura parámetros analíticos.
   * **Médico Patólogo (`doctor`):** Revisa hallazgos analíticos, redacta el dictamen clínico e interpretación diagnóstica y avala formalmente.
   * **Director General (`admin`):** Administrador del sistema con acceso completo.

---

### Paso 3: El Proceso de Negocio Completo (Flujo de Vida Clínico)
Demuestra el ciclo clínico completo con los 3 actores de laboratorio:

#### A. Recepcionista (Ventanilla y Admisión):
1. Entra como `recepcion` / `recepcion123`.
2. Ve a **Pacientes $\rightarrow$ Nuevo Paciente**: Pon el CP `22000` (se autocompleta con API) y escribe una CURP válida (ej. `GOMA010101HBCRLA01`).
3. Ve a **Órdenes $\rightarrow$ Nueva Orden**: Selecciona al paciente, marca 2 estudios (se calcula el total en vivo) y genera la orden. Se registrará: *"Atendido por Laura Morales (Turno Matutino - Ventanilla 1)"*.

#### B. Químico Analista (Procesamiento de Muestras):
1. Entra como `quimico` / `quimico123`.
2. Entra al detalle de la orden. Clic en **"Recibir Muestra en Laboratorio"** $\rightarrow$ Estado avanza a **`Muestra Recibida`**.
3. Clic en **"Iniciar Análisis Clínico"** $\rightarrow$ Estado avanza a **`En Análisis`**.
4. En la tabla de estudios, captura los hallazgos analíticos (ej. *Hemoglobina: 14.2 g/dL*, *Glucosa: 88.5 mg/dL*) y da clic en **"Guardar Parámetros (Laboratorio)"**. La muestra queda firmada técnicamente por el Q.F.B. Roberto Salcedo con Cédula `9384721`.

#### C. Médico Patólogo Validador (El Doctor - Dictamen Clínico):
1. Entra como `doctor` / `doctor123`.
2. Abre la orden. En la parte inferior verás el **Módulo Médico: Dictamen Diagnóstico e Interpretación Médica**.
3. En el cuadro de texto escribe la conclusión médica:
   *Ejemplo: "Serie eritrocitaria y leucocitaria dentro de parámetros fisiológicos normales. Glucemia en ayuno normal. Sin evidencia de anomalías patológicas agudas."*
4. Da clic en el botón rojo: **"Firmar y Avalar Médicamente"**.
5. La orden queda formalmente en estado **`Completada`**, avalada por el Dr. Alejandro Peña Treviño con Cédula `5629143` y Especialidad en Patología Clínica `928371`.

#### D. Reporte Impreso Oficial (Doble Firma):
1. Da clic en **"Imprimir Reporte"** (o consulta el folio desde la página de inicio).
2. Muestra la hoja clínica oficial:
   * **Datos de Recepción:** Nombre de la recepcionista y turno de ventanilla.
   * **Recuadro de Dictamen Médico:** El diagnóstico redactado por el doctor.
   * **Doble Firma Digital:** Sello criptográfico, firma técnica del Químico Q.F.B. y firma médica del Patólogo Responsable Sanitario con sus respectivas cédulas profesionales.

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
