import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'labcontrol.db')

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Tabla de Usuarios (roles: admin, usuario)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre_completo TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin', 'usuario')),
        activo INTEGER NOT NULL DEFAULT 1,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Tabla de Pacientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        curp TEXT UNIQUE,
        fecha_nacimiento DATE,
        sexo TEXT CHECK(sexo IN ('M', 'F', 'O')),
        telefono TEXT,
        email TEXT,
        codigo_postal TEXT,
        colonia TEXT,
        municipio TEXT,
        estado TEXT,
        direccion_calle TEXT,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Tabla de Catálogo de Estudios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estudios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        descripcion TEXT,
        tipo_muestra TEXT NOT NULL,
        indicaciones TEXT,
        precio REAL NOT NULL,
        tiempo_entrega_horas INTEGER DEFAULT 24,
        activo INTEGER NOT NULL DEFAULT 1
    );
    """)

    # Tabla de Órdenes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ordenes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_orden TEXT UNIQUE NOT NULL,
        paciente_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        estado_orden TEXT NOT NULL DEFAULT 'Pendiente' CHECK(estado_orden IN ('Pendiente', 'Muestra Recibida', 'En Análisis', 'Completada', 'Cancelada')),
        total REAL NOT NULL DEFAULT 0.0,
        metodo_pago TEXT DEFAULT 'Efectivo',
        notas_clinicas TEXT,
        fecha_toma_muestra TIMESTAMP,
        fecha_recepcion_muestra TIMESTAMP,
        fecha_completada TIMESTAMP,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE RESTRICT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT
    );
    """)

    # Tabla de Estudios en la Orden
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orden_estudios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        orden_id INTEGER NOT NULL,
        estudio_id INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        estado_estudio TEXT DEFAULT 'Pendiente',
        resultado_texto TEXT,
        valores_referencia TEXT,
        FOREIGN KEY (orden_id) REFERENCES ordenes (id) ON DELETE CASCADE,
        FOREIGN KEY (estudio_id) REFERENCES estudios (id) ON DELETE RESTRICT
    );
    """)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos inicializada correctamente.")
