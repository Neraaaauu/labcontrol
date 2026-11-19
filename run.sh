#!/usr/bin/env bash
# Script de arranque rápido para LabControl
cd "$(dirname "$0")"

echo "============================================="
echo "  Iniciando LabControl - Laboratorio Clínico "
echo "============================================="

# Asegurar que MariaDB (servicio de usuario) esté activo
systemctl --user start mariadb-user 2>/dev/null || true

# Inicializar y verificar BD
python3 seed_data.py

echo "[*] Servidor disponible en: http://127.0.0.1:5000"
echo "[*] Roles de demostración:"
echo "    - Admin:    admin / admin123"
echo "    - Usuario:  recepcion / recepcion123"
echo "============================================="

python3 app.py
