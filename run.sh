#!/usr/bin/env bash
# Script de arranque rápido para LabControl
cd "$(dirname "$0")"

echo "============================================="
echo "  Iniciando LabControl - Laboratorio Clínico "
echo "============================================="

# Inicializar BD con datos semilla si no existe
if [ ! -f "instance/labcontrol.db" ]; then
    echo "[*] Creando base de datos inicial y cargando datos semilla..."
    python3 seed_data.py
fi

echo "[*] Servidor disponible en: http://127.0.0.1:5000"
echo "[*] Roles de demostración:"
echo "    - Admin:    admin / admin123"
echo "    - Usuario:  recepcion / recepcion123"
echo "============================================="

python3 app.py
