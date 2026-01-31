# Guía Rápida de Despliegue - Windows 7

## 🚀 Instalación Express (3 pasos)

### 1️⃣ Instalar Python 3.8.10
- Descargar: https://www.python.org/downloads/release/python-3810/
- ⚠️ **IMPORTANTE:** Marcar "Add Python to PATH"

### 2️⃣ Copiar proyecto
```cmd
# Copiar toda la carpeta del proyecto a:
C:\deuda_servicios_juncal
```

### 3️⃣ Ejecutar instalador
```cmd
cd C:\deuda_servicios_juncal
instalar.bat
```

## 🎯 Uso Diario

### Iniciar sistema:
```cmd
doble clic en: iniciar.bat
```

### Acceder:
- En la misma PC: http://localhost:5000
- Desde otra PC: http://192.168.x.x:5000

## ⚙️ Configuración Base de Datos

Editar archivo `.env`:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=dalas.2009
DB_NAME=wsur
```

## 📱 Acceso en Red Local

1. **Obtener IP del servidor:**
   ```cmd
   ipconfig
   ```
   (Anotar Dirección IPv4: ej. 192.168.1.100)

2. **Configurar Firewall:**
   - Panel de Control → Firewall
   - Permitir puerto 5000 (TCP)

3. **Acceder desde otras PCs:**
   ```
   http://192.168.1.100:5000
   ```

## 🆘 Problemas Comunes

### No encuentra Python
```cmd
# Reinstalar Python marcando "Add to PATH"
```

### Error de MySQL
```cmd
# Verificar que MySQL está corriendo
# Verificar usuario/contraseña en .env
```

### No puedo acceder desde otra PC
```cmd
# 1. Verificar firewall (puerto 5000)
# 2. Verificar que HOST=0.0.0.0 en .env
# 3. Hacer ping a la IP del servidor
```

## 📋 Archivos Importantes

- `instalar.bat` - Instala todo automáticamente
- `iniciar.bat` - Inicia el sistema
- `.env` - Configuración (usuario, contraseña, etc.)
- `INSTALACION_WINDOWS.md` - Guía completa detallada

## ✅ Checklist

- [ ] Python 3.8+ instalado
- [ ] Proyecto en C:\deuda_servicios_juncal
- [ ] Ejecutado instalar.bat sin errores
- [ ] Archivo .env configurado
- [ ] MySQL corriendo
- [ ] Sistema accesible en localhost:5000

---

**Para más detalles ver:** `INSTALACION_WINDOWS.md`
