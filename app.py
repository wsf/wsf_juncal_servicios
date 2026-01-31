from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

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
    
    return render_template('liquidacion.html',
                         contribuyente=contribuyente,
                         recibos_impagos=recibos_impagos,
                         recibos_pagados=recibos_pagados,
                         importe_calculado=importe_calculado,
                         total_deuda=total_deuda,
                         cantidad_impagos=cantidad_impagos,
                         fecha_emision=datetime.now().strftime('%d/%m/%Y'))

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
