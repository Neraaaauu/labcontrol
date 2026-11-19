# DESIGN.md — LabControl Natural UI Design System

## 1. Filosofía de Diseño
* **Dirección:** *Natural UI & Clinical Utility* (Interfaz Natural y Utilidad Clínica).
* **Sensación:** Un software de trabajo sobrio, ordenado, profesional y reposado que un químico o recepcionista de laboratorio puede operar durante jornadas completas sin fatiga visual.
* **Rechazo de Patrones Artificiales (Anti AI-Slop):**
  * Sin dashboards fragmentados en "card soup" (sopa de tarjetas desconectadas).
  * Sin degradados decorativos o luces artificiales.
  * Sin sombras pesadas o halos de neón.
  * Sin border-radius exagerado (se emplean radios discretos de 4px, 6px y 8px, con cápsulas únicamente para filtros y badges de estado).
  * Sin saturación de iconos en cada texto o encabezado.
  * Sin tipografía en negrita exagerada; jerarquías limpias con pesos 400 (regular), 500 (medium) y 600 (semibold).

## 2. Paleta de Color Poco Saturada
```css
:root {
  /* Cabecera y Acentos */
  --c-header-bg: #1e293b;        /* Pizarra natural */
  --c-header-nav-active: #334155;
  --c-accent: #2b4c6f;           /* Azul acero sobrio */
  --c-accent-hover: #1e3650;
  
  /* Superficies */
  --c-bg: #f8fafc;               /* Gris suave y descansado */
  --c-surface: #ffffff;          /* Paneles de trabajo */
  --c-surface-subtle: #f1f5f9;   /* Cabeceras de tabla y fondos alternos */
  
  /* Bordes y Líneas */
  --c-border: #e2e8f0;           /* Separadores discretos */
  --c-border-strong: #cbd5e1;    /* Contornos de inputs */

  /* Tipografía */
  --c-text-title: #0f172a;       /* Titulares y valores clave */
  --c-text-body: #1e293b;        /* Texto de lectura */
  --c-text-muted: #64748b;       /* Metadatos */

  /* Estados de Muestra (Pasteles Naturales) */
  --st-pending-text: #92400e;   --st-pending-bg: #fefce8;
  --st-received-text: #334155;  --st-received-bg: #f1f5f9;
  --st-analysis-text: #1e40af;  --st-analysis-bg: #eff6ff;
  --st-complete-text: #166534;  --st-complete-bg: #f0fdf4;
}
```

## 3. Composición Continua y Componentes Clave
1. **Franja de Métricas Continua (`.metrics-strip`):** Una única barra horizontal con bordes internos delgados que muestra los contadores de pacientes, órdenes y estados, eliminando las tarjetas cuadradas independientes con iconos redundantes.
2. **Línea de Trazabilidad (`.workflow-strip`):** Una tira de proceso horizontal continua que conecta los 4 pasos del laboratorio (Registro, Solicitud, Recepción de Muestra, Análisis y Resultados).
3. **Páneles de Datos Unificados (`.panel-clinical`):** Fusión de la barra de búsqueda y filtros directamente en la cabecera de la tabla de datos, creando un único espacio de trabajo fluido.
4. **Tablas Clínicas Compactas (`.table-clinical`):** Filas con espaciado equilibrado, cabeceras en mayúsculas atenuadas, números tabulares alineados a la derecha y acciones agrupadas.
5. **Badges de Estado Discretos (`.badge-status`):** Indicadores tipo píldora con punto de color (`.dot-indicator`) y textos descriptivos en tonos apagados.
