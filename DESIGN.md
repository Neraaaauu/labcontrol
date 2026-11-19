# DESIGN.md — LabControl Design System

## 1. Dirección Visual y Voz
* **Concepto:** *Clinical Precision & Calm Utility* (Precisión Clínica y Utilidad Serena).
* **Atmósfera:** Limpia, confiable, médica pero contemporánea. El software desaparece para permitir al personal enfocarse en el paciente y en la precisión analítica.
* **Prohibiciones de IA Slop:**
  * Sin degradados violeta/azul genéricos.
  * Sin tarjetas anidadas dentro de tarjetas ("cards inside cards").
  * Sin cejas o kickers redundantes arriba de los títulos.
  * Sin sombras duras tipo comic/neobrutalistas fuera de contexto.
  * Sin números de sección decorativos sin significado funcional.

## 2. Paleta de Color Semántica
```css
:root {
  /* Marca e Identidad */
  --color-brand-primary: #0e7490;    /* Cyan 700 - Confianza médica profunda */
  --color-brand-accent: #0891b2;     /* Cyan 600 - Focos y acciones primarias */
  --color-brand-hover: #155e75;      /* Cyan 800 - Interacción activa */
  --color-brand-light: #ecfeff;      /* Cyan 50 - Fondos suaves */

  /* Neutrales de Fondo y Superficie */
  --bg-page: #f8fafc;                /* Slate 50 - Fondo general fresco y descansado */
  --bg-surface: #ffffff;             /* Blanco puro - Tarjetas y paneles */
  --bg-subtle: #f1f5f9;              /* Slate 100 - Tablas cabeceras y bandas */
  --border-subtle: #e2e8f0;          /* Slate 200 - Delimitación precisa */
  --border-strong: #cbd5e1;          /* Slate 300 - Bordes de inputs */

  /* Tipografía */
  --text-main: #0f172a;              /* Slate 900 - Contraste alto para lectura rápida */
  --text-muted: #64748b;             /* Slate 500 - Etiquetas secundarias */
  --text-subtle: #94a3b8;            /* Slate 400 - Placeholders y metadata */

  /* Estados de Muestra y Negocio */
  --status-pending-text: #b45309;
  --status-pending-bg: #fef3c7;
  --status-pending-border: #fde68a;

  --status-received-text: #334155;
  --status-received-bg: #f1f5f9;
  --status-received-border: #e2e8f0;

  --status-analysis-text: #0369a1;
  --status-analysis-bg: #e0f2fe;
  --status-analysis-border: #bae6fd;

  --status-complete-text: #047857;
  --status-complete-bg: #d1fae5;
  --status-complete-border: #a7f3d0;
}
```

## 3. Tipografía y Jerarquía
* **Familia:** `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif`.
* **Números tabulares:** Activado `font-variant-numeric: tabular-nums` para códigos de orden (`ORD-XXXX`), CURP, precios y resultados numéricos.
* **Escala:**
  * Encabezados de página: `1.35rem` a `1.5rem` (peso 700).
  * Títulos de sección: `1.05rem` a `1.15rem` (peso 600).
  * Texto base: `0.9375rem` (15px, peso 400, interlineado 1.5).
  * Metadatos y etiquetas: `0.8125rem` (13px, peso 500).

## 4. Elevación y Profundidad
* Tarjetas: `box-shadow: 0 1px 3px 0 rgb(15 23 42 / 0.05), 0 1px 2px -1px rgb(15 23 42 / 0.05);`
* Hover interactivo: `box-shadow: 0 4px 6px -1px rgb(15 23 42 / 0.07), 0 2px 4px -2px rgb(15 23 42 / 0.05); transform: translateY(-1px);`
* Borde sutil continuo en todas las superficies blancas (`1px solid var(--border-subtle)`).

## 5. Componentes y Controles
* **Botones:** Bordes suaves de 6px, padding táctil consistente, estado hover con feedback visual sin sacudidas, focus-visible con anillo desplazado (`outline: 2px solid var(--color-brand-accent); outline-offset: 2px`).
* **Inputs y Formularios:** Altura táctil de 42px, bordes limpios, validaciones contextuales inmediatas.
* **Tablas:** Cabeceras en fondo Slate 100 con texto en mayúsculas sutiles (`letter-spacing: 0.05em`), filas con efecto hover suave, alineación numérica a la derecha y acciones agrupadas.
* **Línea de tiempo de muestra:** Stepper horizontal fluido con estados activos claros e iconografía consistente.
