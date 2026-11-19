import os
import sqlite3

# Intentar importar pymysql para soporte de MariaDB
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

MARIADB_SOCKET = os.environ.get('MARIADB_SOCKET', '/home/adrian/.mariadb/mariadb.sock')
MARIADB_USER = os.environ.get('MARIADB_USER', 'adrian')
MARIADB_DB = os.environ.get('MARIADB_DB', 'labcontrol')
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'labcontrol.db')

# Motor preferido: mariadb por defecto; sqlite como alternativa
PREFERRED_ENGINE = os.environ.get('DB_ENGINE', 'mariadb').lower()

class HybridRow(dict):
    """Permite acceder a columnas tanto por nombre (row['nombre']) como por índice numérico (row[0])."""
    def __init__(self, d, t):
        super().__init__(d)
        self._t = t
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._t[key]
        return super().__getitem__(key)

class MariaDBCursorWrapper:
    """Cursor que adapta parámetros (?) y sintaxis estándar para MariaDB/MySQL."""
    def __init__(self, raw_cursor):
        self._c = raw_cursor

    def execute(self, query, args=None):
        if isinstance(query, str):
            # Adaptar placeholders de SQLite (?) a MariaDB (%s)
            query = query.replace('INSERT OR IGNORE INTO', 'INSERT IGNORE INTO')
            query = query.replace('?', '%s')
        if args is not None:
            # pymysql espera tupla o lista
            return self._c.execute(query, tuple(args))
        return self._c.execute(query)

    def executemany(self, query, seq_of_params):
        if isinstance(query, str):
            query = query.replace('INSERT OR IGNORE INTO', 'INSERT IGNORE INTO')
            query = query.replace('?', '%s')
        return self._c.executemany(query, seq_of_params)

    @property
    def lastrowid(self):
        return self._c.lastrowid

    def fetchone(self):
        t = self._c.fetchone()
        if t is None:
            return None
        col_names = [col[0] for col in self._c.description]
        return HybridRow(dict(zip(col_names, t)), t)

    def fetchall(self):
        tuples = self._c.fetchall()
        if not tuples:
            return []
        col_names = [col[0] for col in self._c.description]
        return [HybridRow(dict(zip(col_names, t)), t) for t in tuples]

    def close(self):
        return self._c.close()

class MariaDBConnectionWrapper:
    """Wrapper de conexión pymysql para emular la API de sqlite3."""
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return MariaDBCursorWrapper(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

def get_mariadb_connection():
    if not PYMYSQL_AVAILABLE:
        return None
    try:
        if os.path.exists(MARIADB_SOCKET):
            conn = pymysql.connect(
                user=MARIADB_USER,
                unix_socket=MARIADB_SOCKET,
                database=MARIADB_DB,
                charset='utf8mb4',
                autocommit=False
            )
        else:
            conn = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user=MARIADB_USER,
                database=MARIADB_DB,
                charset='utf8mb4',
                autocommit=False
            )
        # Activar PIPES_AS_CONCAT para soportar 'str1 || str2' igual que en SQLite
        with conn.cursor() as cur:
            cur.execute("SET sql_mode = CONCAT(@@sql_mode, ',PIPES_AS_CONCAT');")
        return MariaDBConnectionWrapper(conn)
    except Exception as e:
        return None

def get_db():
    if PREFERRED_ENGINE == 'mariadb':
        mariadb_conn = get_mariadb_connection()
        if mariadb_conn:
            return mariadb_conn

    # Fallback a SQLite
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def is_using_mariadb():
    conn = get_db()
    is_maria = isinstance(conn, MariaDBConnectionWrapper)
    conn.close()
    return is_maria

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    if isinstance(conn, MariaDBConnectionWrapper):
        # Esquema para MariaDB
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nombre_completo VARCHAR(255) NOT NULL,
            rol VARCHAR(50) NOT NULL,
            activo TINYINT NOT NULL DEFAULT 1,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            apellido VARCHAR(150) NOT NULL,
            curp VARCHAR(20) UNIQUE,
            fecha_nacimiento DATE,
            sexo VARCHAR(5),
            telefono VARCHAR(50),
            email VARCHAR(150),
            codigo_postal VARCHAR(10),
            colonia VARCHAR(150),
            municipio VARCHAR(150),
            estado VARCHAR(150),
            direccion_calle TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            descripcion TEXT,
            tipo_muestra VARCHAR(150) NOT NULL,
            indicaciones TEXT,
            precio DECIMAL(10, 2) NOT NULL,
            tiempo_entrega_horas INT DEFAULT 24,
            activo TINYINT NOT NULL DEFAULT 1
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo_orden VARCHAR(50) UNIQUE NOT NULL,
            paciente_id INT NOT NULL,
            usuario_id INT NOT NULL,
            estado_orden VARCHAR(50) NOT NULL DEFAULT 'Pendiente',
            total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            metodo_pago VARCHAR(50) DEFAULT 'Efectivo',
            notas_clinicas TEXT,
            fecha_toma_muestra DATETIME,
            fecha_recepcion_muestra DATETIME,
            fecha_completada DATETIME,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE RESTRICT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orden_estudios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            orden_id INT NOT NULL,
            estudio_id INT NOT NULL,
            precio_unitario DECIMAL(10, 2) NOT NULL,
            estado_estudio VARCHAR(50) DEFAULT 'Pendiente',
            resultado_texto TEXT,
            valores_referencia TEXT,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id) ON DELETE CASCADE,
            FOREIGN KEY (estudio_id) REFERENCES estudios (id) ON DELETE RESTRICT
        );
        """)
    else:
        # Esquema para SQLite
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
    motor = "MariaDB" if is_using_mariadb() else "SQLite"
    print(f"Base de datos inicializada correctamente con motor: {motor}")
