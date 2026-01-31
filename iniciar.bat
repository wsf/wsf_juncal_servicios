@echo off
REM ================================================
REM Script de Inicio - Sistema Deudas Rurales
REM ================================================

echo.
echo ========================================
echo  SISTEMA DEUDAS RURALES
echo  Comuna de Juncal
echo ========================================
echo.

REM Cambiar a la carpeta del proyecto
cd /d "%~dp0"

REM Verificar que existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado
    echo.
    echo Por favor ejecutar primero: instalar.bat
    echo.
    pause
    exit /b 1
)

REM Verificar que existe el archivo .env
if not exist ".env" (
    echo [ERROR] Archivo .env no encontrado
    echo.
    echo Por favor crear el archivo .env con la configuracion
    echo Puedes copiar .env.example como base
    echo.
    pause
    exit /b 1
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando servidor Flask...
echo.
echo ========================================
echo  INSTRUCCIONES:
echo ========================================
echo.
echo El servidor se iniciara en unos segundos
echo.
echo Para acceder al sistema:
echo   - Desde esta PC: http://localhost:5000
echo   - Desde otra PC: http://[IP-DE-ESTA-PC]:5000
echo.
echo Para detener el servidor:
echo   - Presiona Ctrl + C
echo   - O cierra esta ventana
echo.
echo ========================================
echo.

REM Iniciar Flask
python app.py

REM Si Flask se detiene, pausar para ver mensajes de error
echo.
echo.
echo El servidor se ha detenido.
pause
