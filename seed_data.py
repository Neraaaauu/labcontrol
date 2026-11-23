from werkzeug.security import generate_password_hash
from database import get_db, init_db
import datetime

def seed_database():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # 1. Usuarios con roles clínicos específicos (NOM-007-SSA3)
    usuarios = [
        (
            'admin',
            generate_password_hash('admin123'),
            'QFB. Carlos Méndez',
            'admin',
            '8472910 UABC',
            'Dirección General y Aseguramiento de Calidad',
            'Jornada Administrativa',
            1
        ),
        (
            'recepcion',
            generate_password_hash('recepcion123'),
            'Laura Morales',
            'recepcion',
            'EMP-0412',
            'Atención a Pacientes, Admisión y Cobro',
            'Matutino (Ventanilla 1)',
            1
        ),
        (
            'quimico',
            generate_password_hash('quimico123'),
            'Q.F.B. Roberto Salcedo García',
            'quimico',
            '9384721 UABC',
            'Bioquímica Clínica y Hematología Automatizada',
            'Laboratorio Analítico Central',
            1
        ),
        (
            'doctor',
            generate_password_hash('doctor123'),
            'Dr. Alejandro Peña Treviño',
            'medico',
            'Ced. Méd. 5629143 / Esp. Patología 928371',
            'Patología Clínica y Diagnóstico de Laboratorio',
            'Responsable Sanitario y Validación Médica',
            1
        )
    ]

    for u in usuarios:
        cursor.execute("""
            INSERT OR REPLACE INTO usuarios (username, password_hash, nombre_completo, rol, cedula_profesional, especialidad, turno, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, u)

    conn.commit()

    # Mapeo de IDs de usuarios
    cursor.execute("SELECT id, username FROM usuarios")
    usuarios_map = {row[1]: row[0] for row in cursor.fetchall()}
    u_admin_id = usuarios_map.get('admin', 1)
    u_recepcion_id = usuarios_map.get('recepcion', 2)
    u_quimico_id = usuarios_map.get('quimico', 1)
    u_doctor_id = usuarios_map.get('doctor', 1)

    # 2. Catálogo de Estudios de Laboratorio Clínico
    estudios = [
        (
            'BH-01',
            'Biometría Hemática Completa (Citometría Hemática)',
            'Hematología',
            'Evalúa glóbulos rojos, glóbulos blancos, hemoglobina, hematocrito y plaquetas.',
            'Sangre venosa - Tubo lila con EDTA',
            'Ayuno mínimo de 4 a 8 horas.',
            220.0,
            12
        ),
        (
            'QS-06',
            'Química Sanguínea de 6 Elementos',
            'Bioquímica Clínica',
            'Glucosa, Urea, Creatinina, Ácido Úrico, Colesterol total y Triglicéridos.',
            'Sangre venosa - Tubo rojo sin anticoagulante con gel separador',
            'Ayuno estricto de 8 a 12 horas. No ingerir alcohol 24 horas antes.',
            380.0,
            24
        ),
        (
            'GLU-01',
            'Glucosa Sérica en Ayuno',
            'Bioquímica Clínica',
            'Medición de concentración de glucosa en plasma sanguíneo.',
            'Sangre venosa - Tubo gris o rojo',
            'Ayuno de 8 a 10 horas antes de la toma.',
            90.0,
            6
        ),
        (
            'EGO-01',
            'Examen General de Orina (EGO)',
            'Uroanálisis',
            'Análisis físico, químico y microscópico del sedimento urinario.',
            'Primera orina de la mañana - Frasco recolector estéril',
            'Aseo genital previo. Recolectar chorro medio de la primera micción matutina.',
            130.0,
            8
        ),
        (
            'LIP-01',
            'Perfil Lipídico Completo',
            'Bioquímica Clínica',
            'Colesterol total, HDL, LDL, VLDL y Triglicéridos.',
            'Sangre venosa - Tubo rojo con gel separador',
            'Ayuno de 12 a 14 horas obligatorio.',
            320.0,
            24
        ),
        (
            'TIR-01',
            'Perfil Tiroideo Básico (TSH, T3L, T4L)',
            'Endocrinología / Inmunología',
            'Determinación de hormonas tiroideas para diagnóstico de hipo/hipertiroidismo.',
            'Sangre venosa - Tubo amarillo con gel separador',
            'Ayuno de 8 horas. No tomar medicamento tiroideo previo a la toma.',
            550.0,
            36
        ),
        (
            'COP-03',
            'Coproparasitoscópico Seriado (3 muestras)',
            'Coprología',
            'Búsqueda e identificación de quistes, trofozoítos y huevecillos parasitarios.',
            'Materia fecal fresca - Frasco plástico estéril',
            'Recolectar una muestra al día durante 3 días consecutivos.',
            260.0,
            48
        ),
        (
            'HCG-01',
            'Prueba Inmunológica de Embarazo (hCG en suero)',
            'Inmunología',
            'Detección cuantitativa de la hormona gonadotropina coriónica humana.',
            'Sangre venosa - Tubo rojo',
            'Ayuno no indispensable (mínimo 2 horas).',
            180.0,
            4
        )
    ]

    for est in estudios:
        cursor.execute("""
            INSERT OR IGNORE INTO estudios (codigo, nombre, categoria, descripcion, tipo_muestra, indicaciones, precio, tiempo_entrega_horas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, est)

    # 3. Pacientes Ficticios
    pacientes = [
        (
            'María Fernanda',
            'García López',
            'GALM880415HBCRLA01',
            '1988-04-15',
            'F',
            '664-555-1234',
            'maria.garcia.demo@correo.com',
            '22000',
            'Zona Centro',
            'Tijuana',
            'Baja California',
            'Av. Constitución #1420 Int. 3'
        ),
        (
            'Roberto',
            'Hernández Vega',
            'HEVR920722HBCRBN03',
            '1992-07-22',
            'M',
            '664-555-5678',
            'roberto.hdz.demo@correo.com',
            '22400',
            'Mesa de Otay',
            'Tijuana',
            'Baja California',
            'Calzada Tecnológico #2050'
        ),
        (
            'Ana Patricia',
            'Torres Navarro',
            'TONA951130MBCRRA08',
            '1995-11-30',
            'F',
            '664-555-9012',
            'ana.torres.demo@correo.com',
            '22200',
            'Playas de Tijuana',
            'Tijuana',
            'Baja California',
            'Paseo Playas #455'
        ),
        (
            'Jorge Alberto',
            'Ramírez Soto',
            'RASJ800310HBCMGN05',
            '1980-03-10',
            'M',
            '664-555-3456',
            'jorge.ramirez.demo@correo.com',
            '22100',
            'La Mesa',
            'Tijuana',
            'Baja California',
            'Blvd. Díaz Ordaz #12300'
        ),
        (
            'Valeria',
            'Castillo Mendoza',
            'CAMV010905MBCSLR02',
            '2001-09-05',
            'F',
            '664-555-7890',
            'valeria.castillo.demo@correo.com',
            '22424',
            'Altabrisa',
            'Tijuana',
            'Baja California',
            'Circuito Las Brisas #88'
        )
    ]

    for p in pacientes:
        cursor.execute("""
            INSERT OR IGNORE INTO pacientes 
            (nombre, apellido, curp, fecha_nacimiento, sexo, telefono, email, codigo_postal, colonia, municipio, estado, direccion_calle)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    conn.commit()

    # 4. Órdenes con Diferentes Estados del Flujo
    # Obtenemos IDs
    cursor.execute("SELECT id FROM usuarios WHERE username = 'recepcion'")
    u_recepcion_id = cursor.fetchone()[0]

    cursor.execute("SELECT id, codigo, precio FROM estudios")
    estudios_map = {row['codigo']: (row['id'], row['precio']) for row in cursor.fetchall()}

    cursor.execute("SELECT id FROM pacientes ORDER BY id ASC")
    paciente_ids = [row[0] for row in cursor.fetchall()]

    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    two_days_ago = now - datetime.timedelta(days=2)

    # Orden 1: Completada con resultados listos y avalada por el médico
    cursor.execute("""
        INSERT OR IGNORE INTO ordenes 
        (codigo_orden, paciente_id, usuario_id, quimico_id, medico_id, estado_orden, total, metodo_pago, notas_clinicas, interpretacion_medica, fecha_toma_muestra, fecha_recepcion_muestra, fecha_completada, creado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'ORD-2026-1001',
        paciente_ids[0],
        u_recepcion_id,
        u_quimico_id,
        u_doctor_id,
        'Completada',
        310.0,
        'Efectivo',
        'Chequeo general de rutina. Paciente en ayunas.',
        'Parámetros hematológicos y glucémicos dentro de los rangos de referencia esperados para paciente adulto femenino. Sin evidencia de anemia ni alteraciones en la serie blanca. Se avala resultado oficial.',
        two_days_ago.strftime('%Y-%m-%d 08:30:00'),
        two_days_ago.strftime('%Y-%m-%d 09:00:00'),
        yesterday.strftime('%Y-%m-%d 14:00:00'),
        two_days_ago.strftime('%Y-%m-%d 08:15:00')
    ))

    # Actualizar si ya existía para asegurar vinculación con químico y médico
    cursor.execute("""
        UPDATE ordenes 
        SET quimico_id = ?, medico_id = ?, 
            interpretacion_medica = 'Parámetros hematológicos y glucémicos dentro de los rangos de referencia esperados para paciente adulto femenino. Sin evidencia de anemia ni alteraciones en la serie blanca. Se avala resultado oficial.'
        WHERE codigo_orden = 'ORD-2026-1001'
    """, (u_quimico_id, u_doctor_id))

    cursor.execute("SELECT id FROM ordenes WHERE codigo_orden = 'ORD-2026-1001'")
    ord1_id = cursor.fetchone()[0]

    # Estudios orden 1: BH-01 y GLU-01
    cursor.execute("""
        INSERT OR IGNORE INTO orden_estudios (orden_id, estudio_id, precio_unitario, estado_estudio, resultado_texto, valores_referencia)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ord1_id, estudios_map['BH-01'][0], estudios_map['BH-01'][1], 'Completado', 
          'Hemoglobina: 14.2 g/dL | Leucocitos: 6,800 /uL | Plaquetas: 245,000 /uL (Dentro de parámetros)', 
          'Hemoglobina: 12.0 - 15.5 g/dL, Leucocitos: 4,500 - 10,000 /uL'))
    cursor.execute("""
        INSERT OR IGNORE INTO orden_estudios (orden_id, estudio_id, precio_unitario, estado_estudio, resultado_texto, valores_referencia)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ord1_id, estudios_map['GLU-01'][0], estudios_map['GLU-01'][1], 'Completado', 
          'Glucosa: 88.5 mg/dL (Normoglicemia)', 
          '70.0 - 99.0 mg/dL en ayuno'))

    # Orden 2: En Análisis
    cursor.execute("""
        INSERT OR IGNORE INTO ordenes 
        (codigo_orden, paciente_id, usuario_id, estado_orden, total, metodo_pago, notas_clinicas, fecha_toma_muestra, fecha_recepcion_muestra, creado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'ORD-2026-1002',
        paciente_ids[1],
        u_recepcion_id,
        'En Análisis',
        700.0,
        'Tarjeta de Débito',
        'Control metabólico y perfil lipídico solicitado por endocrinólogo.',
        yesterday.strftime('%Y-%m-%d 07:45:00'),
        yesterday.strftime('%Y-%m-%d 08:15:00'),
        yesterday.strftime('%Y-%m-%d 07:30:00')
    ))

    cursor.execute("SELECT id FROM ordenes WHERE codigo_orden = 'ORD-2026-1002'")
    ord2_id = cursor.fetchone()[0]
    cursor.execute("""
        INSERT OR IGNORE INTO orden_estudios (orden_id, estudio_id, precio_unitario, estado_estudio)
        VALUES (?, ?, ?, ?)
    """, (ord2_id, estudios_map['QS-06'][0], estudios_map['QS-06'][1], 'En Análisis'))
    cursor.execute("""
        INSERT OR IGNORE INTO orden_estudios (orden_id, estudio_id, precio_unitario, estado_estudio)
        VALUES (?, ?, ?, ?)
    """, (ord2_id, estudios_map['LIP-01'][0], estudios_map['LIP-01'][1], 'En Análisis'))

    # Orden 3: Muestra Recibida
    cursor.execute("""
        INSERT OR IGNORE INTO ordenes 
        (codigo_orden, paciente_id, usuario_id, estado_orden, total, metodo_pago, notas_clinicas, fecha_toma_muestra, fecha_recepcion_muestra, creado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'ORD-2026-1003',
        paciente_ids[2],
        u_recepcion_id,
        'Muestra Recibida',
        130.0,
        'Transferencia SPEI',
        'Sospecha de infección de vías urinarias.',
        now.strftime('%Y-%m-%d 09:10:00'),
        now.strftime('%Y-%m-%d 09:25:00'),
        now.strftime('%Y-%m-%d 09:00:00')
    ))
    cursor.execute("SELECT id FROM ordenes WHERE codigo_orden = 'ORD-2026-1003'")
    ord3_id = cursor.fetchone()[0]
    cursor.execute("""
        INSERT OR IGNORE INTO orden_estudios (orden_id, estudio_id, precio_unitario, estado_estudio)
        VALUES (?, ?, ?, ?)
    """, (ord3_id, estudios_map['EGO-01'][0], estudios_map['EGO-01'][1], 'Muestra Recibida'))

    # Orden 4: Pendiente de muestra
    cursor.execute("""
        INSERT OR IGNORE INTO ordenes 
        (codigo_orden, paciente_id, usuario_id, estado_orden, total, metodo_pago, notas_clinicas, creado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'ORD-2026-1004',
        paciente_ids[3],
        u_recepcion_id,
        'Pendiente',
        550.0,
        'Efectivo',
        'Cita programada para toma sanguínea.',
        now.strftime('%Y-%m-%d 10:15:00')
    ))
    cursor.execute("SELECT id FROM ordenes WHERE codigo_orden = 'ORD-2026-1004'")
    ord4_id = cursor.fetchone()[0]
    cursor.execute("""
        INSERT OR IGNORE INTO orden_estudios (orden_id, estudio_id, precio_unitario, estado_estudio)
        VALUES (?, ?, ?, ?)
    """, (ord4_id, estudios_map['TIR-01'][0], estudios_map['TIR-01'][1], 'Pendiente'))

    conn.commit()
    conn.close()
    print("Datos semilla cargados con éxito (Usuarios, Estudios, Pacientes y Órdenes).")

if __name__ == '__main__':
    seed_database()
