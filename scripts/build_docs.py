import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = "/home/adrian/proyectos/labcontrol"
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

COLOR_NAVY = RGBColor(11, 94, 215)
COLOR_DARK = RGBColor(33, 37, 41)
COLOR_GRAY = RGBColor(108, 117, 125)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece márgenes internos en celdas (en dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D0D7DE"):
    """Aplica bordes discretos a una tabla."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def format_doc_base(doc):
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

def add_heading_1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return h

def add_heading_2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_DARK
    return h

def add_paragraph(doc, text, bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10.5)
    run.font.italic = italic
    run.font.color.rgb = COLOR_DARK
    return p

def add_bullet(doc, text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(10.5)
    return p

# ==============================================================================
# GENERACIÓN DE AVANCE 1: ANÁLISIS Y DISEÑO (2 a 3 páginas)
# ==============================================================================
def build_avance_1():
    doc = Document()
    format_doc_base(doc)

    # Encabezado institucional
    p_header = doc.add_paragraph()
    p_header.paragraph_format.space_after = Pt(2)
    r1 = p_header.add_run("UNIVERSIDAD AUTÓNOMA DE BAJA CALIFORNIA\n")
    r1.font.name = "Arial"
    r1.font.size = Pt(12)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_NAVY
    r2 = p_header.add_run("Facultad de Ciencias Químicas e Ingeniería / FCITEC\nIngeniería en Software y Tecnologías Emergentes\nHerramientas de Desarrollo de Software (HDS)")
    r2.font.name = "Arial"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_GRAY

    # Título del reporte
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(6)
    r_tit = p_title.add_run("AVANCE 1: ANÁLISIS Y DISEÑO DE SISTEMA WEB\nPROYECTO: LABCONTROL (LABORATORIO CLÍNICO)")
    r_tit.font.name = "Arial"
    r_tit.font.size = Pt(14)
    r_tit.font.bold = True
    r_tit.font.color.rgb = COLOR_DARK

    # Tabla de datos generales
    table_meta = doc.add_table(rows=4, cols=2)
    set_table_borders(table_meta)
    meta_info = [
        ("Materia y Entrega:", "Herramientas de Desarrollo de Software - Avance 1 (Análisis y Diseño)"),
        ("Sistema Seleccionado:", "Opción 1: LabControl | Gestión de Solicitudes y Muestras de Laboratorio Clínico"),
        ("Integrantes:", "Adrian Gómez / Equipo de Desarrollo HDS"),
        ("Tecnologías Principales:", "Python 3.12, Flask 3.1, MariaDB 10.11+ Relacional (Linux), Jinja2, Bootstrap 5, API Zippopotam/SEPOMEX")
    ]
    for row_idx, (k, v) in enumerate(meta_info):
        c0 = table_meta.cell(row_idx, 0)
        c1 = table_meta.cell(row_idx, 1)
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # 1. Sistema Elegido y Objetivo
    add_heading_1(doc, "1. Sistema Elegido y Objetivo del Proyecto")
    add_paragraph(doc, 
        "Para el proyecto integrador de la asignatura, se seleccionó el sistema LabControl (Laboratorio Clínico). "
        "El objetivo principal es administrar de manera ágil y ordenada el flujo operativo de un laboratorio de análisis clínicos pequeño. "
        "El sistema resuelve el problema del registro manual o desordenado de pacientes, la selección de estudios médicos según catálogo, "
        "la recepción física y trazabilidad del estado de las muestras biológicas (tubos de sangre, frascos de orina/heces), "
        "así como la consulta oportuna de resultados analíticos mediante un folio único y rastreable.",
        bold_prefix="Propósito: ")

    # 2. Funciones Principales y Demostración
    add_heading_1(doc, "2. Funciones Principales y Alcance (MVP)")
    add_paragraph(doc, "El sistema implementa las funciones requeridas para el MVP funcional:")
    add_bullet(doc, "Administración de expedientes con validaciones y autocompletado de domicilio asistido por API.", bold_prefix="Módulo de Pacientes: ")
    add_bullet(doc, "Listado de análisis clínicos con categoría, tipo de muestra, indicaciones de ayuno y costo.", bold_prefix="Catálogo de Estudios: ")
    add_bullet(doc, "Generación de solicitudes con uno o múltiples estudios y cálculo dinámico de importe.", bold_prefix="Órdenes de Laboratorio: ")
    add_bullet(doc, "Línea de tiempo con estados: Pendiente de Toma → Muestra Recibida → En Análisis → Completada.", bold_prefix="Trazabilidad de Muestras: ")
    add_bullet(doc, "Portal accesible para pacientes y médicos ingresando el código de folio (ej. ORD-2026-1001).", bold_prefix="Consulta por Código: ")
    add_bullet(doc, "Demostración completa del ciclo: Registrar paciente → Crear orden → Marcar muestra recibida → Actualizar estado.", bold_prefix="Flujo Principal: ")

    # 3. Framework y Arquitectura
    add_heading_1(doc, "3. Framework Elegido y Justificación Técnica")
    add_paragraph(doc, 
        "Se eligió Python con el microframework Flask (v3.1.3) por su arquitectura limpia, ligera y altamente mantenible, "
        "cumpliendo con creces los requerimientos del curso. Se utiliza MariaDB 10.11+ como motor relacional primario (con servicio mariadb-user en Linux) "
        "garantizando integridad referencial estricta mediante restricciones FOREIGN KEY entre pacientes, usuarios, órdenes y estudios. "
        "En la capa de presentación se emplea Jinja2 y Bootstrap 5 para una interfaz responsive, accesible y profesional adaptada al entorno clínico.",
        bold_prefix="Stack Tecnológico: ")

    # 4. Esquema de Base de Datos
    add_heading_1(doc, "4. Esquema Relacional de Base de Datos")
    add_paragraph(doc, 
        "El modelo relacional consta de 5 entidades normalizadas con integridad referencial completa:")
    add_bullet(doc, "id (PK), username, password_hash (Werkzeug), nombre_completo, rol ('admin' | 'usuario'), activo.", bold_prefix="usuarios: ")
    add_bullet(doc, "id (PK), nombre, apellido, curp (UNIQUE), fecha_nacimiento, sexo, telefono, email, codigo_postal, colonia, municipio, estado, direccion_calle.", bold_prefix="pacientes: ")
    add_bullet(doc, "id (PK), codigo (UNIQUE), nombre, categoria, tipo_muestra, indicaciones, precio, tiempo_entrega_horas, activo.", bold_prefix="estudios: ")
    add_bullet(doc, "id (PK), codigo_orden (UNIQUE), paciente_id (FK), usuario_id (FK), estado_orden, total, metodo_pago, fecha_toma, fecha_recepcion, fecha_completada.", bold_prefix="ordenes: ")
    add_bullet(doc, "id (PK), orden_id (FK ON DELETE CASCADE), estudio_id (FK), precio_unitario, estado_estudio, resultado_texto, valores_referencia.", bold_prefix="orden_estudios: ")

    diagram_path = os.path.join(DOCS_DIR, "esquema_base_datos.png")
    if os.path.exists(diagram_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(diagram_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 1.1: Diagrama Entidad-Relación de LabControl (MariaDB)")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 5. Diseño de Interfaz (3 Pantallas Figma)
    add_heading_1(doc, "5. Diseño de Interfaz (3 Pantallas Prototipadas)")
    add_paragraph(doc, 
        "Se diseñaron 3 pantallas clave siguiendo una guía visual médica orientada a la usabilidad y rapidez en ventanilla:")
    add_bullet(doc, "Métricas en tiempo real (pendientes, recibidas, en análisis, completadas) y accesos rápidos.", bold_prefix="Pantalla 1 - Dashboard Clínico: ")
    add_bullet(doc, "Expediente asistido por la API de Código Postal con autocompletado y validación de CURP.", bold_prefix="Pantalla 2 - Alta de Paciente con API: ")
    add_bullet(doc, "Selección dinámica de pruebas, cotización automática y panel de recepción de muestras.", bold_prefix="Pantalla 3 - Creación y Trazabilidad de Orden: ")

    # 6. Repositorio y Plan
    add_heading_1(doc, "6. Repositorio GitHub y Plan de Trabajo")
    add_paragraph(doc, 
        "El código fuente se gestiona bajo control de versiones Git en un repositorio local y remoto en GitHub. "
        "Cuenta con archivo .gitignore para omitir entornos y archivos temporales, un README.md detallado con guía de arranque, "
        "scripts de siembra de base de datos (seed_data.py) y una suite de pruebas automatizadas con pytest.",
        bold_prefix="Control de Versiones: ")

    out_file = os.path.join(DOCS_DIR, "Avance_1_LabControl_Analisis_y_Diseno.docx")
    doc.save(out_file)
    print(f"Documento de Avance 1 generado con éxito: {out_file}")

# ==============================================================================
# GENERACIÓN DE AVANCE 2: PROTOTIPO FUNCIONAL (Reporte Extenso con Evidencias)
# ==============================================================================
def build_avance_2():
    doc = Document()
    format_doc_base(doc)

    # Encabezado institucional
    p_header = doc.add_paragraph()
    p_header.paragraph_format.space_after = Pt(2)
    r1 = p_header.add_run("UNIVERSIDAD AUTÓNOMA DE BAJA CALIFORNIA\n")
    r1.font.name = "Arial"
    r1.font.size = Pt(12)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_NAVY
    r2 = p_header.add_run("FACULTAD DE CIENCIAS QUÍMICAS E INGENIERÍA\nIngeniería en Software y Tecnologías Emergentes\nHerramientas de Desarrollo de Software (HDS)")
    r2.font.name = "Arial"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = COLOR_GRAY

    # Título del reporte
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(6)
    r_tit = p_title.add_run("REPORTE DE AVANCE 2: PROTOTIPO FUNCIONAL EJECUTABLE\nSISTEMA WEB: LABCONTROL (LABORATORIO CLÍNICO)")
    r_tit.font.name = "Arial"
    r_tit.font.size = Pt(14)
    r_tit.font.bold = True
    r_tit.font.color.rgb = COLOR_DARK

    # Tabla de metadatos
    table_meta = doc.add_table(rows=6, cols=2)
    set_table_borders(table_meta)
    meta_info = [
        ("Materia y Fase:", "Herramientas de Desarrollo de Software - Avance 2 (Prototipo Funcional)"),
        ("Sistema Desarrollado:", "LabControl (Gestión de Pacientes, Órdenes, Catálogo y Muestras de Laboratorio)"),
        ("Integrantes:", "Adrian Gómez / Equipo de Desarrollo HDS"),
        ("Base de Datos y Framework:", "MariaDB 10.11+ (Linux mariadb-user) / Fallback SQLite | Flask 3.1.3"),
        ("Fecha de Entrega:", "Miércoles 18 de noviembre de 2026"),
        ("Estado del Avance:", "100% Cumplido: Software ejecutable con MariaDB, 2 roles, 2 módulos y API integrados.")
    ]
    for row_idx, (k, v) in enumerate(meta_info):
        c0 = table_meta.cell(row_idx, 0)
        c1 = table_meta.cell(row_idx, 1)
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # 1. Resumen Ejecutivo
    add_heading_1(doc, "1. Resumen Ejecutivo del Avance 2")
    add_paragraph(doc, 
        "En cumplimiento con la rúbrica oficial de la materia para el Avance 2 ('Aplicación ejecutable con base de datos, "
        "login, 2 roles, 2 módulos principales y formularios básicos. Mostrar el avance funcionando'), se ha desarrollado "
        "una versión de software plenamente operativa y ejecutable localmente para el sistema LabControl. "
        "A diferencia de un boceto o conjunto de imágenes estáticas, el sistema cuenta con servidor backend en Flask, "
        "base de datos relacional MariaDB (base de datos 'labcontrol' en Linux) inicializada con datos semilla ficticios realistas, "
        "autenticación robusta mediante sesiones cifradas, control de acceso basado en roles (Administrador y Usuario Recepcionista), "
        "integración de API externa para domicilios y un flujo completo de captura, cálculo y cambio de estados de muestras clínicas.",
        bold_prefix="Logro del Avance: ")

    # 2. Arquitectura de Base de Datos y Persistencia
    add_heading_1(doc, "2. Arquitectura de Base de Datos y Persistencia en MariaDB")
    add_paragraph(doc, 
        "El sistema opera de forma nativa sobre el gestor de base de datos relacional MariaDB 10.11+ en Linux "
        "(ejecutado mediante el servicio 'systemctl --user start mariadb-user' y conectado vía socket UNIX con PyMySQL). "
        "El modelo relacional garantiza integridad referencial absoluta mediante restricciones de claves foráneas "
        "(FOREIGN KEY ON DELETE RESTRICT / CASCADE) e índices únicos sobre CURP, username y folios de órdenes. "
        "Asimismo, se incluye una capa de abstracción con fallback transparente a SQLite3 para máxima portabilidad:")
    
    table_db = doc.add_table(rows=6, cols=3)
    set_table_borders(table_db)
    db_rows = [
        ("Tabla", "Campos Principales", "Descripción y Rol en el Negocio"),
        ("usuarios", "id (PK), username, password_hash, nombre_completo, rol, activo", "Control de acceso con 2 roles diferenciados ('admin' y 'usuario')."),
        ("pacientes", "id (PK), nombre, apellido, curp, nacimiento, sexo, telefono, CP, colonia, direccion", "Expedientes clínicos únicos de pacientes atendidos en el laboratorio."),
        ("estudios", "id (PK), codigo, nombre, categoria, tipo_muestra, indicaciones, precio, tiempo_hrs", "Catálogo maestro de estudios clínicos con precios y requerimientos de ayuno."),
        ("ordenes", "id (PK), codigo_orden (ORD-XXXX), paciente_id (FK), usuario_id (FK), estado_orden, total", "Solicitudes de estudio y trazabilidad del estado de las muestras biológicas."),
        ("orden_estudios", "id (PK), orden_id (FK), estudio_id (FK), precio_unitario, resultado_texto", "Detalle de estudios por orden y captura de resultados analíticos de laboratorio.")
    ]
    for row_idx, (c_name, c_fields, c_desc) in enumerate(db_rows):
        c0 = table_db.cell(row_idx, 0)
        c1 = table_db.cell(row_idx, 1)
        c2 = table_db.cell(row_idx, 2)
        c0.width = Inches(1.3)
        c1.width = Inches(2.7)
        c2.width = Inches(2.7)
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
        set_cell_margins(c2, 60, 60, 80, 80)
        if row_idx == 0:
            for c, txt in [(c0, c_name), (c1, c_fields), (c2, c_desc)]:
                r = c.paragraphs[0].add_run(txt)
                r.font.bold = True
                r.font.size = Pt(9)
                r.font.color.rgb = COLOR_NAVY
        else:
            c0.paragraphs[0].add_run(c_name).font.bold = True
            c0.paragraphs[0].runs[0].font.size = Pt(8.5)
            c1.paragraphs[0].add_run(c_fields).font.size = Pt(8.5)
            c2.paragraphs[0].add_run(c_desc).font.size = Pt(8.5)

    add_paragraph(doc, "El script 'seed_data.py' inicializa de manera automática la base de datos con cuentas de prueba, 8 estudios representativos, 5 pacientes y 4 órdenes en diferentes fases de avance.", bold_prefix="Carga de Datos Semilla: ")

    diagram_path = os.path.join(SCREENSHOTS_DIR, "00_esquema_base_datos.png")
    if os.path.exists(diagram_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(diagram_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2.1: Esquema Relacional de Base de Datos en MariaDB (InnoDB)")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 3. Módulo de Autenticación y 2 Roles
    add_heading_1(doc, "3. Módulo de Autenticación y Control de Acceso por Roles")
    add_paragraph(doc, 
        "La seguridad del sistema se basa en sesiones de servidor firmadas criptográficamente y contraseñas hasheadas "
        "con algoritmos seguros mediante Werkzeug Security (pbkdf2:sha256). Se definieron y verificaron los 2 roles solicitados:")
    add_bullet(doc, "Usuario 'admin' (pass: admin123). Representa al Químico Farmacobiólogo en Jefe. Tiene privilegios para consultar y modificar pacientes, crear órdenes, recibir muestras, cambiar estados a análisis, capturar valores analíticos y administrar el catálogo de estudios.", bold_prefix="Rol 1 - Administrador (admin): ")
    add_bullet(doc, "Usuario 'recepcion' (pass: recepcion123). Representa a la Recepción y Atención a Pacientes. Puede dar de alta pacientes con autocompletado por API, crear solicitudes de estudio, calcular totales y marcar muestras recibidas en ventanilla.", bold_prefix="Rol 2 - Usuario Operativo (usuario): ")

    img_login = os.path.join(SCREENSHOTS_DIR, "01_login_roles.png")
    if os.path.exists(img_login):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_login, width=Inches(5.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2.2: Pantalla de inicio de sesión con botones de prueba para los 2 roles")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 4. Módulo 1: Pacientes y API de Código Postal
    add_heading_1(doc, "4. Módulo 1: Padrón de Pacientes y Consumo de API Externa")
    add_paragraph(doc, 
        "El módulo de pacientes permite registrar, consultar, buscar y modificar la información de los pacientes. "
        "Incluye validación obligatoria de nombres, apellidos y formato estricto de CURP de 18 caracteres.")
    add_paragraph(doc, 
        "Integración de la API Externa de Código Postal: Cumpliendo con el requerimiento del PDF ('API sugerida: Consulta de código postal "
        "para apoyar la captura de domicilio. El sistema no debe dejar de funcionar totalmente si el servicio externo falla'), "
        "se integró la API pública de Zippopotam.us (http://api.zippopotam.us/mx/{cp}) conectada al frontend. "
        "Al teclear los 5 dígitos del código postal o presionar el botón de búsqueda, el sistema autocompleta Estado, Municipio y "
        "despliega las Colonias asociadas. Si el servicio externo presenta fallas o no hay red, entra en operación un mecanismo "
        "de respaldo local (caché offline) y los campos permanecen editables manualmente, garantizando disponibilidad total sin bloqueos.",
        bold_prefix="Tolerancia a Fallos de la API: ")

    img_pac = os.path.join(SCREENSHOTS_DIR, "04_pacientes_alta_api.png")
    if os.path.exists(img_pac):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_pac, width=Inches(5.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2.3: Formulario de alta de paciente con autocompletado mediante API de Código Postal")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 5. Módulo 2: Órdenes y Trazabilidad de Muestras
    add_heading_1(doc, "5. Módulo 2: Órdenes de Laboratorio y Recepción de Muestras")
    add_paragraph(doc, 
        "El segundo módulo principal gestiona el núcleo de negocio del laboratorio clínico:")
    add_bullet(doc, "Permite seleccionar un paciente registrado y marcar uno o múltiples estudios del catálogo. Un script JavaScript recalcula en tiempo real el importe total ($ MXN) y cuenta los estudios seleccionados.", bold_prefix="Creación de Orden con Cotización Dinámica: ")
    add_bullet(doc, "El backend genera automáticamente un identificador alfanumérico único (ej. ORD-2026-1002) que servirá para rotular los tubos de ensayo y para la consulta del paciente.", bold_prefix="Generación de Folio Rastreable: ")
    add_bullet(doc, "Se implementó una línea de tiempo visual que muestra las 4 fases de la muestra: 1. Orden Registrada, 2. Muestra Recibida, 3. En Análisis, 4. Resultados Listos.", bold_prefix="Control de Estados de la Muestra: ")

    img_orden_nueva = os.path.join(SCREENSHOTS_DIR, "06_orden_nueva_cotizacion.png")
    if os.path.exists(img_orden_nueva):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_orden_nueva, width=Inches(5.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2.4: Formulario de creación de orden con cálculo automático y selección de estudios")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 6. Demostración del Flujo Principal
    add_heading_1(doc, "6. Demostración del Flujo de Trabajo Principal")
    add_paragraph(doc, 
        "La guía de la materia establece como demostración principal la siguiente secuencia: "
        "'Registrar paciente → crear orden → marcar muestra recibida → actualizar estado de la orden'. "
        "En LabControl este ciclo se ejecuta de manera fluida:")
    add_bullet(doc, "Se capturan los datos en el módulo de pacientes con auxilio de la API de C.P. y se guarda el expediente.", bold_prefix="Paso 1: ")
    add_bullet(doc, "Desde el expediente o menú superior se seleccionan los estudios (ej. Biometría Hemática y Química Sanguínea) y se genera la orden.", bold_prefix="Paso 2: ")
    add_bullet(doc, "El personal de ventanilla confirma la recepción del tubo con anticoagulante EDTA o frasco presionando 'Marcar Muestra Recibida', registrando la hora exacta.", bold_prefix="Paso 3: ")
    add_bullet(doc, "El químico bioquímico traslada la orden al estado 'En Análisis' y finalmente a 'Completada', capturando los parámetros analíticos obtenidos.", bold_prefix="Paso 4: ")

    img_orden_det = os.path.join(SCREENSHOTS_DIR, "07_orden_detalle_completada.png")
    if os.path.exists(img_orden_det):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_orden_det, width=Inches(5.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2.5: Vista de seguimiento de orden con stepper de estados y captura de resultados analíticos")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 7. Apartado de Consulta de Resultados por Folio
    add_heading_1(doc, "7. Apartado para Consultar Resultados por Código")
    add_paragraph(doc, 
        "En apego al requerimiento específico de la guía ('Apartado para buscar los resultados de analisis mediante algun codigo'), "
        "se diseñó la ruta pública '/consultar'. Tanto pacientes como personal médico pueden ingresar el folio de orden (ej. ORD-2026-1001) "
        "sin necesidad de estar autenticados, visualizando el estado de procesamiento de su muestra y, una vez completada, "
        "los hallazgos analíticos validados con sus valores de referencia.",
        bold_prefix="Portal Paciente: ")

    img_pub = os.path.join(SCREENSHOTS_DIR, "10_consulta_publica_resultados.png")
    if os.path.exists(img_pub):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_pub, width=Inches(5.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2.6: Apartado de consulta de análisis clínicos mediante código de folio")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 8. Verificación de Calidad y Pruebas Automatizadas
    add_heading_1(doc, "8. Calidad de Software y Pruebas Unitarias Automatizadas")
    add_paragraph(doc, 
        "Para garantizar que el avance 2 no tenga fallas de regresión y cumpla con los estándares de ingeniería de software, "
        "se construyó una suite de 8 pruebas unitarias automatizadas con pytest ('tests/test_labcontrol.py') que prueban "
        "en memoria y con base de datos temporal:")
    add_bullet(doc, "Verifica el acceso correcto y diferenciación de roles para admin y usuario.", bold_prefix="test_login_exitoso_y_roles: ")
    add_bullet(doc, "Comprueba el rechazo de credenciales inválidas y emisión de alertas.", bold_prefix="test_login_invalido: ")
    add_bullet(doc, "Verifica que usuarios anónimos sean redirigidos a la vista de login.", bold_prefix="test_proteccion_rutas: ")
    add_bullet(doc, "Comprueba el alta correcta de paciente y el rechazo ante CURP duplicada.", bold_prefix="test_registro_paciente: ")
    add_bullet(doc, "Verifica respuesta de API externa y resiliencia del respaldo local.", bold_prefix="test_api_codigo_postal: ")
    add_bullet(doc, "Valida el cálculo aritmético correcto de precios y generación de folio.", bold_prefix="test_creacion_orden: ")
    add_bullet(doc, "Comprueba el ciclo de vida de la muestra (Pendiente → Recibida → Análisis → Completada).", bold_prefix="test_flujo_muestras: ")
    add_bullet(doc, "Comprueba la localización y despliegue público de resultados por código.", bold_prefix="test_consulta_publica: ")

    img_pytest = os.path.join(SCREENSHOTS_DIR, "09_terminal_pytest.png")
    if os.path.exists(img_pytest):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(img_pytest, width=Inches(5.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2.7: Ejecución exitosa de las 8 pruebas unitarias automatizadas con pytest (100% aprobadas)")
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_GRAY

    # 9. Guía de Ejecución Rápida
    add_heading_1(doc, "9. Guía de Ejecución Local para Evaluación")
    add_paragraph(doc, 
        "El sistema es multiplataforma y está preparado para ejecutarse tanto en Linux con MariaDB nativo como en Windows:")
    
    add_paragraph(doc, "Opción A: Ejecución en Linux (MariaDB nativo)", bold_prefix="")
    add_bullet(doc, "cd /home/adrian/proyectos/labcontrol", bold_prefix="1. Acceder al directorio: ")
    add_bullet(doc, "systemctl --user start mariadb-user (asegura que el servicio MariaDB esté activo)", bold_prefix="2. Iniciar MariaDB: ")
    add_bullet(doc, "python3 seed_data.py (inicializa la base 'labcontrol' y datos de prueba)", bold_prefix="3. Inicializar BD: ")
    add_bullet(doc, "python3 app.py o ./run.sh (inicia el servidor en http://127.0.0.1:5000)", bold_prefix="4. Iniciar servidor: ")
    add_bullet(doc, "Abrir en el navegador: http://127.0.0.1:5000", bold_prefix="5. Abrir en navegador: ")
    add_bullet(doc, "Admin: 'admin' / 'admin123' | Usuario: 'recepcion' / 'recepcion123'", bold_prefix="6. Credenciales: ")
    add_bullet(doc, "pytest -v (ejecuta las 8 pruebas automatizadas)", bold_prefix="7. Ejecutar pruebas: ")

    add_paragraph(doc, "Opción B: Ejecución en Windows (CMD / PowerShell)", bold_prefix="")
    add_bullet(doc, "cd C:\\ruta\\a\\labcontrol (o abrir terminal en la carpeta)", bold_prefix="1. Acceder al directorio: ")
    add_bullet(doc, "pip install -r requirements.txt (instala Flask, PyMySQL, etc.)", bold_prefix="2. Dependencias: ")
    add_bullet(doc, "Iniciar MySQL en XAMPP (opcional; si no hay servidor activo, entra respaldo SQLite transparente)", bold_prefix="3. Base de Datos: ")
    add_bullet(doc, "python seed_data.py (inicializa la base y datos semilla)", bold_prefix="4. Inicializar BD: ")
    add_bullet(doc, "python app.py o doble clic a run.bat (inicia en http://127.0.0.1:5000)", bold_prefix="5. Iniciar servidor: ")
    add_bullet(doc, "Abrir en el navegador: http://127.0.0.1:5000", bold_prefix="6. Abrir en navegador: ")
    add_bullet(doc, "Admin: 'admin' / 'admin123' | Usuario: 'recepcion' / 'recepcion123'", bold_prefix="7. Credenciales: ")
    add_bullet(doc, "pytest -v (ejecuta las 8 pruebas automatizadas)", bold_prefix="8. Ejecutar pruebas: ")

    out_file = os.path.join(DOCS_DIR, "Avance_2_LabControl_Prototipo_Funcional.docx")
    doc.save(out_file)
    print(f"Documento de Avance 2 generado con éxito: {out_file}")

if __name__ == '__main__':
    build_avance_1()
    build_avance_2()
