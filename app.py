from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
# from groq import Groq  # Comentado temporalmente por problemas de compatibilidad en Windows

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configurar cliente de Groq
# groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))  # Comentado temporalmente

# Configuración de valores predeterminados desde .env
VALOR_LITRO_DEFAULT = float(os.getenv('VALOR_LITRO', '1500'))
LITROS_CAT01_DEFAULT = float(os.getenv('LITROS_CAT01', '1.375'))
LITROS_CAT02_DEFAULT = float(os.getenv('LITROS_CAT02', '1.625'))
LITROS_CAT03_DEFAULT = float(os.getenv('LITROS_CAT03', '1.625'))
MES_DESDE_DEFAULT = os.getenv('MES_DESDE', '01')
ANIO_DESDE_DEFAULT = os.getenv('ANIO_DESDE', '2024')

def formato_moneda(valor):
    """Formatear número a formato monetario con separador de miles"""
    if valor is None:
        return "0,00"
    # Formatear con punto para miles y coma para decimales (formato argentino)
    return "{:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

def formato_periodo(fecha):
    """Formatear fecha a formato MM/YYYY"""
    if fecha is None:
        return ""
    # Si es string, convertir a datetime
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
        except:
            return fecha
    # Formatear como MM/YYYY
    return fecha.strftime('%m/%Y')

def formato_fecha(fecha):
    """Formatear fecha a formato DD/MM/YY"""
    if fecha is None:
        return ""
    # Si es string, convertir a datetime
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
        except:
            return fecha
    # Formatear como DD/MM/YY
    return fecha.strftime('%d/%m/%y')

# Registrar los filtros personalizados
app.jinja_env.filters['moneda'] = formato_moneda
app.jinja_env.filters['periodo'] = formato_periodo
app.jinja_env.filters['fecha'] = formato_fecha

def numero_a_letras(numero):
    """Convertir número decimal a texto en español"""
    unidades = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
    decenas = ['', '', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
    especiales = {10: 'DIEZ', 11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE', 15: 'QUINCE', 
                  16: 'DIECISEIS', 17: 'DIECISIETE', 18: 'DIECIOCHO', 19: 'DIECINUEVE'}
    centenas = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 
                'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS']
    
    if numero == 0:
        return 'CERO PESOS'
    
    # Separar parte entera y decimal
    partes = f"{numero:.2f}".split('.')
    entero = int(partes[0])
    centavos = int(partes[1])
    
    def convertir_hasta_999(n):
        if n == 0:
            return ''
        elif n < 10:
            return unidades[n]
        elif 10 <= n < 20:
            return especiales[n]
        elif 20 <= n < 100:
            dec = n // 10
            uni = n % 10
            if uni == 0:
                return decenas[dec]
            elif dec == 2:
                return f"VEINTI{unidades[uni]}"
            else:
                return f"{decenas[dec]} Y {unidades[uni]}"
        else:
            cen = n // 100
            resto = n % 100
            if n == 100:
                return 'CIEN'
            elif resto == 0:
                return centenas[cen]
            else:
                return f"{centenas[cen]} {convertir_hasta_999(resto)}"
    
    def convertir_miles(n):
        if n < 1000:
            return convertir_hasta_999(n)
        
        miles = n // 1000
        resto = n % 1000
        
        if miles == 1:
            texto_miles = 'MIL'
        else:
            texto_miles = f"{convertir_hasta_999(miles)} MIL"
        
        if resto == 0:
            return texto_miles
        else:
            return f"{texto_miles} {convertir_hasta_999(resto)}"
    
    # Convertir millones
    if entero >= 1000000:
        millones = entero // 1000000
        resto = entero % 1000000
        
        if millones == 1:
            texto = 'UN MILLON'
        else:
            texto = f"{convertir_hasta_999(millones)} MILLONES"
        
        if resto > 0:
            texto += f" {convertir_miles(resto)}"
    else:
        texto = convertir_miles(entero)
    
    if centavos > 0:
        return f"{texto} CON {centavos}/100 PESOS"
    else:
        return f"{texto} PESOS"

# Configuración de la base de datos desde variables de entorno
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'wsur')
}

def get_db_connection():
    """Crear conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    """Página principal con búsqueda de contribuyentes"""
    return render_template('index.html',
                         valor_litro_default=VALOR_LITRO_DEFAULT,
                         litros_cat01_default=LITROS_CAT01_DEFAULT,
                         litros_cat02_default=LITROS_CAT02_DEFAULT,
                         litros_cat03_default=LITROS_CAT03_DEFAULT,
                         mes_desde_default=MES_DESDE_DEFAULT,
                         anio_desde_default=ANIO_DESDE_DEFAULT)

@app.route('/api/contribuyentes')
def buscar_contribuyentes():
    """API para buscar contribuyentes por apellido"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = """
        SELECT 
            c.ID_contribuyente,
            p.Apellido,
            p.Nombre,
            c.Terreno,
            coef.Descripcion as Categoria,
            coef.Valor as ValorCategoria
        FROM t_contribuyente c
        INNER JOIN t_personas p ON c.ID_persona = p.ID_Persona
        INNER JOIN t_serviciosxcontribuyente s ON c.ID_contribuyente = s.ID_Contribuyente
        INNER JOIN t_coeficientescontribucioninmuebles coef 
            ON s.ID_Servicio = coef.ID_CoeficientesContribucionInmuebles
        WHERE (p.Apellido LIKE %s OR p.Nombre LIKE %s)
            AND coef.Descripcion LIKE '%Rural%'
            AND c.Terreno > 0
        ORDER BY p.Apellido, p.Nombre
        LIMIT 20
    """
    
    search_term = f'%{query}%'
    cursor.execute(sql, (search_term, search_term))
    contribuyentes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(contribuyentes)

@app.route('/liquidacion/<int:id_contribuyente>')
def liquidacion(id_contribuyente):
    """Mostrar liquidación completa de un contribuyente"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener datos del contribuyente
    sql_datos = """
        SELECT 
            p.Apellido,
            p.Nombre,
            c.ID_contribuyente,
            c.Terreno as Hectareas,
            c.Catastro,
            c.Calle,
            c.Numero,
            coef.Descripcion as Categoria,
            coef.Valor as ValorActualPorHa
        FROM t_contribuyente c
        INNER JOIN t_personas p ON c.ID_persona = p.ID_Persona
        INNER JOIN t_serviciosxcontribuyente s ON c.ID_contribuyente = s.ID_Contribuyente
        INNER JOIN t_coeficientescontribucioninmuebles coef 
            ON s.ID_Servicio = coef.ID_CoeficientesContribucionInmuebles
        WHERE c.ID_contribuyente = %s
            AND coef.Descripcion LIKE '%Rural%'
        LIMIT 1
    """
    
    cursor.execute(sql_datos, (id_contribuyente,))
    contribuyente = cursor.fetchone()
    
    if not contribuyente:
        cursor.close()
        conn.close()
        return "Contribuyente no encontrado", 404
    
    # Obtener parámetros desde la URL (con valores por defecto del .env)
    valor_litro = float(request.args.get('valor_litro', VALOR_LITRO_DEFAULT))
    mes_desde = request.args.get('mes_desde', MES_DESDE_DEFAULT)
    anio_desde = request.args.get('anio_desde', ANIO_DESDE_DEFAULT)
    fecha_desde = f"{anio_desde}-{mes_desde}-01"
    
    litros_cat01 = float(request.args.get('litros_cat01', LITROS_CAT01_DEFAULT))
    litros_cat02 = float(request.args.get('litros_cat02', LITROS_CAT02_DEFAULT))
    litros_cat03 = float(request.args.get('litros_cat03', LITROS_CAT03_DEFAULT))
    
    # Obtener recibos impagos (filtrados por fecha)
    sql_impagos = """
        SELECT 
            r.NroRecibo,
            DATE_FORMAT(r.Periodo, '%Y-%m-%d') as Periodo,
            r.FechaGeneracion,
            r.ImporteTotal1 as ImporteFacturado,
            er.Descripcion as Estado,
            r.FechaVencimiento1 as FechaVencimiento
        FROM t_recibos r
        INNER JOIN t_estadorecibo er ON r.ID_EstadoRecibo = er.ID_EstadoRecibo
        WHERE r.ID_Contribuyente = %s
            AND r.ID_EstadoRecibo IN (1, 2, 4)
            AND r.Periodo >= %s
        ORDER BY r.Periodo
    """
    
    cursor.execute(sql_impagos, (id_contribuyente, fecha_desde))
    recibos_impagos = cursor.fetchall()
    
    # Obtener recibos pagados (más de los últimos 5 para dar mejor visibilidad)
    sql_pagados = """
        SELECT 
            r.NroRecibo,
            DATE_FORMAT(r.Periodo, '%Y-%m-%d') as Periodo,
            r.FechaGeneracion,
            r.ImporteTotal1 as ImporteFacturado,
            r.FechaPago,
            er.Descripcion as Estado
        FROM t_recibos r
        INNER JOIN t_estadorecibo er ON r.ID_EstadoRecibo = er.ID_EstadoRecibo
        WHERE r.ID_Contribuyente = %s
            AND r.ID_EstadoRecibo = 3
        ORDER BY r.Periodo DESC
        LIMIT 20
    """
    
    cursor.execute(sql_pagados, (id_contribuyente,))
    recibos_pagados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Calcular litros por cuota según categoría (ya obtuvimos los valores arriba del .env)
    categoria = contribuyente['Categoria']
    hectareas_valor = float(contribuyente['Hectareas'] or 0)
    
    # Definir litros por hectárea según categoría (usando valores configurables)
    if 'cat 01' in categoria:
        litros_por_ha = litros_cat01
    elif 'cat 02' in categoria:
        litros_por_ha = litros_cat02
    elif 'Cat 3' in categoria:
        litros_por_ha = litros_cat03
    else:
        litros_por_ha = 0
    
    litros_por_cuota = hectareas_valor * litros_por_ha
    total_litros = litros_por_cuota * len(recibos_impagos)
    
    # Calcular total en pesos (ya obtuvimos valor_litro arriba del .env)
    total_pesos = total_litros * valor_litro
    
    # Calcular totales
    importe_calculado = round(contribuyente['Hectareas'] * contribuyente['ValorActualPorHa'], 2)
    total_deuda = sum(r['ImporteFacturado'] for r in recibos_impagos)
    cantidad_impagos = len(recibos_impagos)
    
    # Generar leyenda certificada con datos del contribuyente
    nombre_completo = f"{contribuyente['Apellido']} {contribuyente['Nombre'] or ''}".strip()
    domicilio = f"{contribuyente['Calle'] or ''} {contribuyente['Numero'] or ''}".strip() or 'N/A'
    partida = contribuyente['Catastro'] or 'N/A'
    hectareas = f"{contribuyente['Hectareas']:.2f}"
    total_litros_str = f"{total_litros:.2f}"
    total_pesos_str = f"{total_pesos:.2f}"
    total_pesos_letras = numero_a_letras(total_pesos)
    categoria = contribuyente['Categoria']
    
    # Generar lista de períodos adeudados
    periodos_detalle = ""
    if recibos_impagos:
        periodos_list = [f"{r['Periodo']} ({litros_por_cuota:.2f} Lts)" for r in recibos_impagos]
        periodos_detalle = ", ".join(periodos_list)
    
    leyenda_certificado = f"""La COMUNA DE JUNCAL CERTIFICA QUE EL SR/A.: {nombre_completo}, domiciliado en {domicilio}, actual propietario del inmueble cuya partida inmobiliaria es la siguiente: {partida}, con una extensión de: {hectareas} has, respectivamente, adeuda al día {total_litros_str} litros de combustible equivalentes a $: {total_pesos_str}, en concepto de capital e intereses conforme a la Ordenanza Tributaria en vigencia, la suma de {total_pesos_letras}, por la Tasa {categoria}, que corresponde a los períodos que se detallan en el Anexo que junto al presente se acompaña."""
    
    return render_template('liquidacion.html',
                         contribuyente=contribuyente,
                         recibos_impagos=recibos_impagos,
                         recibos_pagados=recibos_pagados,
                         importe_calculado=importe_calculado,
                         total_deuda=total_deuda,
                         cantidad_impagos=cantidad_impagos,
                         litros_por_cuota=litros_por_cuota,
                         litros_por_ha=litros_por_ha,
                         total_litros=total_litros,
                         valor_litro=valor_litro,
                         total_pesos=total_pesos,
                         mes_desde=mes_desde,
                         anio_desde=anio_desde,
                         fecha_emision=datetime.now().strftime('%d/%m/%Y'),
                         leyenda_certificado=leyenda_certificado,
                         periodos_detalle=periodos_detalle)

@app.route('/api/resumen_deuda/<int:id_contribuyente>')
def resumen_deuda(id_contribuyente):
    """API para obtener resumen de deuda en JSON"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    sql = """
        SELECT 
            p.Apellido,
            p.Nombre,
            c.Terreno as Hectareas,
            coef.Descripcion as Categoria,
            coef.Valor as ValorActualPorHa,
            ROUND(c.Terreno * coef.Valor, 2) as ImportePorPeriodo,
            COUNT(r.NroRecibo) as CantidadRecibosImpagos,
            SUM(r.ImporteTotal1) as TotalDeuda
        FROM t_contribuyente c
        INNER JOIN t_personas p ON c.ID_persona = p.ID_Persona
        INNER JOIN t_serviciosxcontribuyente s ON c.ID_contribuyente = s.ID_Contribuyente
        INNER JOIN t_coeficientescontribucioninmuebles coef 
            ON s.ID_Servicio = coef.ID_CoeficientesContribucionInmuebles
        LEFT JOIN t_recibos r ON c.ID_contribuyente = r.ID_Contribuyente
            AND r.ID_EstadoRecibo IN (1, 2, 4)
        WHERE c.ID_contribuyente = %s
            AND coef.Descripcion LIKE '%Rural%'
        GROUP BY p.Apellido, p.Nombre, c.Terreno, coef.Descripcion, coef.Valor
    """
    
    cursor.execute(sql, (id_contribuyente,))
    resumen = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if resumen:
        return jsonify(resumen)
    else:
        return jsonify({"error": "Contribuyente no encontrado"}), 404

@app.route('/api/kpi_rurales')
def kpi_rurales():
    """Obtener KPIs de contribuyentes rurales"""
    try:
        # Obtener parámetros de configuración (con valores por defecto del .env)
        mes_desde = request.args.get('mes_desde', MES_DESDE_DEFAULT)
        anio_desde = request.args.get('anio_desde', ANIO_DESDE_DEFAULT)
        fecha_desde = f"{anio_desde}-{mes_desde}-01"
        
        litros_cat01 = float(request.args.get('litros_cat01', LITROS_CAT01_DEFAULT))
        litros_cat02 = float(request.args.get('litros_cat02', LITROS_CAT02_DEFAULT))
        litros_cat03 = float(request.args.get('litros_cat03', LITROS_CAT03_DEFAULT))
        valor_litro = float(request.args.get('valor_litro', VALOR_LITRO_DEFAULT))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # KPI: Contribuyentes en mora con cálculo de litros
        sql_mora = """
        SELECT 
            c.ID_contribuyente,
            c.Terreno,
            coef.Descripcion as categoria,
            COUNT(DISTINCT r.NroRecibo) as cuotas_deudadas
        FROM t_contribuyente c
        INNER JOIN t_serviciosxcontribuyente sc ON c.ID_contribuyente = sc.ID_Contribuyente
        INNER JOIN t_coeficientescontribucioninmuebles coef 
            ON sc.ID_Servicio = coef.ID_CoeficientesContribucionInmuebles
        INNER JOIN t_recibos r ON c.ID_contribuyente = r.ID_Contribuyente
            AND r.ID_EstadoRecibo IN (1, 2, 4)
            AND r.Periodo >= %s
        WHERE coef.Descripcion LIKE '%Rural%'
        GROUP BY c.ID_contribuyente, c.Terreno, coef.Descripcion
        HAVING cuotas_deudadas > 0
        """
        
        cursor.execute(sql_mora, (fecha_desde,))
        resultado_mora = cursor.fetchall()
        
        # Calcular litros totales según categoría
        total_litros = 0
        for r in resultado_mora:
            categoria = r['categoria']
            hectareas = float(r['Terreno'] or 0)
            cuotas = int(r['cuotas_deudadas'] or 0)
            
            # Determinar litros por hectárea según categoría
            if 'cat 01' in categoria:
                litros_por_ha = litros_cat01
            elif 'cat 02' in categoria:
                litros_por_ha = litros_cat02
            elif 'Cat 3' in categoria:
                litros_por_ha = litros_cat03
            else:
                litros_por_ha = 0
            
            litros_contribuyente = hectareas * litros_por_ha * cuotas
            total_litros += litros_contribuyente
        
        contribuyentes_en_mora = len(resultado_mora)
        total_pesos = total_litros * valor_litro
        
        # KPI: Total de contribuyentes rurales
        sql_total = """
        SELECT COUNT(DISTINCT c.ID_contribuyente) as total_contribuyentes
        FROM t_contribuyente c
        INNER JOIN t_serviciosxcontribuyente sc ON c.ID_contribuyente = sc.ID_Contribuyente
        INNER JOIN t_coeficientescontribucioninmuebles coef 
            ON sc.ID_Servicio = coef.ID_CoeficientesContribucionInmuebles
        WHERE coef.Descripcion LIKE '%Rural%'
        """
        
        cursor.execute(sql_total)
        resultado_total = cursor.fetchone()
        total_contribuyentes = resultado_total['total_contribuyentes']
        
        # Calcular contribuyentes sin mora
        contribuyentes_sin_mora = total_contribuyentes - contribuyentes_en_mora
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'litros_adeudados': round(total_litros, 2),
            'total_pesos': round(total_pesos, 2),
            'contribuyentes_en_mora': contribuyentes_en_mora,
            'contribuyentes_sin_mora': contribuyentes_sin_mora,
            'total_contribuyentes': total_contribuyentes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/listado_deuda_rural')
def listado_deuda_rural():
    """Mostrar listado completo de deudas de todos los contribuyentes rurales"""
    try:
        # Obtener parámetros de fecha desde la URL (con valores por defecto del .env)
        mes_desde = request.args.get('mes_desde', MES_DESDE_DEFAULT)
        anio_desde = request.args.get('anio_desde', ANIO_DESDE_DEFAULT)
        fecha_desde = f"{anio_desde}-{mes_desde}-01"
        
        # Obtener parámetros de litros por categoría (con valores por defecto del .env)
        litros_cat01 = float(request.args.get('litros_cat01', LITROS_CAT01_DEFAULT))
        litros_cat02 = float(request.args.get('litros_cat02', LITROS_CAT02_DEFAULT))
        litros_cat03 = float(request.args.get('litros_cat03', LITROS_CAT03_DEFAULT))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Consulta para obtener todos los contribuyentes rurales con sus deudas (filtrados por fecha)
        sql = """
        SELECT 
            c.ID_contribuyente,
            CONCAT(p.Apellido, ', ', p.Nombre) as nombre_completo,
            c.Terreno as hectareas,
            coef.Descripcion as categoria,
            coef.Valor as valor_categoria,
            COUNT(DISTINCT r.NroRecibo) as cuotas_deudadas
        FROM t_contribuyente c
        INNER JOIN t_personas p ON c.ID_persona = p.ID_Persona
        INNER JOIN t_serviciosxcontribuyente sc ON c.ID_contribuyente = sc.ID_Contribuyente
        INNER JOIN t_coeficientescontribucioninmuebles coef 
            ON sc.ID_Servicio = coef.ID_CoeficientesContribucionInmuebles
        LEFT JOIN t_recibos r ON c.ID_contribuyente = r.ID_Contribuyente
            AND r.ID_EstadoRecibo IN (1, 2, 4)
            AND r.Periodo >= %s
        WHERE coef.Descripcion LIKE '%Rural%'
        GROUP BY c.ID_contribuyente, p.Apellido, p.Nombre, c.Terreno, coef.Descripcion, coef.Valor
        HAVING cuotas_deudadas > 0
        ORDER BY p.Apellido, p.Nombre
        """
        
        cursor.execute(sql, (fecha_desde,))
        contribuyentes = cursor.fetchall()
        
        # Calcular litros por cuota según categoría (ya obtuvimos los valores arriba del .env)
        for c in contribuyentes:
            categoria = c['categoria']
            hectareas = float(c['hectareas'] or 0)
            
            # Definir litros por hectárea según categoría (usando valores configurables)
            if 'cat 01' in categoria:
                litros_por_ha = litros_cat01
            elif 'cat 02' in categoria:
                litros_por_ha = litros_cat02
            elif 'Cat 3' in categoria:
                litros_por_ha = litros_cat03
            else:
                litros_por_ha = 0
            
            c['litros_por_cuota'] = hectareas * litros_por_ha
            c['litros_totales'] = c['litros_por_cuota'] * int(c['cuotas_deudadas'] or 0)
        
        # Calcular totales manejando valores None
        total_hectareas = sum(float(c['hectareas'] or 0) for c in contribuyentes)
        total_cuotas = sum(int(c['cuotas_deudadas'] or 0) for c in contribuyentes)
        total_litros = sum(float(c['litros_totales'] or 0) for c in contribuyentes)
        
        cursor.close()
        conn.close()
        
        return render_template('listado_deuda_rural.html', 
                             contribuyentes=contribuyentes,
                             total_hectareas=total_hectareas,
                             total_cuotas=total_cuotas,
                             total_litros=total_litros,
                             mes_desde=mes_desde,
                             anio_desde=anio_desde,
                             fecha_generacion=datetime.now(),
                             valor_litro_default=VALOR_LITRO_DEFAULT,
                             litros_cat01_default=LITROS_CAT01_DEFAULT,
                             litros_cat02_default=LITROS_CAT02_DEFAULT,
                             litros_cat03_default=LITROS_CAT03_DEFAULT,
                             mes_desde_default=MES_DESDE_DEFAULT,
                             anio_desde_default=ANIO_DESDE_DEFAULT)
    except Exception as e:
        return f"Error al generar listado: {str(e)}", 500

# FUNCIONALIDAD DE IA COMENTADA TEMPORALMENTE POR PROBLEMAS DE COMPATIBILIDAD EN WINDOWS
# Para habilitarla, descomentar estas rutas y la importación de Groq al inicio del archivo

# @app.route('/consultas_llm')
# def consultas_llm():
#     """Página de consultas con LLM"""
#     return render_template('consultas_llm.html')

# @app.route('/api/consultar_llm', methods=['POST'])
# def consultar_llm():
#     """Procesar consulta con LLM usando Groq"""
#     try:
#         data = request.get_json()
#         pregunta = data.get('pregunta', '')
#         
#         if not pregunta:
#             return jsonify({"error": "No se proporcionó pregunta"}), 400
#         
#         # Obtener contexto de la base de datos
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         
#         # Obtener resumen de contribuyentes rurales
#         sql_contexto = """
#         SELECT 
#             c.ID_contribuyente,
#             CONCAT(p.Apellido, ', ', p.Nombre) as nombre_completo,
#             c.Terreno as hectareas,
#             coef.Descripcion as categoria,
#             coef.Valor as valor_categoria,
#             COUNT(DISTINCT r.NroRecibo) as cuotas_deudadas,
#             (COUNT(DISTINCT r.NroRecibo) * c.Terreno * coef.Valor) as deuda_total
#         FROM t_contribuyente c
#         INNER JOIN t_personas p ON c.ID_persona = p.ID_Persona
#         INNER JOIN t_serviciosxcontribuyente sc ON c.ID_contribuyente = sc.ID_Contribuyente
#         INNER JOIN t_coeficientescontribucioninmuebles coef 
#             ON sc.ID_Servicio = coef.ID_CoeficientesContribucionInmuebles
#         LEFT JOIN t_recibos r ON c.ID_contribuyente = r.ID_Contribuyente
#             AND r.ID_EstadoRecibo IN (1, 2, 4)
#         WHERE coef.Descripcion LIKE '%Rural%'
#         GROUP BY c.ID_contribuyente, p.Apellido, p.Nombre, c.Terreno, coef.Descripcion, coef.Valor
#         ORDER BY p.Apellido, p.Nombre
#         LIMIT 100
#         """
#         
#         cursor.execute(sql_contexto)
#         contribuyentes = cursor.fetchall()
#         
#         cursor.close()
#         conn.close()
#         
#         # Preparar contexto para el LLM
#         contexto = "Información de contribuyentes rurales de la Comuna de Juncal:\n\n"
#         for c in contribuyentes:
#             contexto += f"- {c['nombre_completo']}: {c['hectareas']} hectáreas, Categoría {c['categoria']}, "
#             contexto += f"Cuotas adeudadas: {c['cuotas_deudadas']}, Deuda total: ${c['deuda_total']:,.2f}\n"
#         
#         # Llamar a Groq
#         chat_completion = groq_client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "system",
#                     "content": f"""Eres un asistente experto en analizar información de contribuyentes rurales de la Comuna de Juncal. 
#                     
# Contexto de datos disponibles:
# {contexto}
# 
# Responde de forma clara, concisa y profesional. Si te preguntan por un contribuyente específico, busca en los datos proporcionados.
# Si necesitas hacer cálculos, hazlos basándote en los datos. Usa formato argentino para montos ($1.234,56).
# Si no tienes la información exacta, indica que necesitas más detalles."""
#                 },
#                 {
#                     "role": "user",
#                     "content": pregunta
#                 }
#             ],
#             model="llama-3.3-70b-versatile",
#             temperature=0.3,
#             max_tokens=1024,
#         )
#         
#         respuesta = chat_completion.choices[0].message.content
#         
#         return jsonify({
#             "respuesta": respuesta,
#             "tokens_usados": chat_completion.usage.total_tokens
#         })
#         
#     except Exception as e:
#         return jsonify({"error": f"Error al procesar consulta: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
