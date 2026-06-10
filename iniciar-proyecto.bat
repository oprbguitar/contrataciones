@echo off
title ContrataRadar - Servidor local
echo ==========================================
echo Iniciando ContrataRadar en modo local...
echo ==========================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python no esta instalado en el sistema.
    echo Intentando abrir docs/index.html directamente en tu navegador...
    start docs\index.html
    pause
    exit /b
)

echo Levantando servidor local en http://localhost:8000 ...
echo Abriendo el navegador automaticamente...
echo.
echo Para cerrar el servidor, cierra esta ventana o presiona Ctrl+C.
echo ==========================================

:: Abrir el navegador en el puerto local
start http://localhost:8000/

:: Cambiar al directorio docs y levantar el servidor
cd docs
python -m http.server 8000

pause
