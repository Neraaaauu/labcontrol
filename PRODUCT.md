# PRODUCT.md — LabControl

## 1. Producto y Propósito
**LabControl** es una aplicación web clínica para la gestión de solicitudes, toma de muestras, procesamiento analítico y entrega de resultados de un laboratorio de análisis clínicos pequeño.

## 2. Usuarios y Contexto de Uso
* **Bioquímico / Administrador:** Monitorea cargas de trabajo de laboratorio, procesa muestras, valida parámetros analíticos, emite resultados y administra el catálogo de pruebas.
* **Recepcionista / Atención en Ventanilla:** Registra pacientes con captura rápida asistida por API de Código Postal, cotiza estudios en tiempo real, crea solicitudes y rotula/recibe muestras.
* **Paciente:** Consulta de forma pública sus resultados mediante su código único de orden (folio `ORD-XXXX`) desde su móvil o computadora.

## 3. Modo de Superficie (Impeccable Mode)
* **Superficies Internas (Dashboard, Pacientes, Órdenes, Catálogo):** `Operate`
  * Prioridad: Máxima escaneabilidad, rapidez en ventanilla, precisión en datos clínicos, formularios fluidos, ergonomía visual y accesibilidad en jornadas continuas.
* **Portal de Consulta Externa (`/consultar`):** `Read / Service`
  * Prioridad: Claridad, tranquilidad para el paciente, visualización limpia de parámetros y valores de referencia sin tecnicismos innecesarios.

## 4. Requisitos Clave y Restricciones
* Base de datos MariaDB 10.11+ relacional con llaves foráneas e integridad referencial (fallback SQLite).
* Control de acceso basado en 2 roles (`admin` y `usuario`).
* Flujo de trabajo clínico estricto: `Registro de Paciente → Creación de Orden → Recepción de Muestra → Análisis Bioquímico → Resultados Listos`.
* Tolerancia a fallos: La API de Código Postal jamás bloquea la captura manual.
