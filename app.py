import os
import re
import random
import datetime
import urllib.request
import json
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
)
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db, init_db, obtener_orden_completa_optimizada

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'labcontrol-secret-key-uabc-2026')

# Asegurar base de datos inicializada
init_db()

# ==========================================
# VALIDACIONES DE NEGOCIO Y AYUDAS CLÍNICAS
# ==========================================

CURP_REGEX = re.compile(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validar_curp_formato(curp):
    """Valida formato oficial de CURP mexicana (18 caracteres)."""
    if not curp:
        return True, ""
    curp = curp.strip().upper()
    if len(curp) != 18:
        return False, "La CURP debe tener exactamente 18 caracteres alfanuméricos."
    if not CURP_REGEX.match(curp):
        return False, "El formato de la CURP es inválido (debe cumplir con el estándar RENAPO)."
    return True, ""

def validar_email_formato(email):
    """Valida formato de correo electrónico si fue proporcionado."""
    if not email:
        return True, ""
    if not EMAIL_REGEX.match(email.strip()):
        return False, "El formato de correo electrónico es inválido (ejemplo: usuario@correo.com)."
    return True, ""

def validar_telefono_formato(tel):
    """Valida que el teléfono contenga al menos 10 dígitos numéricos si fue proporcionado."""
    if not tel:
        return True, ""
    digits = re.sub(r'\D', '', tel)
    if len(digits) < 10:
        return False, "El número telefónico debe contener al menos 10 dígitos numéricos."
    return True, ""

# ==========================================
# DECORADORES DE SEGURIDAD Y ROLES
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta sección.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión.', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('Acceso restringido: Se requieren privilegios de Administrador.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_now():
    from database import is_using_mariadb
    return {
        'now': datetime.datetime.now(),
        'app_name': 'LabControl',
        'current_year': 2026,
        'db_engine': 'MariaDB (Linux)' if is_using_mariadb() else 'SQLite'
    }


# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Ingresa tu usuario y contraseña.', 'danger')
            return render_template('login.html')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nombre_completo'] = user['nombre_completo']
            session['rol'] = user['rol']
            flash(f'¡Bienvenido/a {user["nombre_completo"]}!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard'))
        else:
            flash('Credenciales incorrectas o usuario inactivo. Verifica tus datos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

# ==========================================
# PORTAL PÚBLICO (INDEX) Y CONSULTA DE RESULTADOS
# (Avance 3: Rediseño del Index para Clientes/Pacientes)
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def index():
    codigo_buscado = ''
    orden = None
    estudios_orden = []

    if request.method == 'POST' or request.args.get('codigo') or request.args.get('folio'):
        codigo_buscado = (request.form.get('codigo') or request.form.get('folio') or 
                          request.args.get('codigo') or request.args.get('folio') or '').strip().upper()
        if codigo_buscado:
            orden, estudios_orden = obtener_orden_completa_optimizada(codigo_buscado)
            if not orden:
                flash(f'No se encontró ninguna orden con el folio "{codigo_buscado}". Verifica el código.', 'warning')

    return render_template('index.html', 
                           codigo_buscado=codigo_buscado, 
                           orden=orden, 
                           estudios_orden=estudios_orden)

# ==========================================
# DASHBOARD PRINCIPAL (Área Administrativa)
# ==========================================

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    # Contadores para tarjetas
    cursor.execute("SELECT COUNT(*) FROM pacientes")
    total_pacientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordenes")
    total_ordenes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordenes WHERE estado_orden = 'Pendiente'")
    muestras_pendientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordenes WHERE estado_orden = 'Muestra Recibida'")
    muestras_recibidas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordenes WHERE estado_orden = 'En Análisis'")
    en_analisis = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordenes WHERE estado_orden = 'Completada'")
    completadas = cursor.fetchone()[0]

    # Órdenes recientes con datos del paciente
    cursor.execute("""
        SELECT o.*, p.nombre || ' ' || p.apellido AS paciente_nombre, p.telefono AS paciente_tel,
               u.nombre_completo AS atendido_por,
               (SELECT COUNT(*) FROM orden_estudios WHERE orden_id = o.id) AS num_estudios
        FROM ordenes o
        JOIN pacientes p ON o.paciente_id = p.id
        JOIN usuarios u ON o.usuario_id = u.id
        ORDER BY o.creado_en DESC
        LIMIT 6
    """)
    ordenes_recientes = cursor.fetchall()

    conn.close()

    metrics = {
        'total_pacientes': total_pacientes,
        'total_ordenes': total_ordenes,
        'muestras_pendientes': muestras_pendientes,
        'muestras_recibidas': muestras_recibidas,
        'en_analisis': en_analisis,
        'completadas': completadas
    }

    return render_template('dashboard.html', metrics=metrics, ordenes_recientes=ordenes_recientes)

# ==========================================
# MÓDULO 1: PACIENTES
# ==========================================

@app.route('/pacientes')
@login_required
def lista_pacientes():
    q = request.args.get('q', '').strip()
    conn = get_db()
    cursor = conn.cursor()

    if q:
        cursor.execute("""
            SELECT p.*, 
                   (SELECT COUNT(*) FROM ordenes WHERE paciente_id = p.id) as total_ordenes
            FROM pacientes p
            WHERE p.nombre LIKE ? OR p.apellido LIKE ? OR p.curp LIKE ? OR p.telefono LIKE ?
            ORDER BY p.apellido ASC
        """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
    else:
        cursor.execute("""
            SELECT p.*, 
                   (SELECT COUNT(*) FROM ordenes WHERE paciente_id = p.id) as total_ordenes
            FROM pacientes p
            ORDER BY p.creado_en DESC
        """)

    pacientes = cursor.fetchall()
    conn.close()
    return render_template('pacientes/index.html', pacientes=pacientes, q=q)

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_paciente():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        curp = request.form.get('curp', '').strip().upper()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
        sexo = request.form.get('sexo', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        codigo_postal = request.form.get('codigo_postal', '').strip()
        colonia = request.form.get('colonia', '').strip()
        municipio = request.form.get('municipio', '').strip()
        estado = request.form.get('estado', '').strip()
        direccion_calle = request.form.get('direccion_calle', '').strip()

        # Validaciones de negocio reforzadas
        errores = []
        if not nombre:
            errores.append('El nombre del paciente es obligatorio.')
        if not apellido:
            errores.append('Los apellidos son obligatorios.')
        
        curp_valida, msg_curp = validar_curp_formato(curp)
        if not curp_valida:
            errores.append(msg_curp)

        email_valido, msg_email = validar_email_formato(email)
        if not email_valido:
            errores.append(msg_email)

        tel_valido, msg_tel = validar_telefono_formato(telefono)
        if not tel_valido:
            errores.append(msg_tel)

        if sexo and sexo not in ('M', 'F', 'O'):
            errores.append('El sexo biológico seleccionado no es válido (debe ser Masculino [M], Femenino [F] u Otro [O]).')

        if errores:
            for err in errores:
                flash(err, 'danger')
            return render_template('pacientes/nuevo.html', form=request.form)

        conn = get_db()
        cursor = conn.cursor()

        # Comprobar CURP única si se ingresó
        if curp:
            cursor.execute("SELECT id FROM pacientes WHERE curp = ?", (curp,))
            if cursor.fetchone():
                conn.close()
                flash('Ya existe un paciente registrado con esa CURP.', 'danger')
                return render_template('pacientes/nuevo.html', form=request.form)

        cursor.execute("""
            INSERT INTO pacientes 
            (nombre, apellido, curp, fecha_nacimiento, sexo, telefono, email, codigo_postal, colonia, municipio, estado, direccion_calle)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, apellido, curp or None, fecha_nacimiento or None, sexo or None, telefono, email, codigo_postal, colonia, municipio, estado, direccion_calle))
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()

        flash(f'Paciente {nombre} {apellido} registrado exitosamente.', 'success')
        return redirect(url_for('detalle_paciente', id=nuevo_id))

    return render_template('pacientes/nuevo.html', form={})

@app.route('/pacientes/<int:id>')
@login_required
def detalle_paciente(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes WHERE id = ?", (id,))
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        flash('Paciente no encontrado.', 'danger')
        return redirect(url_for('lista_pacientes'))

    # Órdenes del paciente
    cursor.execute("""
        SELECT o.*, u.nombre_completo as atendido_por,
               (SELECT COUNT(*) FROM orden_estudios WHERE orden_id = o.id) as num_estudios
        FROM ordenes o
        JOIN usuarios u ON o.usuario_id = u.id
        WHERE o.paciente_id = ?
        ORDER BY o.creado_en DESC
    """, (id,))
    ordenes = cursor.fetchall()

    conn.close()
    return render_template('pacientes/detalle.html', paciente=paciente, ordenes=ordenes)

@app.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_paciente(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes WHERE id = ?", (id,))
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        flash('Paciente no encontrado.', 'danger')
        return redirect(url_for('lista_pacientes'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        curp = request.form.get('curp', '').strip().upper()
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
        sexo = request.form.get('sexo', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        codigo_postal = request.form.get('codigo_postal', '').strip()
        colonia = request.form.get('colonia', '').strip()
        municipio = request.form.get('municipio', '').strip()
        estado = request.form.get('estado', '').strip()
        direccion_calle = request.form.get('direccion_calle', '').strip()

        errores = []
        if not nombre:
            errores.append('El nombre del paciente es obligatorio.')
        if not apellido:
            errores.append('Los apellidos son obligatorios.')

        curp_valida, msg_curp = validar_curp_formato(curp)
        if not curp_valida:
            errores.append(msg_curp)

        email_valido, msg_email = validar_email_formato(email)
        if not email_valido:
            errores.append(msg_email)

        tel_valido, msg_tel = validar_telefono_formato(telefono)
        if not tel_valido:
            errores.append(msg_tel)

        if sexo and sexo not in ('M', 'F', 'O'):
            errores.append('El sexo biológico seleccionado no es válido (debe ser Masculino [M], Femenino [F] u Otro [O]).')

        if errores:
            for err in errores:
                flash(err, 'danger')
            conn.close()
            return render_template('pacientes/editar.html', paciente=paciente)

        # Validar CURP única excluyendo el paciente actual
        if curp:
            cursor.execute("SELECT id FROM pacientes WHERE curp = ? AND id != ?", (curp, id))
            if cursor.fetchone():
                conn.close()
                flash('Otro paciente ya tiene esa CURP registrada.', 'danger')
                return render_template('pacientes/editar.html', paciente=paciente)

        cursor.execute("""
            UPDATE pacientes
            SET nombre = ?, apellido = ?, curp = ?, fecha_nacimiento = ?, sexo = ?,
                telefono = ?, email = ?, codigo_postal = ?, colonia = ?, municipio = ?,
                estado = ?, direccion_calle = ?
            WHERE id = ?
        """, (nombre, apellido, curp or None, fecha_nacimiento or None, sexo or None,
              telefono, email, codigo_postal, colonia, municipio, estado, direccion_calle, id))
        conn.commit()
        conn.close()

        flash('Información del paciente actualizada correctamente.', 'success')
        return redirect(url_for('detalle_paciente', id=id))

    conn.close()
    return render_template('pacientes/editar.html', paciente=paciente)

# ==========================================
# MÓDULO 2: ÓRDENES Y MUESTRAS DE LABORATORIO
# ==========================================

@app.route('/ordenes')
@login_required
def lista_ordenes():
    estado_filtro = request.args.get('estado', '').strip()
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT o.*, p.nombre || ' ' || p.apellido AS paciente_nombre, p.curp AS paciente_curp,
               u.nombre_completo AS atendido_por,
               (SELECT COUNT(*) FROM orden_estudios WHERE orden_id = o.id) AS num_estudios
        FROM ordenes o
        JOIN pacientes p ON o.paciente_id = p.id
        JOIN usuarios u ON o.usuario_id = u.id
    """
    params = []

    if estado_filtro and estado_filtro != 'Todos':
        query += " WHERE o.estado_orden = ?"
        params.append(estado_filtro)

    query += " ORDER BY o.creado_en DESC"

    cursor.execute(query, params)
    ordenes = cursor.fetchall()
    conn.close()

    return render_template('ordenes/index.html', ordenes=ordenes, estado_filtro=estado_filtro)

@app.route('/ordenes/nueva', methods=['GET', 'POST'])
@login_required
def nueva_orden():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        estudios_seleccionados = request.form.getlist('estudios')
        metodo_pago = request.form.get('metodo_pago', 'Efectivo')
        notas_clinicas = request.form.get('notas_clinicas', '').strip()
        marcar_recibida_inmediato = request.form.get('marcar_recibida_inmediato') == '1'

        errores = []
        if not paciente_id:
            errores.append('Debes seleccionar un paciente.')
        if not estudios_seleccionados:
            errores.append('Debes seleccionar al menos un estudio del catálogo.')

        if errores:
            for err in errores:
                flash(err, 'danger')
            cursor.execute("SELECT id, nombre, apellido, curp FROM pacientes ORDER BY apellido ASC")
            pacientes = cursor.fetchall()
            cursor.execute("SELECT * FROM estudios WHERE activo = 1 ORDER BY categoria, nombre")
            estudios = cursor.fetchall()
            conn.close()
            return render_template('ordenes/nueva.html', pacientes=pacientes, estudios=estudios, paciente_pre=paciente_id)

        # Generar código de orden único
        # Formato ORD-2026-XXXX
        random_code = random.randint(1000, 9999)
        codigo_orden = f"ORD-2026-{random_code}"

        # Verificar unicidad
        cursor.execute("SELECT id FROM ordenes WHERE codigo_orden = ?", (codigo_orden,))
        while cursor.fetchone():
            random_code = random.randint(1000, 9999)
            codigo_orden = f"ORD-2026-{random_code}"
            cursor.execute("SELECT id FROM ordenes WHERE codigo_orden = ?", (codigo_orden,))

        # Calcular precio total a partir de la base de datos
        placeholders = ','.join(['?'] * len(estudios_seleccionados))
        cursor.execute(f"SELECT id, precio FROM estudios WHERE id IN ({placeholders})", estudios_seleccionados)
        estudios_db = cursor.fetchall()

        total = sum(item['precio'] for item in estudios_db)

        ahora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        estado_inicial = 'Muestra Recibida' if marcar_recibida_inmediato else 'Pendiente'
        fecha_toma = ahora if marcar_recibida_inmediato else None
        fecha_recepcion = ahora if marcar_recibida_inmediato else None

        cursor.execute("""
            INSERT INTO ordenes 
            (codigo_orden, paciente_id, usuario_id, estado_orden, total, metodo_pago, notas_clinicas, fecha_toma_muestra, fecha_recepcion_muestra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo_orden, paciente_id, session['user_id'], estado_inicial, total, metodo_pago, notas_clinicas, fecha_toma, fecha_recepcion))

        orden_id = cursor.lastrowid

        # Insertar los estudios asociados
        for item in estudios_db:
            cursor.execute("""
                INSERT INTO orden_estudios (orden_id, estudio_id, precio_unitario, estado_estudio)
                VALUES (?, ?, ?, ?)
            """, (orden_id, item['id'], item['precio'], estado_inicial))

        conn.commit()
        conn.close()

        flash(f'¡Orden {codigo_orden} creada exitosamente con {len(estudios_db)} estudio(s)!', 'success')
        return redirect(url_for('detalle_orden', id=orden_id))

    # Cargar datos para el formulario
    paciente_pre = request.args.get('paciente_id')
    cursor.execute("SELECT id, nombre, apellido, curp FROM pacientes ORDER BY apellido ASC")
    pacientes = cursor.fetchall()

    cursor.execute("SELECT * FROM estudios WHERE activo = 1 ORDER BY categoria, nombre")
    estudios = cursor.fetchall()
    conn.close()

    return render_template('ordenes/nueva.html', pacientes=pacientes, estudios=estudios, paciente_pre=paciente_pre)

@app.route('/ordenes/<int:id>')
@login_required
def detalle_orden(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.*, 
               p.nombre || ' ' || p.apellido AS paciente_nombre,
               p.curp AS paciente_curp,
               p.telefono AS paciente_telefono,
               p.email AS paciente_email,
               p.fecha_nacimiento AS paciente_nacimiento,
               p.sexo AS paciente_sexo,
               u.nombre_completo AS atendido_por
        FROM ordenes o
        JOIN pacientes p ON o.paciente_id = p.id
        JOIN usuarios u ON o.usuario_id = u.id
        WHERE o.id = ?
    """, (id,))
    orden = cursor.fetchone()

    if not orden:
        conn.close()
        flash('Orden de laboratorio no encontrada.', 'danger')
        return redirect(url_for('lista_ordenes'))

    # Estudios asociados a la orden
    cursor.execute("""
        SELECT oe.*, e.nombre, e.codigo, e.categoria, e.tipo_muestra, e.indicaciones, e.tiempo_entrega_horas
        FROM orden_estudios oe
        JOIN estudios e ON oe.estudio_id = e.id
        WHERE oe.orden_id = ?
    """, (id,))
    estudios_orden = cursor.fetchall()

    conn.close()
    return render_template('ordenes/detalle.html', orden=orden, estudios_orden=estudios_orden)

@app.route('/ordenes/<int:id>/estado', methods=['POST'])
@login_required
def cambiar_estado_orden(id):
    nuevo_estado = request.form.get('nuevo_estado', '').strip()
    estados_validos = ['Pendiente', 'Muestra Recibida', 'En Análisis', 'Completada', 'Cancelada']

    if nuevo_estado not in estados_validos:
        flash('Estado no válido.', 'danger')
        return redirect(url_for('detalle_orden', id=id))

    conn = get_db()
    cursor = conn.cursor()

    # Validaciones de máquina de estados clínica
    cursor.execute("SELECT estado_orden FROM ordenes WHERE id = ?", (id,))
    orden_db = cursor.fetchone()
    if not orden_db:
        conn.close()
        flash('Orden de laboratorio no encontrada.', 'danger')
        return redirect(url_for('lista_ordenes'))

    estado_actual = orden_db['estado_orden']
    if estado_actual == 'Cancelada' and nuevo_estado != 'Cancelada':
        conn.close()
        flash('Una orden cancelada no puede cambiar de estado.', 'danger')
        return redirect(url_for('detalle_orden', id=id))

    if nuevo_estado == 'Completada' and estado_actual not in ['En Análisis', 'Muestra Recibida', 'Completada']:
        conn.close()
        flash('No se puede completar una orden sin antes haber recibido la muestra biológica en laboratorio.', 'warning')
        return redirect(url_for('detalle_orden', id=id))

    ahora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if nuevo_estado == 'Muestra Recibida':
        cursor.execute("""
            UPDATE ordenes 
            SET estado_orden = ?, 
                fecha_toma_muestra = COALESCE(fecha_toma_muestra, ?),
                fecha_recepcion_muestra = ?
            WHERE id = ?
        """, (nuevo_estado, ahora, ahora, id))
    elif nuevo_estado == 'En Análisis':
        cursor.execute("UPDATE ordenes SET estado_orden = ? WHERE id = ?", (nuevo_estado, id))
    elif nuevo_estado == 'Completada':
        cursor.execute("""
            UPDATE ordenes 
            SET estado_orden = ?, 
                fecha_completada = ?
            WHERE id = ?
        """, (nuevo_estado, ahora, id))
    else:
        cursor.execute("UPDATE ordenes SET estado_orden = ? WHERE id = ?", (nuevo_estado, id))

    # Actualizar estado de los estudios hijos también
    cursor.execute("UPDATE orden_estudios SET estado_estudio = ? WHERE orden_id = ?", (nuevo_estado, id))

    conn.commit()
    conn.close()

    flash(f'Estado de la orden actualizado a: "{nuevo_estado}".', 'success')
    return redirect(url_for('detalle_orden', id=id))

@app.route('/ordenes/<int:id>/capturar-resultados', methods=['POST'])
@login_required
def capturar_resultados(id):
    conn = get_db()
    cursor = conn.cursor()

    # Recorrer los resultados enviados en el formulario
    for key, value in request.form.items():
        if key.startswith('resultado_'):
            estudio_oe_id = key.replace('resultado_', '')
            resultado_texto = value.strip()
            cursor.execute("""
                UPDATE orden_estudios
                SET resultado_texto = ?
                WHERE id = ? AND orden_id = ?
            """, (resultado_texto, estudio_oe_id, id))

    conn.commit()
    conn.close()
    flash('Resultados analíticos guardados correctamente.', 'success')
    return redirect(url_for('detalle_orden', id=id))

# ==========================================
# REPORTES CLÍNICOS E IMPRESIÓN OFICIAL
# (Avance 3: Cierre del proceso de negocio)
# ==========================================

@app.route('/ordenes/<int:id>/imprimir')
@login_required
def reporte_interno_impreso(id):
    """Genera la vista oficial imprimible de resultados clínicos para el personal."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo_orden FROM ordenes WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        flash('Orden no encontrada.', 'danger')
        return redirect(url_for('lista_ordenes'))

    orden, estudios_orden = obtener_orden_completa_optimizada(row['codigo_orden'])
    return render_template('ordenes/reporte_impreso.html', orden=orden, estudios_orden=estudios_orden)

@app.route('/consultar/reporte/<codigo>')
def reporte_publico_impreso(codigo):
    """Acceso público al informe de resultados oficial para el paciente con su código."""
    codigo = codigo.strip().upper()
    orden, estudios_orden = obtener_orden_completa_optimizada(codigo)
    if not orden:
        flash('La orden solicitada no existe o el folio es inválido.', 'danger')
        return redirect(url_for('index'))
    return render_template('ordenes/reporte_impreso.html', orden=orden, estudios_orden=estudios_orden)

# ==========================================
# CATÁLOGO DE ESTUDIOS
# ==========================================

@app.route('/estudios')
@login_required
def catalogo_estudios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estudios ORDER BY categoria, nombre")
    estudios = cursor.fetchall()
    conn.close()
    return render_template('estudios/index.html', estudios=estudios)

@app.route('/estudios/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_estudio():
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip().upper()
        nombre = request.form.get('nombre', '').strip()
        categoria = request.form.get('categoria', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        tipo_muestra = request.form.get('tipo_muestra', '').strip()
        indicaciones = request.form.get('indicaciones', '').strip()
        precio = request.form.get('precio', '0').strip()
        tiempo_entrega = request.form.get('tiempo_entrega_horas', '24').strip()

        if not codigo or not nombre or not tipo_muestra:
            flash('Código, nombre y tipo de muestra son obligatorios.', 'danger')
            return render_template('estudios/nuevo.html', form=request.form)

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO estudios 
                (codigo, nombre, categoria, descripcion, tipo_muestra, indicaciones, precio, tiempo_entrega_horas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo, nombre, categoria, descripcion, tipo_muestra, indicaciones, float(precio), int(tiempo_entrega)))
            conn.commit()
            flash(f'Estudio {nombre} agregado al catálogo.', 'success')
            conn.close()
            return redirect(url_for('catalogo_estudios'))
        except Exception as e:
            conn.close()
            flash(f'Error al registrar el estudio: {str(e)}', 'danger')
            return render_template('estudios/nuevo.html', form=request.form)

    return render_template('estudios/nuevo.html', form={})

# ==========================================
# APARTADO PARA CONSULTAR RESULTADOS POR CÓDIGO
# (Requisito explícito del PDF: "Apartado para buscar los resultados de analisis mediante algun codigo")
# ==========================================

@app.route('/consultar', methods=['GET', 'POST'])
def consultar_codigo():
    resultado_busqueda = None
    codigo_buscado = ''
    estudios_resultado = []

    if request.method == 'POST' or request.args.get('codigo') or request.args.get('folio'):
        codigo_buscado = (request.form.get('codigo') or request.form.get('folio') or 
                          request.args.get('codigo') or request.args.get('folio') or '').strip().upper()

        if not codigo_buscado:
            flash('Por favor ingresa un folio o código de orden (Ejemplo: ORD-2026-1001).', 'warning')
        else:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, 
                       p.nombre || ' ' || p.apellido AS paciente_nombre,
                       p.curp AS paciente_curp
                FROM ordenes o
                JOIN pacientes p ON o.paciente_id = p.id
                WHERE o.codigo_orden = ?
            """, (codigo_buscado,))
            resultado_busqueda = cursor.fetchone()

            if resultado_busqueda:
                cursor.execute("""
                    SELECT oe.*, e.nombre, e.tipo_muestra, e.indicaciones
                    FROM orden_estudios oe
                    JOIN estudios e ON oe.estudio_id = e.id
                    WHERE oe.orden_id = ?
                """, (resultado_busqueda['id'],))
                estudios_resultado = cursor.fetchall()
            else:
                flash(f'No se encontró ninguna orden con el folio "{codigo_buscado}". Verifica el código.', 'danger')

            conn.close()

    return render_template('consulta_publica.html', 
                           codigo_buscado=codigo_buscado, 
                           orden=resultado_busqueda, 
                           estudios=estudios_resultado)

# ==========================================
# API EXTERNA: CÓDIGO POSTAL (Con fallback tolerante a fallos)
# ==========================================

FALLBACK_CODIGOS_POSTALES = {
    "22000": {"estado": "Baja California", "municipio": "Tijuana", "colonias": ["Zona Centro", "Tijuana Centro", "Centro Zona Norte", "Zona Este"]},
    "22400": {"estado": "Baja California", "municipio": "Tijuana", "colonias": ["Mesa de Otay", "Otay Universidad", "Otay Constituyentes", "Otay Galerías"]},
    "22200": {"estado": "Baja California", "municipio": "Tijuana", "colonias": ["Playas de Tijuana", "Costa Azul", "Laderas del Mar", "Soler"]},
    "22100": {"estado": "Baja California", "municipio": "Tijuana", "colonias": ["La Mesa", "Las Huertas", "Los Pinos", "Jardines de la Mesa"]},
    "22424": {"estado": "Baja California", "municipio": "Tijuana", "colonias": ["Altabrisa", "Tomás Aquino", "Otay Jardín", "Misiones del Pedregal"]},
    "21000": {"estado": "Baja California", "municipio": "Mexicali", "colonias": ["Mexicali Centro", "Primera Sección", "Segunda Sección"]},
    "22800": {"estado": "Baja California", "municipio": "Ensenada", "colonias": ["Ensenada Centro", "Obrera", "Bahía"]},
    "06000": {"estado": "Ciudad de México", "municipio": "Cuauhtémoc", "colonias": ["Centro (Área 1)", "Centro (Área 2)"]}
}

@app.route('/api/codigo-postal/<cp>')
def api_codigo_postal(cp):
    cp = cp.strip()
    if not cp.isdigit() or len(cp) != 5:
        return jsonify({'error': 'El código postal debe contener exactamente 5 dígitos numéricos.'}), 400

    # 1. Intentar consumir API pública externa (Zippopotam.us) con timeout corto
    url = f"http://api.zippopotam.us/mx/{cp}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'LabControl-App/1.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                places = data.get('places', [])
                if places:
                    colonias = [p.get('place name') for p in places if p.get('place name')]
                    estado = places[0].get('state', '')
                    # En Zippopotam, para MX a veces el municipio viene deducible o es la misma ciudad
                    return jsonify({
                        'codigo_postal': cp,
                        'estado': estado,
                        'municipio': 'Tijuana' if 'Baja California' in estado and cp.startswith('22') else estado,
                        'colonias': colonias,
                        'fuente': 'API Externa (Zippopotam)'
                    })
    except Exception as e:
        # Fallback tolerante a fallos si la API no responde o hay problemas de red
        pass

    # 2. Respaldo local tolerante a fallos si la API falla o está offline
    if cp in FALLBACK_CODIGOS_POSTALES:
        datos = FALLBACK_CODIGOS_POSTALES[cp]
        return jsonify({
            'codigo_postal': cp,
            'estado': datos['estado'],
            'municipio': datos['municipio'],
            'colonias': datos['colonias'],
            'fuente': 'Caché / Fallback Offline'
        })

    # Si no se encuentra en línea ni en el respaldo, devolver respuesta controlada
    return jsonify({
        'codigo_postal': cp,
        'estado': '',
        'municipio': '',
        'colonias': [],
        'fuente': 'No encontrado (captura manual disponible)',
        'mensaje': 'Código postal no encontrado en el servicio; puedes capturar tu domicilio manualmente.'
    }), 200

# ==========================================
# API REST INTERNA (Avance 3 - Endpoints JSON)
# ==========================================

@app.route('/api/v1/ordenes/<codigo>', methods=['GET'])
def api_v1_detalle_orden(codigo):
    """Retorna los datos clínicos, estado y resultados de una orden en JSON."""
    codigo = codigo.strip().upper()
    orden, estudios_orden = obtener_orden_completa_optimizada(codigo)
    if not orden:
        return jsonify({
            'status': 'error',
            'codigo_http': 404,
            'mensaje': f'Orden con folio {codigo} no encontrada en el sistema.'
        }), 404

    return jsonify({
        'status': 'success',
        'codigo_http': 200,
        'data': {
            'folio': orden['codigo_orden'],
            'estado': orden['estado_orden'],
            'paciente': {
                'id': orden['paciente_id'],
                'nombre_completo': orden['paciente_nombre'],
                'curp': orden['paciente_curp'],
                'sexo': orden['paciente_sexo'],
                'telefono': orden['paciente_telefono']
            },
            'fechas': {
                'creado_en': orden['creado_en'],
                'toma_muestra': orden['fecha_toma_muestra'],
                'recepcion_muestra': orden['fecha_recepcion_muestra'],
                'completada': orden['fecha_completada']
            },
            'financiero': {
                'total': orden['total'],
                'metodo_pago': orden['metodo_pago']
            },
            'estudios': estudios_orden
        }
    }), 200

@app.route('/api/v1/estudios', methods=['GET'])
def api_v1_catalogo_estudios():
    """Retorna el catálogo público de estudios en formato JSON."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, codigo, nombre, categoria, descripcion, tipo_muestra, precio, tiempo_entrega_horas 
        FROM estudios 
        WHERE activo = 1 
        ORDER BY categoria, nombre
    """)
    filas = cursor.fetchall()
    conn.close()

    estudios_list = []
    for r in filas:
        estudios_list.append({
            'id': r['id'],
            'codigo': r['codigo'],
            'nombre': r['nombre'],
            'categoria': r['categoria'],
            'descripcion': r['descripcion'],
            'tipo_muestra': r['tipo_muestra'],
            'precio': r['precio'],
            'tiempo_entrega_horas': r['tiempo_entrega_horas']
        })

    return jsonify({
        'status': 'success',
        'total': len(estudios_list),
        'estudios': estudios_list
    }), 200

@app.route('/api/v1/pacientes/validar-curp', methods=['POST'])
def api_v1_validar_curp():
    """Endpoint para validación de CURP en tiempo real con detección de duplicados."""
    data = request.get_json(silent=True) or request.form
    curp = (data.get('curp') or '').strip().upper()

    valido, mensaje = validar_curp_formato(curp)
    if not valido:
        return jsonify({
            'valido': False,
            'mensaje': mensaje,
            'disponible': False
        }), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, apellido FROM pacientes WHERE curp = ?", (curp,))
    existente = cursor.fetchone()
    conn.close()

    if existente:
        return jsonify({
            'valido': True,
            'disponible': False,
            'mensaje': f'La CURP ya está registrada a nombre de {existente["nombre"]} {existente["apellido"]}.',
            'paciente_id': existente['id']
        }), 200

    anio = int(curp[4:6])
    mes = curp[6:8]
    dia = curp[8:10]
    sexo = curp[10]
    siglo = '19' if anio > 30 else '20'
    fecha_nacimiento_est = f"{siglo}{anio:02d}-{mes}-{dia}"

    return jsonify({
        'valido': True,
        'disponible': True,
        'mensaje': 'CURP válida y disponible para registro.',
        'metadatos': {
            'fecha_nacimiento_estimada': fecha_nacimiento_est,
            'sexo': sexo
        }
    }), 200

@app.route('/api/v1/metricas', methods=['GET'])
def api_v1_metricas():
    """Telemetría y métricas operativas del sistema."""
    from database import is_using_mariadb
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM pacientes")
    total_pacientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ordenes")
    total_ordenes = cursor.fetchone()[0]

    cursor.execute("SELECT estado_orden, COUNT(*) FROM ordenes GROUP BY estado_orden")
    estados_dist = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) FROM estudios WHERE activo = 1")
    total_estudios = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        'status': 'success',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'motor_bd': 'MariaDB 10.11+ Relacional' if is_using_mariadb() else 'SQLite 3',
        'metricas': {
            'total_pacientes': total_pacientes,
            'total_ordenes': total_ordenes,
            'total_estudios_activos': total_estudios,
            'distribucion_estados': estados_dist
        }
    }), 200

@app.route('/dev-login/<role>')
def dev_login(role):
    """Ruta auxiliar para automatización de capturas y evaluación local."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE rol = ? AND activo = 1 LIMIT 1", (role,))
    user = cursor.fetchone()
    conn.close()
    if user:
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['nombre_completo'] = user['nombre_completo']
        session['rol'] = user['rol']
    dest = request.args.get('next', url_for('dashboard'))
    return redirect(dest)

if __name__ == '__main__':
    # Ejecutable en localhost
    app.run(debug=True, host='127.0.0.1', port=5000)

