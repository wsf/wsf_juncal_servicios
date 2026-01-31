# Guía de Instalación en Windows 7 - Sistema de Deudas Rurales

## 📋 Requisitos Previos

### Software Necesario:
- ✅ MySQL/MariaDB (ya instalado con base de datos `wsur`)
- ✅ Python 3.8 o superior
- ✅ Git para Windows (opcional, para descargar el código)
- ✅ Conexión a Internet (para la primera instalación)

---

## 🔧 PASO 1: Instalar Python 3.8+ en Windows 7

### Opción A: Descargar Python 3.8.10 (última versión compatible con Windows 7)

1. **Descargar Python:**
   - Ir a: https://www.python.org/downloads/release/python-3810/
   - Descargar: `Windows x86-64 executable installer` (64 bits)
   - O descargar: `Windows x86 executable installer` (32 bits si tu sistema es de 32 bits)

2. **Instalar Python:**
   - Ejecutar el instalador descargado
   - ⚠️ **MUY IMPORTANTE:** Marcar la casilla "Add Python 3.8 to PATH"
   - Hacer clic en "Install Now"
   - Esperar a que finalice la instalación

3. **Verificar instalación:**
   - Abrir "Símbolo del sistema" (cmd)
   - Ejecutar: `python --version`
   - Debe mostrar: `Python 3.8.10`

---

## 📥 PASO 2: Descargar el Proyecto

### Opción A: Con Git (Recomendado)

1. **Instalar Git para Windows:**
   - Descargar desde: https://git-scm.com/download/win
   - Instalar con opciones por defecto

2. **Clonar el repositorio:**
   ```cmd
   cd C:\
   git clone [URL_DEL_REPOSITORIO] deuda_servicios_juncal
   cd deuda_servicios_juncal
   ```

### Opción B: Descarga Manual (Sin Git)

1. **Descargar el código:**
   - Ir a la página del repositorio en GitHub
   - Hacer clic en "Code" → "Download ZIP"
   - Extraer el ZIP en `C:\deuda_servicios_juncal`

2. **Abrir carpeta:**
   ```cmd
   cd C:\deuda_servicios_juncal
   ```

---

## 🐍 PASO 3: Crear Entorno Virtual

1. **Abrir Símbolo del sistema (cmd) como Administrador**
   - Clic derecho en "Símbolo del sistema"
   - Seleccionar "Ejecutar como administrador"

2. **Navegar a la carpeta del proyecto:**
   ```cmd
   cd C:\deuda_servicios_juncal
   ```

3. **Crear entorno virtual:**
   ```cmd
   python -m venv venv
   ```

4. **Activar entorno virtual:**
   ```cmd
   venv\Scripts\activate
   ```
   
   Deberías ver `(venv)` al inicio de la línea de comandos.

---

## 📦 PASO 4: Instalar Dependencias

Con el entorno virtual activado:

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

**Tiempo estimado:** 2-5 minutos dependiendo de la conexión a Internet.

---

## ⚙️ PASO 5: Configurar el Archivo .env

1. **Copiar el archivo de ejemplo:**
   ```cmd
   copy .env.example .env
   ```

2. **Editar el archivo `.env`:**
   - Abrir con Bloc de notas: `notepad .env`
   - Configurar los valores:

   ```ini
   # Configuración de Base de Datos
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=dalas.2009
   DB_NAME=wsur

   # Configuración de Flask
   DEBUG=True
   PORT=5000
   HOST=0.0.0.0

   # Configuración de Groq LLM (Consultas IA)
   # Obtener en: https://console.groq.com/
   GROQ_API_KEY=tu_api_key_de_groq_aqui
   ```

3. **Guardar y cerrar** el archivo.

### 🤖 Obtener API Key de Groq (Para Consultas IA):

1. Ir a: https://console.groq.com/
2. Crear cuenta gratis (con Google o email)
3. Ir a "API Keys" → "Create API Key"
4. Copiar la key generada
5. Pegarla en el archivo `.env` en la línea `GROQ_API_KEY=`

---

## 🚀 PASO 6: Ejecutar la Aplicación

1. **Con el entorno virtual activado:**
   ```cmd
   python app.py
   ```

2. **Verificar que inició correctamente:**
   - Deberías ver algo como:
   ```
   * Running on http://127.0.0.1:5000
   * Running on http://192.168.x.x:5000
   ```

3. **Abrir en navegador:**
   - En la misma PC: http://127.0.0.1:5000 o http://localhost:5000
   - Desde otra PC en la red: http://[IP-DEL-SERVIDOR]:5000

---

## 🌐 PASO 7: Acceso desde Otras Computadoras

### A. Obtener la IP del servidor:

```cmd
ipconfig
```

Buscar "Dirección IPv4" (ejemplo: 192.168.1.100)

### B. Configurar Firewall de Windows:

1. **Abrir Firewall de Windows:**
   - Panel de Control → Sistema y Seguridad → Firewall de Windows
   - Clic en "Configuración avanzada"

2. **Crear regla de entrada:**
   - Clic derecho en "Reglas de entrada" → "Nueva regla"
   - Tipo: Puerto
   - Protocolo: TCP
   - Puerto: 5000
   - Acción: Permitir conexión
   - Perfil: Marcar todos
   - Nombre: "Flask Deudas Rurales"

3. **Verificar desde otra PC:**
   - Abrir navegador en otra computadora
   - Ir a: http://192.168.1.100:5000 (usar la IP del servidor)

---

## 🔄 PASO 8: Ejecutar Automáticamente al Iniciar Windows

### Opción A: Crear Acceso Directo en Inicio

1. **Crear archivo BAT:**
   - Crear archivo: `C:\deuda_servicios_juncal\iniciar.bat`
   - Contenido:
   ```batch
   @echo off
   cd C:\deuda_servicios_juncal
   call venv\Scripts\activate
   python app.py
   pause
   ```

2. **Crear acceso directo:**
   - Clic derecho en `iniciar.bat` → "Crear acceso directo"
   - Mover el acceso directo a:
     `C:\Users\[USUARIO]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

### Opción B: Como Servicio de Windows (Avanzado)

Ver documentación adicional o usar herramientas como NSSM (Non-Sucking Service Manager).

---

## 📝 PASO 9: Uso Diario

### Iniciar la aplicación:

1. **Abrir Símbolo del sistema**
2. **Ejecutar:**
   ```cmd
   cd C:\deuda_servicios_juncal
   venv\Scripts\activate
   python app.py
   ```

3. **Mantener la ventana abierta** mientras se usa el sistema

### Detener la aplicación:

- Presionar `Ctrl + C` en la ventana del Símbolo del sistema
- O cerrar la ventana

---

## 🔧 Solución de Problemas

### Problema: "python no se reconoce como comando"
**Solución:**
- Python no está en PATH
- Reinstalar Python marcando "Add Python to PATH"
- O agregar manualmente: `C:\Python38\` a la variable PATH del sistema

### Problema: "Error al conectar con MySQL"
**Solución:**
- Verificar que MySQL está corriendo
- Verificar usuario/contraseña en `.env`
- Verificar que la base de datos `wsur` existe
- Probar conexión: `mysql -u root -pdalas.2009 wsur`

### Problema: "Error al instalar dependencias"
**Solución:**
```cmd
python -m pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

### Problema: "No puedo acceder desde otra PC"
**Solución:**
- Verificar que el firewall permite el puerto 5000
- Verificar que HOST=0.0.0.0 en el archivo `.env`
- Hacer ping a la IP del servidor desde otra PC
- Verificar que ambas PCs están en la misma red

### Problema: "Groq API no funciona"
**Solución:**
- Verificar que la API key es correcta en `.env`
- Verificar conexión a Internet
- La funcionalidad de consultas IA es opcional, el resto del sistema funciona sin ella

### Problema: "Puerto 5000 ya en uso"
**Solución:**
```cmd
netstat -ano | findstr :5000
taskkill /PID [numero_del_proceso] /F
```

---

## 📊 Verificación de Instalación Exitosa

Si todo está bien configurado, deberías poder:

✅ Abrir http://localhost:5000 y ver la página principal
✅ Ver los KPIs al hacer clic en "Actualizar Indicadores"
✅ Acceder al "Listado Completo" y ver todos los contribuyentes
✅ Buscar contribuyentes por nombre
✅ Ver liquidaciones individuales
✅ Hacer consultas con el asistente de IA (si configuraste Groq)
✅ Acceder desde otras PCs en la red local

---

## 📞 Soporte Adicional

Si encuentras problemas no listados aquí:

1. Verificar los logs en la ventana del Símbolo del sistema
2. Anotar el mensaje de error exacto
3. Verificar que todos los pasos se siguieron correctamente
4. Consultar el archivo GROQ_SETUP.md para configuración de IA

---

## 🔄 Actualizar el Sistema

Para actualizar a una nueva versión:

```cmd
cd C:\deuda_servicios_juncal
git pull
venv\Scripts\activate
pip install -r requirements.txt --upgrade
python app.py
```

---

## 📁 Estructura de Archivos

```
C:\deuda_servicios_juncal\
├── venv\                    (entorno virtual - no tocar)
├── static\                  (archivos CSS)
├── templates\               (páginas HTML)
├── app.py                   (aplicación principal)
├── requirements.txt         (dependencias)
├── .env                     (configuración - IMPORTANTE)
├── .env.example            (ejemplo de configuración)
├── README.md               (documentación general)
├── GROQ_SETUP.md           (configuración IA)
└── iniciar.bat             (script de inicio)
```

---

## ⚠️ Notas Importantes

- **Seguridad:** No exponer el servidor directamente a Internet sin configurar autenticación
- **Backups:** Hacer respaldo regular de la base de datos MySQL
- **API Keys:** Mantener las API keys en el archivo `.env` (nunca compartir públicamente)
- **Performance:** Windows 7 puede ser más lento, se recomienda Windows 10 o superior para mejor rendimiento
- **Soporte:** Windows 7 ya no tiene soporte oficial de Microsoft, considerar migrar a Windows 10/11

---

## ✅ Checklist Final

Antes de dar por terminada la instalación, verificar:

- [ ] Python 3.8+ instalado y en PATH
- [ ] Proyecto descargado en `C:\deuda_servicios_juncal`
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas sin errores
- [ ] Archivo `.env` configurado correctamente
- [ ] MySQL corriendo con base de datos `wsur`
- [ ] Aplicación inicia sin errores
- [ ] Página principal carga en el navegador
- [ ] KPIs funcionan correctamente
- [ ] Listado de deudas muestra datos
- [ ] Acceso desde red local funciona (si es necesario)
- [ ] Firewall configurado (si acceso remoto)
- [ ] API de Groq configurada (opcional)

**¡Instalación completada exitosamente!** 🎉
