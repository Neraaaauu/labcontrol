import pytest
import os
import sys
import tempfile
import sqlite3

# Añadir el directorio padre al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as lab_app
import database
import seed_data

@pytest.fixture
def client():
    # Usar base de datos temporal SQLite para pruebas aisladas
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    database.DB_PATH = db_path
    database.PREFERRED_ENGINE = 'sqlite'
    lab_app.app.config['TESTING'] = True
    lab_app.app.secret_key = 'test-secret-key'


    with lab_app.app.test_client() as client:
        with lab_app.app.app_context():
            seed_data.seed_database()
        yield client

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

def test_login_exitoso_y_roles(client):
    """Verifica inicio de sesión exitoso para los 4 roles clínicos definidos (admin, recepcion, quimico, medico)."""
    # 1. Test Admin
    res_admin = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert res_admin.status_code == 200
    assert b"Carlos M" in res_admin.data or b"Dashboard" in res_admin.data
    client.get('/logout')

    # 2. Test Recepción
    res_user = client.post('/login', data={'username': 'recepcion', 'password': 'recepcion123'}, follow_redirects=True)
    assert res_user.status_code == 200
    assert b"Laura Morales" in res_user.data or b"Dashboard" in res_user.data
    client.get('/logout')

    # 3. Test Químico Analista Q.F.B.
    res_qfb = client.post('/login', data={'username': 'quimico', 'password': 'quimico123'}, follow_redirects=True)
    assert res_qfb.status_code == 200
    assert b"Roberto Salcedo" in res_qfb.data or b"Dashboard" in res_qfb.data
    client.get('/logout')

    # 4. Test Médico Patólogo Validador
    res_doc = client.post('/login', data={'username': 'doctor', 'password': 'doctor123'}, follow_redirects=True)
    assert res_doc.status_code == 200
    assert b"Alejandro Pe" in res_doc.data or b"Dashboard" in res_doc.data

def test_login_invalido(client):
    """Verifica rechazo ante contraseñas incorrectas."""
    res = client.post('/login', data={'username': 'admin', 'password': 'password_incorrecto'}, follow_redirects=True)
    assert b"Credenciales incorrectas" in res.data

def test_proteccion_rutas_requiere_login(client):
    """Rutas protegidas deben redirigir a login si no hay sesión."""
    res = client.get('/pacientes', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.location

def test_registro_paciente_con_validacion(client):
    """Verifica creación de nuevo paciente y validaciones de datos."""
    # Iniciar sesión primero
    client.post('/login', data={'username': 'recepcion', 'password': 'recepcion123'})

    # Registro válido
    res = client.post('/pacientes/nuevo', data={
        'nombre': 'Guillermo',
        'apellido': 'Del Toro',
        'curp': 'DELG641009HDFRRL01',
        'fecha_nacimiento': '1964-10-09',
        'sexo': 'M',
        'telefono': '664-999-8877',
        'email': 'memo.deltoro@demo.com',
        'codigo_postal': '22000',
        'colonia': 'Zona Centro',
        'municipio': 'Tijuana',
        'estado': 'Baja California',
        'direccion_calle': 'Av. Madero #100'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Guillermo Del Toro" in res.data or b"registrado exitosamente" in res.data

    # CURP duplicada debe ser rechazada
    res_dup = client.post('/pacientes/nuevo', data={
        'nombre': 'Otro',
        'apellido': 'Nombre',
        'curp': 'DELG641009HDFRRL01'
    }, follow_redirects=True)
    assert b"Ya existe un paciente registrado con esa CURP" in res_dup.data

def test_api_codigo_postal_externo_y_fallback(client):
    """Verifica que el endpoint de C.P. responda adecuadamente y tolere fallos."""
    # Código postal común
    res = client.get('/api/codigo-postal/22000')
    assert res.status_code == 200
    data = res.get_json()
    assert 'estado' in data
    assert 'Baja California' in data['estado']
    assert 'colonias' in data
    assert len(data['colonias']) > 0

    # CP con formato inválido debe arrojar 400
    res_bad = client.get('/api/codigo-postal/999')
    assert res_bad.status_code == 400

def test_creacion_orden_y_calculo_total(client):
    """Verifica que una orden con múltiples estudios calcule correctamente su costo y genere folio."""
    client.post('/login', data={'username': 'recepcion', 'password': 'recepcion123'})

    # Crear orden para paciente 1 con estudios BH-01 (220.0) y QS-06 (380.0)
    # Total esperado: 600.00
    res = client.post('/ordenes/nueva', data={
        'paciente_id': '1',
        'estudios': ['1', '2'],
        'metodo_pago': 'Efectivo',
        'notas_clinicas': 'Prueba automatizada de orden.',
        'marcar_recibida_inmediato': '1'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"ORD-2026-" in res.data
    assert b"$600.00" in res.data or b"600" in res.data

def test_flujo_transicion_muestras_y_resultados(client):
    """Verifica la demostración principal: de muestra recibida a análisis y completada."""
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})

    # Cambiar estado de orden 3 a 'En Análisis'
    res = client.post('/ordenes/3/estado', data={'nuevo_estado': 'En Análisis'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"En An" in res.data

    # Pasar a 'Completada'
    res2 = client.post('/ordenes/3/estado', data={'nuevo_estado': 'Completada'}, follow_redirects=True)
    assert res2.status_code == 200
    assert b"Completada" in res2.data

def test_consulta_publica_por_codigo(client):
    """Verifica búsqueda por código de orden en portal de consulta."""
    res = client.post('/consultar', data={'codigo': 'ORD-2026-1001'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"ORD-2026-1001" in res.data
    assert b"Mar" in res.data or b"Garc" in res.data  # María Fernanda García

# ==============================================================================
# PRUEBAS UNITARIAS AVANCE 3 (INTEGRACIÓN, CALIDAD, API Y REGLAS DE NEGOCIO)
# ==============================================================================

def test_index_redisenado_portal_paciente(client):
    """Verifica que la raíz sea el portal público accesible para clientes sin requerir login."""
    res = client.get('/')
    assert res.status_code == 200
    assert b"Consulta y Descarga de Resultados" in res.data or b"Consultar Mis Resultados" in res.data
    assert b"Portal de Control Cl" in res.data or b"Panel Administrativo" in res.data
    assert b"ORD-2026-1001" in res.data  # Chips de prueba

def test_index_busqueda_directa_por_folio(client):
    """Verifica la consulta de resultados interactiva en la nueva página principal."""
    res = client.post('/', data={'codigo': 'ORD-2026-1001'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"ORD-2026-1001" in res.data
    assert b"Garc" in res.data  # Paciente García López
    assert b"Resultados Validados" in res.data or b"Completada" in res.data

def test_reporte_clinico_oficial_impreso(client):
    """Verifica que el informe de resultados clínico oficial se genere con sello, datos de QFB y validación del médico patólogo."""
    res = client.get('/consultar/reporte/ORD-2026-1001')
    assert res.status_code == 200
    assert b"LABCONTROL" in res.data
    assert b"Informe Cl" in res.data
    assert b"Alejandro Pe" in res.data  # Dr. Alejandro Peña (Médico Patólogo)
    assert b"Roberto Salcedo" in res.data  # QFB. Roberto Salcedo
    assert b"SELLO" in res.data

def test_api_rest_ordenes_json_y_404(client):
    """Verifica el endpoint REST /api/v1/ordenes/<codigo> tanto para folios válidos como 404."""
    # Caso 1: Folio existente
    res = client.get('/api/v1/ordenes/ORD-2026-1001')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['data']['folio'] == 'ORD-2026-1001'
    assert 'paciente' in data['data']
    assert 'estudios' in data['data']
    assert len(data['data']['estudios']) > 0

    # Caso 2: Folio inexistente debe responder HTTP 404 estructurado
    res_404 = client.get('/api/v1/ordenes/ORD-9999-9999')
    assert res_404.status_code == 404
    data_404 = res_404.get_json()
    assert data_404['status'] == 'error'
    assert data_404['codigo_http'] == 404

def test_api_rest_catalogo_estudios_json(client):
    """Verifica el endpoint REST /api/v1/estudios para consultar el catálogo disponible."""
    res = client.get('/api/v1/estudios')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'estudios' in data
    assert len(data['estudios']) >= 4
    primer_estudio = data['estudios'][0]
    assert 'codigo' in primer_estudio
    assert 'precio' in primer_estudio

def test_api_rest_validacion_curp_tiempo_real(client):
    """Verifica el endpoint REST /api/v1/pacientes/validar-curp."""
    # Caso 1: CURP con formato inválido -> 400 Bad Request
    res_inv = client.post('/api/v1/pacientes/validar-curp', json={'curp': 'CURP_INVALIDA_123'})
    assert res_inv.status_code == 400
    assert res_inv.get_json()['valido'] is False

    # Caso 2: CURP válida y duplicada (María Fernanda García)
    res_dup = client.post('/api/v1/pacientes/validar-curp', json={'curp': 'GALM880415HBCRLA01'})
    assert res_dup.status_code == 200
    assert res_dup.get_json()['disponible'] is False
    assert b"ya est" in res_dup.data or "ya está" in res_dup.get_json()['mensaje']

    # Caso 3: CURP válida y nueva disponible
    res_ok = client.post('/api/v1/pacientes/validar-curp', json={'curp': 'DELG641009HDFRRL01'})
    assert res_ok.status_code == 200
    assert res_ok.get_json()['disponible'] is True
    assert 'metadatos' in res_ok.get_json()

def test_maquina_estados_rechazo_transicion_invalida(client):
    """Verifica que la máquina de estados impida completar una orden sin haber recibido muestra biológica."""
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})

    # Orden 4 está en estado 'Pendiente' (sin muestra recibida). Intentar saltar a 'Completada' debe ser rechazado
    res = client.post('/ordenes/4/estado', data={'nuevo_estado': 'Completada'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"No se puede completar una orden sin antes haber recibido la muestra" in res.data

def test_rol_quimico_procesamiento_y_captura(client):
    """Verifica que el rol de Químico Analista pueda capturar hallazgos analíticos en laboratorio."""
    client.post('/login', data={'username': 'quimico', 'password': 'quimico123'})

    # Capturar resultados para la orden 2
    res = client.post('/ordenes/2/capturar-resultados', data={
        'resultado_3': 'Glucosa: 92.0 mg/dL | Urea: 28.0 mg/dL | Creatinina: 0.9 mg/dL'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"guardados correctamente" in res.data

def test_rol_medico_dictamen_y_restriccion_recepcion(client):
    """Verifica que el Médico Patólogo emita el dictamen clínico y que recepción no tenga acceso a dictaminar."""
    # Caso 1: Recepción intenta dictaminar médicamente -> Rechazado
    client.post('/login', data={'username': 'recepcion', 'password': 'recepcion123'})
    res_rec = client.post('/ordenes/2/validar-medico', data={
        'interpretacion_medica': 'Dictamen no autorizado por recepcionista'
    }, follow_redirects=True)
    assert b"Acceso denegado" in res_rec.data or b"Pat" in res_rec.data
    client.get('/logout')

    # Caso 2: Médico Patólogo emite dictamen clínico oficial -> Aceptado
    client.post('/login', data={'username': 'doctor', 'password': 'doctor123'})
    res_doc = client.post('/ordenes/2/validar-medico', data={
        'interpretacion_medica': 'Perfil metabólico dentro de límites normales. Sin datos de nefropatía ni dislipidemia.'
    }, follow_redirects=True)
    assert res_doc.status_code == 200
    assert b"Dictamen" in res_doc.data and b"avalada" in res_doc.data
