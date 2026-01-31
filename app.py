from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

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

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'dalas.2009',
    'database': 'wsur'
}

def get_db_connection():
    """Crear conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    """Página principal con búsqueda de contribuyentes"""
    return render_template('index.html')

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
    
    # Obtener recibos impagos
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
        ORDER BY r.Periodo
    """
    
    cursor.execute(sql_impagos, (id_contribuyente,))
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
    
    # Calcular totales
    importe_calculado = round(contribuyente['Hectareas'] * contribuyente['ValorActualPorHa'], 2)
    total_deuda = sum(r['ImporteFacturado'] for r in recibos_impagos)
    cantidad_impagos = len(recibos_impagos)
    
    # Generar leyenda certificada con datos del contribuyente
    nombre_completo = f"{contribuyente['Apellido']} {contribuyente['Nombre'] or ''}".strip()
    domicilio = f"{contribuyente['Calle'] or ''} {contribuyente['Numero'] or ''}".strip() or 'N/A'
    partida = contribuyente['Catastro'] or 'N/A'
    hectareas = f"{contribuyente['Hectareas']:.2f}"
    total_deuda_numero = f"{total_deuda:.2f}"
    total_deuda_letras = numero_a_letras(total_deuda)
    categoria = contribuyente['Categoria']
    
    # Generar lista de períodos adeudados
    periodos_detalle = ""
    if recibos_impagos:
        periodos_list = [f"{r['Periodo']} (${r['ImporteFacturado']:.2f})" for r in recibos_impagos]
        periodos_detalle = ", ".join(periodos_list)
    
    leyenda_certificado = f"""La COMUNA DE JUNCAL CERTIFICA QUE EL SR/A.: {nombre_completo}, domiciliado en {domicilio}, actual propietario del inmueble cuya partida inmobiliaria es la siguiente: {partida}, con una extensión de: {hectareas} has, respectivamente, adeuda al día $: {total_deuda_numero}, en concepto de capital e intereses conforme a la Ordenanza Tributaria en vigencia, la suma de {total_deuda_letras}, por la Tasa {categoria}, que corresponde a los períodos que se detallan en el Anexo que junto al presente se acompaña."""
    
    return render_template('liquidacion.html',
                         contribuyente=contribuyente,
                         recibos_impagos=recibos_impagos,
                         recibos_pagados=recibos_pagados,
                         importe_calculado=importe_calculado,
                         total_deuda=total_deuda,
                         cantidad_impagos=cantidad_impagos,
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
