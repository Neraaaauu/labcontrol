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
OUTPUT_PDF = os.path.join(DOCS_DIR, "Avance_2_LabControl_Prototipo_Funcional.pdf")

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
            self.drawString(45, 755, "UABC / HDS — LabControl: Reporte de Avance 2 (Prototipo Funcional)")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(45, 747, 567, 747)

        # Footer
        footer_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(567, 30, footer_text)
        self.drawString(45, 30, "LabControl — Sistema Integral de Laboratorio Clínico (MariaDB + Flask)")
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
        leading=10,
        textColor=COLOR_MUTED,
        alignment=1,  # Center
        spaceBefore=3,
        spaceAfter=8
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=COLOR_NAVY
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=COLOR_DARK
    )

    story = []

    # 1. Encabezado Institucional
    story.append(Paragraph("UNIVERSIDAD AUTÓNOMA DE BAJA CALIFORNIA", title_inst))
    story.append(Paragraph("Facultad de Ciencias Químicas e Ingeniería / FCITEC &bull; Ingeniería en Software y Tecnologías Emergentes<br/>Herramientas de Desarrollo de Software (HDS)", sub_inst))
    story.append(Paragraph("REPORTE DE AVANCE 2: PROTOTIPO FUNCIONAL EJECUTABLE<br/>SISTEMA WEB: LABCONTROL (LABORATORIO CLÍNICO)", report_title))

    # Tabla de Metadatos
    meta_data = [
        [Paragraph("<b>Materia y Fase:</b>", table_cell), Paragraph("Herramientas de Desarrollo de Software &bull; <b>Avance 2 (Prototipo Funcional)</b>", table_cell)],
        [Paragraph("<b>Sistema Desarrollado:</b>", table_cell), Paragraph("Opción 1: <b>LabControl</b> (Gestión de Pacientes, Órdenes, Catálogo y Muestras)", table_cell)],
        [Paragraph("<b>Integrantes:</b>", table_cell), Paragraph("Adrian Gómez / Equipo de Desarrollo HDS", table_cell)],
        [Paragraph("<b>Base de Datos y Framework:</b>", table_cell), Paragraph("<b>MariaDB 10.11+ (Linux mariadb-user)</b> &bull; Fallback SQLite &bull; <b>Flask 3.1.3</b>", table_cell)],
        [Paragraph("<b>Estado del Entregable:</b>", table_cell), Paragraph("<b>100% Operativo</b>: Software ejecutable con MariaDB, login, 2 roles, 2 módulos y API.", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[150, 372])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 1. Resumen Ejecutivo
    story.append(Paragraph("1. Resumen Ejecutivo del Avance 2", h1_style))
    story.append(Paragraph(
        "En cumplimiento con la rúbrica oficial de la asignatura para el Avance 2 (<i>«Aplicación ejecutable con base de datos, "
        "login, 2 roles, 2 módulos principales y formularios básicos. Mostrar el avance funcionando»</i>), se ha desarrollado "
        "una versión de software plenamente operativa y ejecutable localmente para el sistema <b>LabControl</b>. "
        "A diferencia de un diseño estático o maquetas no funcionales, el sistema cuenta con un backend en Flask, "
        "base de datos relacional MariaDB inicializada con datos semilla ficticios realistas, autenticación mediante sesiones cifradas, "
        "control de acceso basado en 2 roles (Administrador y Usuario Recepcionista), integración de API externa para consulta de domicilios "
        "por Código Postal con tolerancia a fallos, y el flujo de trabajo clínico completo.",
        body_style
    ))

    # 2. Arquitectura de Base de Datos y Persistencia
    story.append(Paragraph("2. Arquitectura de Base de Datos y Persistencia en MariaDB", h1_style))
    story.append(Paragraph(
        "El sistema opera de forma nativa sobre el gestor relacional <b>MariaDB 10.11+</b> en Linux mediante el servicio de usuario "
        "<code>mariadb-user</code> (conexión directa por socket UNIX con <code>pymysql</code>). El modelo de datos estructurado en la base "
        "<code>labcontrol</code> garantiza consistencia e integridad referencial estricta mediante restricciones de claves foráneas "
        "(<code>FOREIGN KEY ON DELETE CASCADE / RESTRICT</code>) e índices únicos sobre CURP, usuarios y códigos de órdenes. "
        "Adicionalmente, se incluye un mecanismo de compatibilidad y fallback transparente a <b>SQLite3</b> para portabilidad:",
        body_style
    ))

    db_rows = [
        [Paragraph("Tabla", table_header), Paragraph("Atributos Clave", table_header), Paragraph("Rol en el Negocio", table_header)],
        [Paragraph("<b>usuarios</b>", table_cell), Paragraph("id (PK), username, password_hash, nombre, rol, activo", table_cell), Paragraph("Control de acceso y permisos para los 2 roles (admin y usuario).", table_cell)],
        [Paragraph("<b>pacientes</b>", table_cell), Paragraph("id (PK), nombre, apellido, curp (UNIQUE), nacimiento, CP, colonia", table_cell), Paragraph("Expedientes de pacientes con datos sociodemográficos.", table_cell)],
        [Paragraph("<b>estudios</b>", table_cell), Paragraph("id (PK), codigo, nombre, categoria, tipo_muestra, precio, tiempo_hrs", table_cell), Paragraph("Catálogo de análisis clínicos con tipo de muestra y ayuno.", table_cell)],
        [Paragraph("<b>ordenes</b>", table_cell), Paragraph("id (PK), codigo_orden (ORD-XXXX), paciente_id (FK), usuario_id, estado, total", table_cell), Paragraph("Solicitudes de estudio y trazabilidad de muestras biológicas.", table_cell)],
        [Paragraph("<b>orden_estudios</b>", table_cell), Paragraph("id (PK), orden_id (FK), estudio_id (FK), precio_unitario, resultado_texto", table_cell), Paragraph("Detalle de pruebas por orden y captura de parámetros analíticos.", table_cell)]
    ]
    t_db = Table(db_rows, colWidths=[90, 210, 222])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 8))

    img_diag = os.path.join(SCREENSHOTS_DIR, "00_esquema_base_datos.png")
    if os.path.exists(img_diag):
        story.append(Image(img_diag, width=470, height=240))
        story.append(Paragraph("Figura 2.1: Esquema Relacional de Base de Datos en MariaDB (InnoDB)", caption_style))

    # 3. Módulo de Autenticación y 2 Roles
    story.append(Paragraph("3. Módulo de Autenticación y Control de Acceso por Roles", h1_style))
    story.append(Paragraph(
        "Se implementó el inicio y cierre de sesión con verificación de credenciales seguras mediante hashes criptográficos "
        "con Werkzeug Security (<code>pbkdf2:sha256</code>) y decoradores <code>@login_required</code> y <code>@admin_required</code>. Se verificaron los dos roles:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Rol Administrador (admin):</b> Usuario <code>admin</code> (pass: <code>admin123</code>). Representa al Químico Bioquímico en Jefe. Posee control total: actualización de muestras a 'En Análisis', captura de resultados analíticos y alta en el catálogo.", bullet_style))
    story.append(Paragraph("&bull; <b>Rol Usuario Operativo (usuario):</b> Usuario <code>recepcion</code> (pass: <code>recepcion123</code>). Representa a Recepción. Puede registrar pacientes, cotizar y crear solicitudes de laboratorio y marcar muestras recibidas en ventanilla.", bullet_style))

    img_login = os.path.join(SCREENSHOTS_DIR, "01_login_roles.png")
    if os.path.exists(img_login):
        story.append(Image(img_login, width=470, height=220))
        story.append(Paragraph("Figura 2.2: Pantalla de inicio de sesión con selectores rápidos para los dos roles de prueba", caption_style))

    # 4. Módulo 1: Pacientes y API de C.P.
    story.append(Paragraph("4. Módulo 1: Directorio de Pacientes y Consumo de API Externa", h1_style))
    story.append(Paragraph(
        "Permite registrar, buscar y consultar expedientes de pacientes con validación obligatoria de nombres, apellidos y formato estricto de CURP de 18 caracteres. "
        "<br/><b>Tolerancia a fallos en la API de Código Postal:</b> Cumpliendo la directriz oficial (<i>«el sistema no debe dejar de funcionar totalmente si el servicio externo falla»</i>), "
        "se integró la API pública de Zippopotam.us. Al teclear el C.P. de 5 dígitos, se autocompleta Estado, Municipio y Colonias. "
        "Si no hay conexión de red o la API falla, entra en operación un caché local de respaldo y los campos permanecen editables manualmente sin bloquear al operador.",
        body_style
    ))

    img_pac = os.path.join(SCREENSHOTS_DIR, "04_pacientes_alta_api.png")
    if os.path.exists(img_pac):
        story.append(Image(img_pac, width=470, height=225))
        story.append(Paragraph("Figura 2.3: Formulario de alta de paciente asistido por API de Código Postal con respaldo offline", caption_style))

    # 5. Módulo 2: Órdenes y Muestras
    story.append(Paragraph("5. Módulo 2: Órdenes de Laboratorio y Trazabilidad de Muestras", h1_style))
    story.append(Paragraph(
        "Permite asociar un paciente a uno o múltiples estudios del catálogo clínico. Un script JavaScript recalcula en tiempo real el importe total ($ MXN). "
        "El backend genera un código de orden único e irrepetible (formato <code>ORD-2026-XXXX</code>) que sirve de folio para rotulación de tubos biológicos y consulta del paciente. "
        "Se incluye una línea de proceso continua que refleja los estados de custodia: <b>Pendiente Toma &rarr; Muestra Recibida &rarr; En Análisis &rarr; Completada</b>.",
        body_style
    ))

    img_ord = os.path.join(SCREENSHOTS_DIR, "06_orden_nueva_cotizacion.png")
    if os.path.exists(img_ord):
        story.append(Image(img_ord, width=470, height=230))
        story.append(Paragraph("Figura 2.4: Formulario de generación de orden con cotización viva y selección de estudios", caption_style))

    # 6. Demostración del Flujo de Trabajo Principal
    story.append(Paragraph("6. Demostración del Flujo de Trabajo Principal", h1_style))
    story.append(Paragraph(
        "El sistema cumple puntualmente la secuencia de demostración requerida en la guía oficial: "
        "<b>Registrar paciente &rarr; crear orden &rarr; marcar muestra recibida &rarr; actualizar estado de la orden</b>.",
        body_style
    ))
    story.append(Paragraph("1. Se da de alta al paciente mediante el formulario con autocompletado de domicilio por C.P.", bullet_style))
    story.append(Paragraph("2. Se genera la orden seleccionando las pruebas requeridas (ej. Biometría Hemática y Glucosa).", bullet_style))
    story.append(Paragraph("3. Personal de ventanilla recibe los tubos rotulados y presiona 'Marcar Muestra Recibida', registrando la hora exacta.", bullet_style))
    story.append(Paragraph("4. El químico traslada la muestra al estado 'En Análisis' y finalmente a 'Completada', capturando los hallazgos analíticos.", bullet_style))

    img_det = os.path.join(SCREENSHOTS_DIR, "07_orden_detalle_completada.png")
    if os.path.exists(img_det):
        story.append(Image(img_det, width=470, height=230))
        story.append(Paragraph("Figura 2.5: Detalle de orden con trazabilidad de muestra y captura de parámetros analíticos", caption_style))

    # 7. Apartado para Consultar Resultados por Folio
    story.append(Paragraph("7. Apartado para Consultar Resultados por Código de Folio", h1_style))
    story.append(Paragraph(
        "En apego al requerimiento específico (<i>«Apartado para buscar los resultados de análisis mediante algún código»</i>), "
        "se desarrolló la ruta pública <code>/consultar</code>. Pacientes o médicos pueden ingresar su folio (ej. <code>ORD-2026-1001</code>) "
        "para consultar en línea el estado de su muestra y visualizar los resultados validados sin requerir inicio de sesión.",
        body_style
    ))

    img_pub = os.path.join(SCREENSHOTS_DIR, "10_consulta_publica_resultados.png")
    if os.path.exists(img_pub):
        story.append(Image(img_pub, width=470, height=220))
        story.append(Paragraph("Figura 2.6: Portal público de consulta de resultados por código de folio", caption_style))

    # 8. Verificación de Calidad y Pruebas Unitarias
    story.append(Paragraph("8. Calidad de Software y Pruebas Unitarias Automatizadas", h1_style))
    story.append(Paragraph(
        "Se construyó una suite de <b>8 pruebas unitarias automatizadas con pytest</b> (<code>tests/test_labcontrol.py</code>) "
        "que evalúan autenticación, protección de rutas, validación de CURP, resiliencia de la API de C.P., cálculo aritmético de totales "
        "y transiciones de estado de muestra. La suite se ejecuta en memoria y base de datos aislada con <b>100% de éxito</b>:",
        body_style
    ))

    img_test = os.path.join(SCREENSHOTS_DIR, "09_terminal_pytest.png")
    if os.path.exists(img_test):
        story.append(Image(img_test, width=470, height=135))
        story.append(Paragraph("Figura 2.7: Ejecución exitosa de la suite de 8 pruebas unitarias con pytest (100% aprobadas)", caption_style))

    # 9. Guía de Ejecución Local
    story.append(Paragraph("9. Guía de Ejecución Local para Evaluación", h1_style))
    story.append(Paragraph(
        "<b>Opción A — En Linux (MariaDB nativo):</b><br/>"
        "&bull; <b>Directorio:</b> <code>cd /home/adrian/proyectos/labcontrol</code><br/>"
        "&bull; <b>Servicio MariaDB:</b> <code>systemctl --user start mariadb-user</code><br/>"
        "&bull; <b>Semilla y Servidor:</b> <code>./run.sh</code> o <code>python3 app.py</code> (URL: <code>http://127.0.0.1:5000</code>)<br/>"
        "&bull; <b>Credenciales:</b> Admin: <code>admin</code> / <code>admin123</code> &bull; Usuario: <code>recepcion</code> / <code>recepcion123</code><br/>"
        "&bull; <b>Pruebas Unitarias:</b> <code>pytest -v</code><br/><br/>"
        "<b>Opción B — En Windows (CMD / PowerShell):</b><br/>"
        "&bull; <b>Directorio:</b> <code>cd C:\\ruta\\hacia\\labcontrol</code><br/>"
        "&bull; <b>Dependencias:</b> <code>pip install -r requirements.txt</code><br/>"
        "&bull; <b>Base de Datos:</b> Iniciar MySQL en XAMPP (opcional; si no hay servidor activo, entra respaldo SQLite transparente)<br/>"
        "&bull; <b>Semilla y Servidor:</b> Doble clic en <code>run.bat</code> o ejecutar <code>python app.py</code> (URL: <code>http://127.0.0.1:5000</code>)<br/>"
        "&bull; <b>Pruebas Unitarias:</b> <code>pytest -v</code>",
        body_style
    ))

    # Construir documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado con éxito: {OUTPUT_PDF}")

if __name__ == '__main__':
    build_pdf()
