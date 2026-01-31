# Instrucciones de Instalación en Red Local

## Configuración Rápida para Servidor en Red Local

### 1. Transferir los archivos al servidor

Copiar toda la carpeta del proyecto al servidor donde se instalará.

### 2. Configurar la conexión a la base de datos

1. Copiar el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```

2. Editar el archivo `.env` con los datos del servidor MySQL en tu red:
   ```bash
   nano .env
   ```
   
   O con cualquier editor de texto, modificar estas líneas:
   ```ini
   DB_HOST=192.168.X.X          # IP del servidor MySQL en la red local
   DB_PORT=3306
   DB_USER=usuario_mysql
   DB_PASSWORD=tu_contraseña
   DB_NAME=wsur
   ```

### 3. Instalar Python y dependencias

```bash
# Verificar que Python 3.8+ esté instalado
python3 --version

# Crear entorno virtual
python3 -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Verificar la conexión a la base de datos

```bash
python -c "from app import get_db_connection; conn = get_db_connection(); print('✅ Conexión exitosa'); conn.close()"
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en:
- Servidor local: `http://localhost:5000`
- Red local: `http://IP_DEL_SERVIDOR:5000`

Para obtener la IP del servidor:
```bash
hostname -I
```

### Ejemplo de Configuración Completa

**Escenario:** Base de datos MySQL en servidor 192.168.0.50, aplicación en servidor 192.168.0.100

**Archivo .env:**
```ini
DB_HOST=192.168.0.50
DB_PORT=3306
DB_USER=juncal_app
DB_PASSWORD=MiClaveSegura123
DB_NAME=wsur

DEBUG=False
PORT=5000
HOST=0.0.0.0
```

**Acceso desde otros equipos en la red:**
```
http://192.168.0.100:5000
```

### Ejecutar como Servicio (Producción)

Para que la aplicación se ejecute automáticamente al iniciar el servidor:

#### Opción 1: systemd (Linux)

Crear archivo `/etc/systemd/system/deuda-juncal.service`:

```ini
[Unit]
Description=Sistema Deuda Servicios Juncal
After=network.target mysql.service

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/al/proyecto/deuda_servicios_juncal
Environment="PATH=/ruta/al/proyecto/deuda_servicios_juncal/.venv/bin"
ExecStart=/ruta/al/proyecto/deuda_servicios_juncal/.venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar el servicio:
```bash
sudo systemctl enable deuda-juncal
sudo systemctl start deuda-juncal
sudo systemctl status deuda-juncal
```

#### Opción 2: Servidor Gunicorn (Producción)

```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Configuración del Firewall

Si el firewall está activo, abrir el puerto:

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 5000

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### Solución de Problemas

**"ModuleNotFoundError: No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**"Access denied for user"**
- Verificar usuario y contraseña en `.env`
- Verificar que el usuario MySQL tenga permisos
- Si la conexión es remota, verificar que el usuario pueda conectarse desde esa IP

**"Can't connect to MySQL server"**
- Verificar que MySQL esté corriendo: `sudo systemctl status mysql`
- Verificar que el firewall permita conexiones al puerto 3306
- Verificar el bind-address en `/etc/mysql/mysql.conf.d/mysqld.cnf`

**"Address already in use"**
- Cambiar el puerto en `.env` (por ejemplo, PORT=5001)
- O detener la aplicación que está usando el puerto 5000

Para más detalles, consultar [CONFIG_README.md](CONFIG_README.md).
