# Configuración de Groq para Consultas con IA

## ¿Qué es Groq?

Groq es un servicio de IA que proporciona acceso gratuito a modelos de lenguaje de alta velocidad como Llama 3.

## Cómo obtener tu API Key de Groq (GRATIS)

1. **Ve al sitio de Groq Console:**
   - Abre tu navegador y ve a: https://console.groq.com/

2. **Crea una cuenta:**
   - Haz clic en "Sign Up" o "Get Started"
   - Puedes registrarte con Google, GitHub o email
   - Completa el proceso de registro

3. **Genera tu API Key:**
   - Una vez dentro del dashboard, busca la sección "API Keys"
   - Haz clic en "Create API Key"
   - Dale un nombre descriptivo (ej: "Comuna Juncal")
   - Copia la API key generada (¡guárdala en lugar seguro!)

4. **Configura en el proyecto:**
   - Abre el archivo `.env` en la raíz del proyecto
   - Busca la línea: `GROQ_API_KEY=tu_api_key_aqui`
   - Reemplaza `tu_api_key_aqui` con tu API key real
   - Ejemplo: `GROQ_API_KEY=gsk_1234567890abcdef...`

5. **Reinicia la aplicación:**
   - Detén Flask (Ctrl+C)
   - Vuelve a ejecutar: `python app.py`

## Características del plan gratuito

✅ **Completamente GRATIS**
✅ Límite generoso: 30 solicitudes por minuto
✅ Acceso a modelos rápidos como Llama 3.3 70B
✅ Sin tarjeta de crédito requerida

## Modelos disponibles

El sistema usa por defecto: **llama-3.3-70b-versatile**
- Rápido y eficiente
- Excelente para consultas en español
- Respuestas precisas sobre datos estructurados

## Ejemplos de uso

Una vez configurado, puedes hacer preguntas como:
- "¿Cuántos contribuyentes tienen deuda?"
- "¿Quién tiene la mayor deuda?"
- "Dame información sobre Juan Pérez"
- "Lista los top 5 contribuyentes por deuda"
- "¿Cuál es el promedio de hectáreas?"

## Solución de problemas

**Error: "API key not found"**
- Verifica que el archivo `.env` existe
- Asegúrate de que la línea `GROQ_API_KEY` está correctamente configurada
- Reinicia la aplicación Flask

**Error: "Rate limit exceeded"**
- Estás haciendo demasiadas solicitudes por minuto
- Espera unos segundos e intenta nuevamente

**Error de conexión**
- Verifica tu conexión a internet
- Groq requiere acceso a internet para funcionar

## Seguridad

⚠️ **IMPORTANTE:**
- Nunca compartas tu API key públicamente
- No la subas a GitHub (está en `.gitignore`)
- Cada desarrollador debe tener su propia API key

## Enlaces útiles

- Console de Groq: https://console.groq.com/
- Documentación: https://console.groq.com/docs
- Límites y precios: https://wow.groq.com/
