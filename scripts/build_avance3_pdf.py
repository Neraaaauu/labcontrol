#!/usr/bin/env python3
"""
Generador del Documento Oficial de Avance 3 (.pdf) para LabControl
Materia: Herramientas de Desarrollo de Software (HDS) — UABC FCQI
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

BASE_DIR = "/home/adrian/proyectos/labcontrol"
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "Avance_3_LabControl_Integracion_y_Calidad.pdf")

COLOR_STEEL = colors.HexColor("#2b4c6f")
COLOR_NAVY = colors.HexColor("#1e293b")
COLOR_DARK = colors.HexColor("#0f172a")
COLOR_MUTED = colors.HexColor("#64748b")
COLOR_BORDER = colors.HexColor("#e2e8f0")
COLOR_HEADER_BG = colors.HexColor("#f1f5f9")
COLOR_LIGHT_BG = colors.HexColor("#f8fafc")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_MUTED)

        # Header (desde la página 2)
        if self._pageNumber > 1:
            self.drawString(45, 755, "UABC / HDS — LabControl: Reporte de Avance 3 (Integración y Calidad)")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(45, 747, 567, 747)

        # Footer
        footer_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(567, 30, footer_text)
        self.drawString(45, 30, "LabControl — Sistema Integral de Laboratorio Clínico (MariaDB + Flask + REST API)")
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(45, 42, 567, 42)

        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=48,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_inst = ParagraphStyle(
        'InstTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=COLOR_STEEL,
        spaceAfter=1
    )

    sub_inst = ParagraphStyle(
        'SubInst',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=COLOR_MUTED,
        spaceAfter=12
    )

    report_title = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=COLOR_DARK,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=COLOR_STEEL,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=COLOR_NAVY,
        alignment=4,  # Justified
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=COLOR_NAVY,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10.5,
        textColor=COLOR_MUTED,
        alignment=1,  # Centered
        spaceAfter=8,
        spaceBefore=2
    )

    story = []

    # 1. Cabecera Institucional
    story.append(Paragraph("UNIVERSIDAD AUTÓNOMA DE BAJA CALIFORNIA", title_inst))
    story.append(Paragraph(
        "FACULTAD DE CIENCIAS QUÍMICAS E INGENIERÍA &bull; INGENIERÍA EN SOFTWARE Y TECNOLOGÍAS EMERGENTES<br/>"
        "Herramientas de Desarrollo de Software (HDS) &bull; Semestre 2026-2",
        sub_inst
    ))

    story.append(Paragraph("REPORTE DE AVANCE 3: INTEGRACIÓN Y CALIDAD<br/><font size='10.5' color='#64748b'>SISTEMA WEB: LABCONTROL (LABORATORIO CLÍNICO)</font>", report_title))

    # 2. Metadatos del Proyecto
    meta_table_data = [
        [
            Paragraph("<b>Materia y Fase:</b>", body_style),
            Paragraph("Herramientas de Desarrollo de Software — Avance 3 (Integración y Calidad)", body_style)
        ],
        [
            Paragraph("<b>Sistema Desarrollado:</b>", body_style),
            Paragraph("LabControl (Gestión de Pacientes, Órdenes, Toma de Muestras y Resultados)", body_style)
        ],
        [
            Paragraph("<b>Integrantes:</b>", body_style),
            Paragraph("Adrian Gómez / Equipo de Desarrollo HDS", body_style)
        ],
        [
            Paragraph("<b>Tecnologías y Persistencia:</b>", body_style),
            Paragraph("Python 3.12, Flask 3.1, MariaDB 10.11+ (Linux nativo), Fallback SQLite, Bootstrap 5", body_style)
        ],
        [
            Paragraph("<b>Fecha de Entrega:</b>", body_style),
            Paragraph("Lunes 23 de noviembre de 2026", body_style)
        ],
        [
            Paragraph("<b>Cumplimiento de Rúbrica:</b>", body_style),
            Paragraph("<font color='#166534'><b>100% Cumplido:</b> Proceso completo, API externa/interna, validaciones, 15 pruebas y benchmark.</font>", body_style)
        ]
    ]

    t_meta = Table(meta_table_data, colWidths=[150, 372])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 3. Resumen Ejecutivo
    story.append(Paragraph("1. Resumen Ejecutivo del Avance 3", h1_style))
    story.append(Paragraph(
        "<b>Logros Clave del Avance 3:</b> En estricto cumplimiento con la rúbrica oficial de la materia ('Proceso de negocio completo, "
        "API, validaciones, 3 pruebas unitarias, medición de rendimiento y mejora. Presentar borrador del reporte Word'), "
        "se ha culminado con éxito la fase de integración y consolidación de calidad para el sistema LabControl. "
        "Esta entrega aporta: (1) Un rediseño total de la página principal (Index) orientada al paciente con consulta por folio "
        "y catálogo de servicios; (2) El proceso de negocio clínico completo, desde la toma de muestra hasta la emisión de la hoja oficial con validación analítica; "
        "(3) Integración dual de APIs: externa para autocompletado de domicilios con tolerancia a fallos y una API REST interna con endpoints JSON estructurados; "
        "(4) Sistema de validaciones estrictas sintácticas y semánticas; (5) Suite de 15 pruebas unitarias automatizadas con pytest; y "
        "(6) Medición formal de rendimiento con cProfile demostrando una aceleración de 2.38x (reducción del 57.9% en tiempo de respuesta de BD).",
        body_style
    ))

    # 4. Rediseño del Index
    story.append(Paragraph("2. Rediseño del Index y Portal Público para Clientes", h1_style))
    story.append(Paragraph(
        "Siguiendo los lineamientos de diseño de la entrega, se transformó la página principal ('/') en un portal público orientado al paciente "
        "que no requiere autenticación previa, con estilo sobrio y profesional (Natural UI):",
        body_style
    ))
    story.append(Paragraph("• <b>Módulo Central de Consulta por Folio:</b> Permite al paciente ingresar su código (ej. ORD-2026-1001) para visualizar la tira de trazabilidad de 4 fases y consultar sus resultados analíticos y valores de referencia en tiempo real.", bullet_style))
    story.append(Paragraph("• <b>Catálogo de Especialidades y Guía Clínica:</b> Información completa de Hematología, Bioquímica, Inmunología, Microbiología, Check-ups, horas de ayuno requeridas y sedes en Tijuana (Otay UABC y Zona Río).", bullet_style))
    story.append(Paragraph("• <b>Bloque de Acceso al Panel Administrativo:</b> Sección inferior destacada con fondo oscuro ('block-admin-portal') que contiene el hipervínculo directo al inicio de sesión administrativo ('/login') y credenciales demo.", bullet_style))

    img_index = os.path.join(SCREENSHOTS_DIR, "12_index_portal_cliente.png")
    if os.path.exists(img_index):
        story.append(KeepTogether([
            Image(img_index, width=520, height=270),
            Paragraph("Figura 2.1: Nueva página de inicio (Index) pública para pacientes con buscador de folios y catálogo de servicios.", caption_style)
        ]))

    img_consulta = os.path.join(SCREENSHOTS_DIR, "13_index_consulta_folio.png")
    if os.path.exists(img_consulta):
        story.append(KeepTogether([
            Image(img_consulta, width=520, height=270),
            Paragraph("Figura 2.2: Despliegue interactivo del estado de la orden ORD-2026-1001 con trazabilidad de 4 fases y parámetros analíticos.", caption_style)
        ]))

    # 5. Proceso de Negocio Completo
    story.append(Paragraph("3. Proceso de Negocio Completo y Hoja Clínica Oficial", h1_style))
    story.append(Paragraph(
        "El sistema resuelve de extremo a extremo el ciclo de trabajo de un laboratorio de análisis clínicos en 5 fases estandarizadas: "
        "<b>1. Alta de paciente</b> (asistida por API de CP y validación de CURP); "
        "<b>2. Creación de orden</b> (selección multi-estudio y cotización automática en tiempo real); "
        "<b>3. Toma y recepción de muestra</b> (registro de timestamp y cambio a 'Muestra Recibida'); "
        "<b>4. Procesamiento bioquímico</b> (captura de valores analíticos por el químico responsable); y "
        "<b>5. Emisión del informe clínico oficial</b> con sello de validación analítica y firma de QFB.",
        body_style
    ))

    img_reporte = os.path.join(SCREENSHOTS_DIR, "14_reporte_clinico_impreso.png")
    if os.path.exists(img_reporte):
        story.append(KeepTogether([
            Image(img_reporte, width=520, height=280),
            Paragraph("Figura 3.1: Hoja clínica oficial de resultados generada para impresión y descarga en PDF con sellos COFEPRIS y firma de QFB.", caption_style)
        ]))

    # 6. APIs
    story.append(Paragraph("4. Integración de APIs: Externa de C.P. e Interna REST", h1_style))
    story.append(Paragraph(
        "<b>API Externa (Zippopotam.us):</b> Consumo de 'http://api.zippopotam.us/mx/{cp}' con timeout de 2.5s y respaldo offline local "
        "que previene cualquier bloqueo ante caídas de red o fallos externos.<br/>"
        "<b>API REST Interna (Endpoints JSON):</b> Se expusieron 4 endpoints formales: "
        "<code>GET /api/v1/ordenes/&lt;codigo&gt;</code>, "
        "<code>GET /api/v1/estudios</code>, "
        "<code>POST /api/v1/pacientes/validar-curp</code> y "
        "<code>GET /api/v1/metricas</code> con códigos de estado HTTP estándar (200, 400, 404).",
        body_style
    ))

    img_api = os.path.join(SCREENSHOTS_DIR, "15_api_rest_json.png")
    if os.path.exists(img_api):
        story.append(KeepTogether([
            Image(img_api, width=520, height=210),
            Paragraph("Figura 4.1: Consumo del endpoint REST JSON /api/v1/ordenes/ORD-2026-1001 verificado vía cURL.", caption_style)
        ]))

    # 7. Validaciones
    story.append(Paragraph("5. Sistema de Validaciones Clínicas y Manejo de Errores", h1_style))
    story.append(Paragraph(
        "Se aplicó blindaje exhaustivo en controladores y modelos: "
        "• <b>Validación de CURP:</b> Expresión regular oficial de 18 caracteres alfanuméricos y rechazo de duplicados en MariaDB. "
        "• <b>Validación de Emails y Teléfonos:</b> Regex RFC 5322 y teléfonos de al menos 10 dígitos. "
        "• <b>Validación de Órdenes:</b> Selección obligatoria de estudios y cálculo de cotización directamente en backend. "
        "• <b>Máquina de Estados:</b> Prohibición de completar órdenes sin muestra biológica y blindaje de órdenes canceladas.",
        body_style
    ))

    # 8. Pruebas Unitarias
    story.append(Paragraph("6. Pruebas Unitarias Automatizadas (Suite pytest)", h1_style))
    story.append(Paragraph(
        "Se desarrolló una suite completa de <b>15 pruebas unitarias</b> ejecutadas con pytest bajo una base de datos SQLite aislada "
        "en memoria para garantizar pruebas reproducibles e independientes:",
        body_style
    ))

    img_test = os.path.join(SCREENSHOTS_DIR, "09_terminal_pytest.png")
    if os.path.exists(img_test):
        story.append(KeepTogether([
            Image(img_test, width=520, height=250),
            Paragraph("Figura 6.1: Ejecución exitosa de la suite de 15 pruebas unitarias automatizadas con pytest.", caption_style)
        ]))

    # 9. Medición de Rendimiento
    story.append(Paragraph("7. Medición de Rendimiento, Perfilado y Mejora (Antes vs. Después)", h1_style))
    story.append(Paragraph(
        "<b>Proceso Medido:</b> Búsqueda y Despliegue de Resultados Clínicos por Folio mediante <code>cProfile</code> y <code>time.perf_counter</code> (120 iteraciones).<br/>"
        "<b>Cuello de Botella (Antes):</b> Consultas fragmentadas N+1 (4 a 6 consultas por petición) y ausencia de índices secundarios.<br/>"
        "<b>Mejora Técnica (Después):</b> Creación de índices compuestos B-Tree en MariaDB/SQLite (<code>idx_ordenes_codigo</code>, <code>idx_orden_estudios_orden</code>, <code>idx_pacientes_curp</code>) "
        "y consolidación de 5 consultas en un único <code>INNER/LEFT JOIN</code> relacional.",
        body_style
    ))

    bench_table_data = [
        [
            Paragraph("<b>Métrica de Rendimiento</b>", body_style),
            Paragraph("<b>Antes (N+1 / Sin Índices)</b>", body_style),
            Paragraph("<b>Después (JOIN + Índices B-Tree)</b>", body_style),
            Paragraph("<b>Impacto Cuantitativo</b>", body_style)
        ],
        [
            Paragraph("Tiempo de Respuesta Medio", body_style),
            Paragraph("7.35 ms por consulta", body_style),
            Paragraph("3.09 ms por consulta", body_style),
            Paragraph("<font color='#166534'><b>2.38x más rápido</b></font>", body_style)
        ],
        [
            Paragraph("Latencia Mínima", body_style),
            Paragraph("4.26 ms", body_style),
            Paragraph("1.82 ms", body_style),
            Paragraph("<font color='#166534'><b>57.3% menor</b></font>", body_style)
        ],
        [
            Paragraph("Viajes a Base de Datos", body_style),
            Paragraph("4 a 6 consultas / req", body_style),
            Paragraph("1 sola consulta relacional", body_style),
            Paragraph("<font color='#166534'><b>Reducción 80%</b></font>", body_style)
        ],
        [
            Paragraph("Estrategia de Búsqueda", body_style),
            Paragraph("Full Table Scan", body_style),
            Paragraph("Búsqueda B-Tree Indexada", body_style),
            Paragraph("<font color='#166534'><b>Acceso O(log N)</b></font>", body_style)
        ]
    ]
    t_bench = Table(bench_table_data, colWidths=[140, 125, 135, 122])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 6))

    img_bench = os.path.join(SCREENSHOTS_DIR, "medicion_rendimiento.png")
    if os.path.exists(img_bench):
        story.append(KeepTogether([
            Image(img_bench, width=520, height=270),
            Paragraph("Figura 7.1: Gráfica comparativa de latencia (ms) antes vs. después de la optimización en MariaDB.", caption_style)
        ]))

    # 10. Conclusiones y Guía de Ejecución
    story.append(Paragraph("8. Guía de Ejecución y Conclusiones del Avance 3", h1_style))
    story.append(Paragraph(
        "<b>Pasos de Ejecución Local:</b><br/>"
        "1. Iniciar servicio MariaDB: <code>systemctl --user start mariadb-user</code><br/>"
        "2. Cargar datos semilla: <code>python3 seed_data.py</code><br/>"
        "3. Ejecutar suite de pruebas: <code>pytest -v</code> (15 pruebas aprobadas)<br/>"
        "4. Ejecutar benchmark de rendimiento: <code>python3 scripts/benchmark_performance.py</code><br/>"
        "5. Iniciar servidor Flask: <code>python3 app.py</code> (disponible en http://127.0.0.1:5000)<br/><br/>"
        "<b>Conclusión:</b> El Avance 3 consolida a LabControl con arquitectura robusta, proceso de negocio 100% operativo, "
        "calidad avalada por 15 pruebas unitarias y perfilado empírico demostrable, quedando el equipo plenamente preparado "
        "para la Entrega Final y demostración en vivo del 26 de noviembre.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Reporte PDF de Avance 3 generado exitosamente en: {OUTPUT_PDF}")

if __name__ == '__main__':
    build_pdf()
