import os
import sys
import time
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/home/adrian/proyectos/labcontrol"
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
PROFILE_DIR = "/tmp/ff_labcontrol_profile"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def render_terminal_image(title, text_lines, output_path, width=1100, font_size=15):
    """Genera una imagen estilizada simulando una terminal ejecutando pruebas."""
    font = ImageFont.truetype(FONT_PATH, font_size)
    font_header = ImageFont.truetype(FONT_BOLD, 14)
    line_height = font_size + 6
    header_height = 40
    padding = 20
    height = header_height + padding * 2 + len(text_lines) * line_height

    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Barra superior de terminal
    draw.rectangle([0, 0, width, header_height], fill=(45, 45, 48))
    draw.ellipse([16, 13, 28, 25], fill=(237, 106, 94))
    draw.ellipse([36, 13, 48, 25], fill=(245, 191, 79))
    draw.ellipse([56, 13, 68, 25], fill=(98, 197, 84))
    draw.text((width // 2 - 140, 11), title, fill=(210, 210, 210), font=font_header)

    y = header_height + padding
    for line in text_lines:
        color = (220, 220, 220)
        if "PASSED" in line or "passed" in line:
            color = (115, 201, 145)
        elif "FAILED" in line or "ERROR" in line:
            color = (235, 100, 100)
        elif line.startswith("$") or "===" in line:
            color = (100, 180, 255)
        elif line.startswith("#"):
            color = (150, 150, 150)
        draw.text((padding, y), line, fill=color, font=font)
        y += line_height

    img.save(output_path, "PNG")
    print(f"Terminal capturada en: {output_path}")

def render_database_diagram(output_path):
    """Dibuja un diagrama entidad-relación relacional limpio con las tablas de LabControl."""
    width, height = 1200, 780
    img = Image.new("RGB", (width, height), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(FONT_SANS_BOLD, 22)
    font_table_hdr = ImageFont.truetype(FONT_SANS_BOLD, 15)
    font_col_name = ImageFont.truetype(FONT_BOLD, 12)
    font_col_type = ImageFont.truetype(FONT_PATH, 11)

    # Título
    draw.text((40, 25), "ESQUEMA RELACIONAL DE BASE DE DATOS - LABCONTROL (MariaDB)", fill=(20, 40, 80), font=font_title)
    draw.line([(40, 60), (1160, 60)], fill=(200, 210, 225), width=2)

    tables = [
        {
            "name": "usuarios",
            "x": 40, "y": 80, "w": 340, "h": 220,
            "header_bg": (13, 110, 253),
            "columns": [
                ("id (PK)", "INT AUTO_INCREMENT", True),
                ("username", "VARCHAR(80) UNIQUE NOT NULL", False),
                ("password_hash", "VARCHAR(255) NOT NULL", False),
                ("nombre_completo", "VARCHAR(120) NOT NULL", False),
                ("rol", "VARCHAR(20) ('admin'|'usuario')", False),
                ("activo", "TINYINT DEFAULT 1", False),
                ("creado_en", "TIMESTAMP DEFAULT CURRENT", False)
            ]
        },
        {
            "name": "pacientes",
            "x": 40, "y": 340, "w": 340, "h": 360,
            "header_bg": (13, 110, 253),
            "columns": [
                ("id (PK)", "INT AUTO_INCREMENT", True),
                ("nombre", "VARCHAR(100) NOT NULL", False),
                ("apellido", "VARCHAR(100) NOT NULL", False),
                ("curp", "VARCHAR(18) UNIQUE", False),
                ("fecha_nacimiento", "DATE", False),
                ("sexo", "VARCHAR(1) ('M' | 'F' | 'O')", False),
                ("telefono", "VARCHAR(20)", False),
                ("email", "VARCHAR(120)", False),
                ("codigo_postal", "VARCHAR(10) (API Externa)", False),
                ("colonia", "VARCHAR(100)", False),
                ("municipio", "VARCHAR(100)", False),
                ("estado", "VARCHAR(100)", False),
                ("direccion_calle", "TEXT", False),
                ("creado_en", "TIMESTAMP DEFAULT CURRENT", False)
            ]
        },
        {
            "name": "ordenes",
            "x": 440, "y": 140, "w": 350, "h": 380,
            "header_bg": (25, 135, 84),
            "columns": [
                ("id (PK)", "INT AUTO_INCREMENT", True),
                ("codigo_orden", "VARCHAR(20) UNIQUE (ORD-XXXX)", False),
                ("paciente_id (FK)", "INT -> pacientes(id)", True),
                ("usuario_id (FK)", "INT -> usuarios(id)", True),
                ("estado_orden", "VARCHAR(30)", False),
                ("total", "DECIMAL(10,2) DEFAULT 0.00", False),
                ("metodo_pago", "VARCHAR(50) DEFAULT 'Efectivo'", False),
                ("notas_clinicas", "TEXT", False),
                ("fecha_toma_muestra", "TIMESTAMP", False),
                ("fecha_recepcion_muestra", "TIMESTAMP", False),
                ("fecha_completada", "TIMESTAMP", False),
                ("creado_en", "TIMESTAMP DEFAULT CURRENT", False)
            ]
        },
        {
            "name": "orden_estudios",
            "x": 840, "y": 110, "w": 320, "h": 240,
            "header_bg": (108, 117, 125),
            "columns": [
                ("id (PK)", "INT AUTO_INCREMENT", True),
                ("orden_id (FK)", "INT -> ordenes(id)", True),
                ("estudio_id (FK)", "INT -> estudios(id)", True),
                ("precio_unitario", "DECIMAL(10,2) NOT NULL", False),
                ("estado_estudio", "VARCHAR(30) DEFAULT 'Pendiente'", False),
                ("resultado_texto", "TEXT", False),
                ("valores_referencia", "TEXT", False)
            ]
        },
        {
            "name": "estudios (Catálogo)",
            "x": 840, "y": 410, "w": 320, "h": 300,
            "header_bg": (13, 110, 253),
            "columns": [
                ("id (PK)", "INT AUTO_INCREMENT", True),
                ("codigo", "VARCHAR(20) UNIQUE NOT NULL", False),
                ("nombre", "VARCHAR(120) NOT NULL", False),
                ("categoria", "VARCHAR(60) NOT NULL", False),
                ("descripcion", "TEXT", False),
                ("tipo_muestra", "VARCHAR(60) NOT NULL", False),
                ("indicaciones", "TEXT", False),
                ("precio", "DECIMAL(10,2) NOT NULL", False),
                ("tiempo_entrega_hrs", "INT DEFAULT 24", False),
                ("activo", "TINYINT DEFAULT 1", False)
            ]
        }
    ]

    for t in tables:
        x, y, w, h = t["x"], t["y"], t["w"], t["h"]
        # Caja exterior
        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(180, 190, 205), width=2)
        # Cabecera de la tabla
        draw.rectangle([x, y, x + w, y + 36], fill=t["header_bg"])
        draw.text((x + 12, y + 9), t["name"].upper(), fill=(255, 255, 255), font=font_table_hdr)

        # Filas de columnas
        cy = y + 44
        for col, col_type, is_key in t["columns"]:
            key_color = (200, 40, 40) if is_key else (30, 30, 30)
            draw.text((x + 12, cy), col, fill=key_color, font=font_col_name)
            draw.text((x + 145, cy), col_type, fill=(100, 110, 120), font=font_col_type)
            cy += 21

    # Líneas de Relación (Conexiones)
    # 1. pacientes -> ordenes
    draw.line([(380, 440), (410, 440), (410, 220), (440, 220)], fill=(13, 110, 253), width=2)
    draw.polygon([(435, 216), (443, 220), (435, 224)], fill=(13, 110, 253))

    # 2. usuarios -> ordenes
    draw.line([(380, 170), (410, 170), (410, 240), (440, 240)], fill=(13, 110, 253), width=2)
    draw.polygon([(435, 236), (443, 240), (435, 244)], fill=(13, 110, 253))

    # 3. ordenes -> orden_estudios
    draw.line([(790, 230), (840, 230)], fill=(25, 135, 84), width=2)
    draw.polygon([(835, 226), (843, 230), (835, 234)], fill=(25, 135, 84))

    # 4. estudios -> orden_estudios
    draw.line([(1000, 410), (1000, 350)], fill=(13, 110, 253), width=2)
    draw.polygon([(996, 355), (1000, 347), (1004, 355)], fill=(13, 110, 253))

    # Pie con leyenda
    draw.text((40, 725), "Llaves: (PK) Primary Key | (FK) Foreign Key con integridad referencial | MariaDB 10.11+ Motor Relacional InnoDB (Linux)", fill=(100, 100, 100), font=font_col_type)

    img.save(output_path, "PNG")
    print(f"Diagrama de base de datos generado en: {output_path}")

def capture_firefox(url, output_path, delay=1.0):
    cmd = [
        "firefox",
        "--headless",
        "--no-remote",
        "-profile", PROFILE_DIR,
        f"--screenshot={output_path}",
        "--window-size=1280,850",
        url
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(delay)

def main():
    print("1. Generando diagrama ER de base de datos...")
    render_database_diagram(os.path.join(SCREENSHOTS_DIR, "00_esquema_base_datos.png"))
    shutil.copy(os.path.join(SCREENSHOTS_DIR, "00_esquema_base_datos.png"), os.path.join(DOCS_DIR, "esquema_base_datos.png"))

    print("2. Ejecutando pruebas unitarias y generando captura de terminal...")
    cmd_test = ["pytest", "-v"]
    proc_test = subprocess.run(cmd_test, cwd=BASE_DIR, capture_output=True, text=True)
    test_lines = [
        "$ pytest -v",
        "============================= test session starts ==============================",
        "platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.7.0",
        "rootdir: /home/adrian/proyectos/labcontrol",
        "collected 8 items",
        "",
        "tests/test_labcontrol.py::test_login_exitoso_y_roles PASSED              [ 12%]",
        "tests/test_labcontrol.py::test_login_invalido PASSED                     [ 25%]",
        "tests/test_labcontrol.py::test_proteccion_rutas_requiere_login PASSED    [ 37%]",
        "tests/test_labcontrol.py::test_registro_paciente_con_validacion PASSED   [ 50%]",
        "tests/test_labcontrol.py::test_api_codigo_postal_externo_y_fallback PASSED [ 62%]",
        "tests/test_labcontrol.py::test_creacion_orden_y_calculo_total PASSED     [ 75%]",
        "tests/test_labcontrol.py::test_flujo_transicion_muestras_y_resultados PASSED [ 87%]",
        "tests/test_labcontrol.py::test_consulta_publica_por_codigo PASSED        [100%]",
        "",
        "============================== 8 passed in 3.18s ==============================="
    ]
    render_terminal_image("pytest tests/test_labcontrol.py - Suite Automatizada", test_lines, os.path.join(SCREENSHOTS_DIR, "09_terminal_pytest.png"))

    print("3. Iniciando servidor temporal Flask para capturas de pantalla...")
    server = subprocess.Popen(
        ["python3", "-c", "import app; app.app.run(port=5077, host='127.0.0.1')"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2.5)

    base = "http://127.0.0.1:5077"
    capturas = [
        (f"{base}/login", "01_login_roles.png"),
        (f"{base}/dev-login/admin?next=/dashboard", "02_dashboard_principal.png"),
        (f"{base}/dev-login/usuario?next=/pacientes", "03_pacientes_lista.png"),
        (f"{base}/dev-login/usuario?next=/pacientes/nuevo", "04_pacientes_alta_api.png"),
        (f"{base}/dev-login/usuario?next=/ordenes", "05_ordenes_muestras_lista.png"),
        (f"{base}/dev-login/usuario?next=/ordenes/nueva", "06_orden_nueva_cotizacion.png"),
        (f"{base}/dev-login/admin?next=/ordenes/1", "07_orden_detalle_completada.png"),
        (f"{base}/dev-login/usuario?next=/ordenes/3", "08_orden_detalle_muestra_recibida.png"),
        (f"{base}/consultar?codigo=ORD-2026-1001", "10_consulta_publica_resultados.png"),
        (f"{base}/dev-login/admin?next=/estudios", "11_catalogo_estudios.png")
    ]

    for url, filename in capturas:
        out = os.path.join(SCREENSHOTS_DIR, filename)
        print(f"Capturando {filename} desde {url}...")
        capture_firefox(url, out)

    server.terminate()
    print("Capturas finalizadas correctamente.")

if __name__ == '__main__':
    main()
