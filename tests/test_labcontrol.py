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
    # Usar base de datos temporal para pruebas aisladas
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    database.DB_PATH = db_path
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
    """Verifica inicio de sesión exitoso tanto para admin como usuario."""
    # Test Admin
    res_admin = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert res_admin.status_code == 200
    assert b"Carlos M" in res_admin.data or b"Dashboard" in res_admin.data

    # Cerrar sesión
    client.get('/logout')

    # Test Usuario/Recepción
    res_user = client.post('/login', data={'username': 'recepcion', 'password': 'recepcion123'}, follow_redirects=True)
    assert res_user.status_code == 200
    assert b"Laura Morales" in res_user.data or b"Dashboard" in res_user.data

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
