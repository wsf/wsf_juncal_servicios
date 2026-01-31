# Sistema de Liquidación de Deudas - Servicios Rurales Juncal

Sistema web desarrollado en Flask para gestionar y generar liquidaciones de deuda de contribuyentes rurales del Municipio de Juncal.

## Características

- 🔍 Búsqueda dinámica de contribuyentes por apellido o nombre
- 📊 Cálculo automático de deuda basado en:
  - Cantidad de hectáreas
  - Categoría asignada (Rural cat 01, 02, 03)
  - Valor actual del combustible
- 📄 Generación de liquidaciones detalladas
- 🖨️ Función de impresión optimizada
- ✅ Visualización de historial de pagos
- 💰 Detalle de recibos impagos

## Requisitos Previos

- Python 3.8 o superior
- MySQL/MariaDB con la base de datos `wsur`
- pip (gestor de paquetes de Python)

## Instalación

1. **Clonar o navegar al directorio del proyecto:**
   ```bash
   cd /media/asartorio/disco214/Ale/proyectos_wsf/deuda_servicios_juncal
   ```

2. **Crear un entorno virtual (recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos:**
   - Editar el archivo `app.py` si es necesario cambiar las credenciales:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'dalas.2009',
       'database': 'wsur'
   }
   ```

## Uso

1. **Iniciar el servidor:**
   ```bash
   python app.py
   ```

2. **Acceder a la aplicación:**
   - Abrir el navegador en: http://localhost:5000

3. **Operaciones disponibles:**
   - **Buscar contribuyente:** Escribir apellido o nombre en el buscador
   - **Ver liquidación:** Hacer clic en el contribuyente deseado
   - **Imprimir:** Usar el botón "Imprimir" en la liquidación

## Estructura del Proyecto

```
deuda_servicios_juncal/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Este archivo
├── templates/            # Plantillas HTML
│   ├── index.html       # Página de búsqueda
│   └── liquidacion.html # Página de liquidación
└── static/              # Archivos estáticos
    └── style.css        # Estilos CSS
```

## API Endpoints

### GET `/`
Página principal con búsqueda de contribuyentes

### GET `/api/contribuyentes?q={query}`
Buscar contribuyentes por apellido o nombre
- **Parámetros:** `q` - término de búsqueda
- **Respuesta:** JSON con lista de contribuyentes

### GET `/liquidacion/<id_contribuyente>`
Ver liquidación completa de un contribuyente
- **Parámetros:** `id_contribuyente` - ID del contribuyente
- **Respuesta:** HTML con liquidación detallada

### GET `/api/resumen_deuda/<id_contribuyente>`
Obtener resumen de deuda en formato JSON
- **Parámetros:** `id_contribuyente` - ID del contribuyente
- **Respuesta:** JSON con resumen de deuda

## Cálculo de Deuda

La deuda se calcula según la fórmula:

```
Importe = Hectáreas × Valor_Categoría
```

Donde:
- **Hectáreas:** Campo `Terreno` de `t_contribuyente`
- **Valor_Categoría:** Campo `Valor` de `t_coeficientescontribucioninmuebles`

## Relación de Tablas

```
t_contribuyente
    ↓ (ID_Contribuyente)
t_serviciosxcontribuyente
    ↓ (ID_Servicio → ID_CoeficientesContribucionInmuebles)
t_coeficientescontribucioninmuebles
    (Contiene: Categoría, Valor)
```

## Estados de Recibos

- **1:** Generado (IMPAGO)
- **2:** Impreso (IMPAGO)
- **3:** Pagado
- **4:** Pago anulado (IMPAGO)

## Soporte

Para problemas o consultas sobre el sistema, contactar al administrador del sistema.

## Licencia

© 2026 Municipio de Juncal - Uso interno
