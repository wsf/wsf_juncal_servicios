@echo off
REM ================================================
REM Script de Instalación Automática
REM Sistema de Deudas Rurales - Comuna de Juncal
REM ================================================

echo.
echo ========================================
echo  INSTALACION SISTEMA DEUDAS RURALES
echo  Comuna de Juncal
echo ========================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo.
    echo Por favor instalar Python 3.8+ desde:
    echo https://www.python.org/downloads/release/python-3810/
    echo.
    echo IMPORTANTE: Marcar "Add Python to PATH" durante instalacion
    pause
    exit /b 1
)

echo [OK] Python instalado correctamente
python --version
echo.

REM Verificar que estamos en la carpeta correcta
if not exist "requirements.txt" (
    echo [ERROR] No se encuentra requirements.txt
    echo.
    echo Por favor ejecutar este script desde la carpeta del proyecto:
    echo C:\deuda_servicios_juncal\
    pause
    exit /b 1
)

echo [1/5] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado
echo.

echo [2/5] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

echo [3/5] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip actualizado
echo.

echo [4/5] Instalando dependencias...
echo (Esto puede tardar 2-5 minutos dependiendo de tu conexion)
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

echo [5/5] Configurando archivo .env...
if exist ".env" (
    echo [INFO] El archivo .env ya existe, no se sobreescribira
) else (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Archivo .env creado desde .env.example
        echo.
        echo ========================================
        echo  IMPORTANTE: CONFIGURAR .env
        echo ========================================
        echo.
        echo Debes editar el archivo .env con tu configuracion:
        echo - DB_HOST (generalmente localhost)
        echo - DB_USER (generalmente root)
        echo - DB_PASSWORD (tu contraseña de MySQL)
        echo - GROQ_API_KEY (obtener gratis en https://console.groq.com/)
        echo.
        echo Presiona cualquier tecla para abrir .env en Bloc de notas...
        pause >nul
        notepad .env
    ) else (
        echo [ADVERTENCIA] No se encuentra .env.example
    )
)
echo.

echo ========================================
echo  INSTALACION COMPLETADA
echo ========================================
echo.
echo Proximos pasos:
echo.
echo 1. Verificar configuracion en .env
echo 2. Asegurarse que MySQL esta corriendo
echo 3. Ejecutar: iniciar.bat
echo.
echo Para iniciar el sistema ahora, ejecuta:
echo    venv\Scripts\activate
echo    python app.py
echo.
pause
