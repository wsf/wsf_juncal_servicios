# Guía de Configuración - Sistema de Deuda Servicios Juncal

## Configuración de Base de Datos

Este sistema utiliza un archivo `.env` para configurar la conexión a la base de datos. Esto permite instalar la aplicación en diferentes ambientes sin modificar el código.

### Pasos para Configurar

1. **Copiar el archivo de ejemplo**
   ```bash
   cp .env.example .env
   ```

2. **Editar el archivo .env con los datos de tu servidor**
   
   Abrir el archivo `.env` con un editor de texto y modificar los valores:

   ```ini
   # Configuración de Base de Datos
   DB_HOST=192.168.1.100        # IP del servidor de base de datos en tu red local
   DB_PORT=3306                  # Puerto de MySQL/MariaDB
   DB_USER=usuario_db            # Usuario de la base de datos
   DB_PASSWORD=contraseña_db     # Contraseña del usuario
   DB_NAME=wsur                  # Nombre de la base de datos

   # Configuración de Flask
   DEBUG=False                   # Poner en False en producción
   PORT=5000                     # Puerto donde correrá la aplicación
   HOST=0.0.0.0                  # 0.0.0.0 permite acceso desde red local
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

### Ejemplos de Configuración

#### Servidor Local (mismo equipo)
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=mi_contraseña
DB_NAME=wsur
```

#### Servidor en Red Local
```ini
DB_HOST=192.168.0.50          # IP del servidor MySQL en la red
DB_PORT=3306
DB_USER=admin_juncal
DB_PASSWORD=contraseña_segura
DB_NAME=wsur
```

#### Servidor con Puerto Personalizado
```ini
DB_HOST=10.0.0.15
DB_PORT=3307                   # Puerto personalizado
DB_USER=juncal_user
DB_PASSWORD=pass123
DB_NAME=wsur
```

### Seguridad

- ⚠️ **IMPORTANTE**: El archivo `.env` contiene información sensible (contraseñas)
- ✅ El archivo `.env` está incluido en `.gitignore` para no subirlo a repositorios
- ✅ Usar `.env.example` como plantilla sin datos sensibles
- 🔒 En producción, usar contraseñas fuertes y usuario con permisos limitados
- 🔒 Asegurar que solo el usuario del sistema que ejecuta la app pueda leer el archivo `.env`

### Permisos Recomendados de Usuario MySQL

Para mayor seguridad, crear un usuario específico con permisos limitados:

```sql
-- Crear usuario específico para la aplicación
CREATE USER 'juncal_app'@'%' IDENTIFIED BY 'contraseña_segura';

-- Otorgar solo los permisos necesarios
GRANT SELECT, INSERT, UPDATE ON wsur.* TO 'juncal_app'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;
```

Luego configurar en `.env`:
```ini
DB_USER=juncal_app
DB_PASSWORD=contraseña_segura
```

### Solución de Problemas

**Error de conexión a la base de datos:**
1. Verificar que el servidor MySQL esté corriendo
2. Verificar que el host/IP sea accesible desde el equipo donde corre la app
3. Verificar usuario y contraseña
4. Verificar que el puerto esté abierto en el firewall
5. Para conexiones remotas, verificar que MySQL acepte conexiones desde la red:
   ```sql
   -- Verificar bind-address en my.cnf/my.ini
   -- Debe ser 0.0.0.0 o la IP específica, no 127.0.0.1
   ```

**La aplicación no lee el archivo .env:**
1. Verificar que el archivo se llame exactamente `.env` (no `.env.txt`)
2. Verificar que esté en el mismo directorio que `app.py`
3. Verificar que `python-dotenv` esté instalado: `pip install python-dotenv`

### Variables de Configuración Disponibles

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| DB_HOST | Servidor de base de datos | localhost |
| DB_PORT | Puerto MySQL/MariaDB | 3306 |
| DB_USER | Usuario de la base de datos | root |
| DB_PASSWORD | Contraseña del usuario | (vacío) |
| DB_NAME | Nombre de la base de datos | wsur |
| DEBUG | Modo debug de Flask | True |
| PORT | Puerto de la aplicación web | 5000 |
| HOST | Host de la aplicación | 0.0.0.0 |

### Acceso desde Red Local

Para que otros equipos en la red local puedan acceder a la aplicación:

1. Configurar en `.env`:
   ```ini
   HOST=0.0.0.0
   PORT=5000
   ```

2. Obtener la IP del servidor donde corre la app:
   ```bash
   # En Linux
   ip addr show
   
   # O usar
   hostname -I
   ```

3. Acceder desde otros equipos usando:
   ```
   http://IP_DEL_SERVIDOR:5000
   ```
   Ejemplo: `http://192.168.0.112:5000`

### Contacto

Para soporte técnico o consultas sobre la configuración, contactar al administrador del sistema.
