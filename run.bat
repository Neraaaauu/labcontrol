@echo off
title LabControl - Servidor Local
echo =============================================
echo   Iniciando LabControl - Laboratorio Clinico
echo =============================================

:: Inicializar base de datos y datos ficticios de prueba
python seed_data.py

echo.
echo [*] Servidor disponible en: http://127.0.0.1:5000
echo [*] Roles de demostracion:
echo     - Admin:    admin / admin123
echo     - Usuario:  recepcion / recepcion123
echo =============================================

python app.py
pause
