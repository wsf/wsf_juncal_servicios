@echo off
REM ================================================
REM Iniciador Rápido con Navegador Automático
REM Sistema Deudas Rurales - Comuna de Juncal
REM ================================================

cd /d "%~dp0"

REM Verificar entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Ejecutar primero instalar.bat
    pause
    exit /b 1
)

REM Verificar .env
if not exist ".env" (
    echo ERROR: Archivo .env no encontrado
    pause
    exit /b 1
)

echo Iniciando Sistema Deudas Rurales...
echo.

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Iniciar Flask en segundo plano
start /B python app.py

REM Esperar 3 segundos para que Flask inicie
echo Esperando que el servidor inicie...
timeout /t 3 /nobreak >nul

REM Abrir navegador automáticamente
start http://localhost:5000

echo.
echo ========================================
echo  Sistema iniciado correctamente
echo ========================================
echo.
echo El navegador se abrio automaticamente en:
echo http://localhost:5000
echo.
echo Para DETENER el servidor:
echo   1. Cierra esta ventana
echo   2. O presiona Ctrl + C
echo.

REM Mantener la ventana abierta
pause >nul
