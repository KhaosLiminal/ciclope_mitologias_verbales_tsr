#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TSR_CAPA2_Correciones.py
Corrige genealogías con errores o longitud insuficiente
"""

import json
import os
import requests
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SONAR_API_URL = "https://api.perplexity.ai/chat/completions"
SONAR_MODEL = "sonar-pro"

# Configuración de API
SONAR_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not SONAR_API_KEY:
    raise ValueError("ERROR: PERPLEXITY_API_KEY no está configurada")

HEADERS = {
    "Authorization": f"Bearer {SONAR_API_KEY}",
    "Content-Type": "application/json"
}

# Configuración de reintentos
MAX_ATTEMPTS = 3
INITIAL_DELAY = 5  # segundos
TIMEOUT = 180  # segundos

# Directorios
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "resultados" / "TSR_CAPA2_Genealogias_Batch"
LOG_DIR = BASE_DIR / "logs" / "CAPA2_Correciones"

# Asegurar que existan los directorios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de logging
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"correcciones_{timestamp}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def estimate_tokens(text: str) -> int:
    """Estima el número de tokens en un texto."""
    return len(text.split())  # Aproximación simple: 1 token ≈ 1 palabra

def make_api_call(prompt: str, max_tokens: int = 4000) -> Optional[Dict]:
    """Realiza una llamada a la API de Perplexity."""
    messages = [
        {
            "role": "system",
            "content": "Eres un experto en filosofía, teoría crítica y estudios culturales. Tu tarea es generar análisis genealógicos profundos y bien documentados."
        },
        {"role": "user", "content": prompt}
    ]
    
    data = {
        "model": SONAR_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
    }
    
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.post(
                SONAR_API_URL,
                headers=HEADERS,
                json=data,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            delay = INITIAL_DELAY * (2 ** attempt)
            logger.warning(f"Intento {attempt + 1}/{MAX_ATTEMPTS} fallido: {str(e)}. Reintentando en {delay}s...")
            time.sleep(delay)
    
    return None

def generate_genealogy(tsr_id: str, concept: str, existing_content: str = "") -> Optional[Dict]:
    """Genera una genealogía para un concepto dado."""
    # Plantilla mejorada para asegurar longitud y calidad
    prompt = f"""
    Necesito que generes una genealogía detallada del concepto: "{concept}".
    
    REQUISITOS:
    1. Extensión: Mínimo 600 palabras, máximo 800 palabras.
    2. Estructura en 4 fases claramente diferenciadas:
       - Origen: Contexto histórico y surgimiento del concepto.
       - Desarrollo: Evolución y transformaciones principales.
       - Críticas: Cuestionamientos y debates en torno al concepto.
       - Situación actual: Relevancia contemporánea y perspectivas futuras.
    
    3. Incluye al menos 3-5 referencias académicas clave con citas textuales relevantes.
    4. Profundidad analítica: Ve más allá de lo obvio, mostrando conexiones inesperadas.
    5. Estilo: Académico pero accesible, con un hilo narrativo claro.
    
    Si el siguiente contenido ya existe, úsalo como referencia pero mejóralo significativamente:
    --- CONTENIDO EXISTENTE ---
    {existing_content}
    --- FIN CONTENIDO EXISTENTE ---
    
    Devuelve la respuesta en formato JSON con esta estructura exacta:
    {{
        "titulo": "[TÍTULO ATRACTIVO QUE RESUMA LA GENEALOGÍA]",
        "contenido": "[TEXTO COMPLETO DE LA GENEALOGÍA, 600-800 PALABRAS]",
        "referencias": [
            "[CITA COMPLETA 1]",
            "[CITA COMPLETA 2]"
        ]
    }}
    """
    
    response = make_api_call(prompt)
    if not response or "choices" not in response or not response["choices"]:
        logger.error(f"No se pudo generar respuesta para {tsr_id}")
        return None
    
    try:
        content = response["choices"][0]["message"]["content"]
        # Limpiar el contenido de posibles marcas de código
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Error al procesar la respuesta para {tsr_id}: {str(e)}")
        logger.debug(f"Respuesta cruda: {response}")
        return None

def save_genealogy(tsr_id: str, data: Dict) -> bool:
    """Guarda la genealogía en un archivo Markdown."""
    try:
        output_file = OUTPUT_DIR / f"TSR_{tsr_id}_genealogia.md"
        
        # Formatear el contenido en Markdown
        content = f"# {data['titulo']}\n\n{data['contenido']}\n\n## Referencias\n"
        for ref in data.get('referencias', []):
            content += f"- {ref}\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        word_count = len(data['contenido'].split())
        logger.info(f"Guardado: {output_file.name} ({word_count} palabras)")
        return True
    except Exception as e:
        logger.error(f"Error al guardar {tsr_id}: {str(e)}")
        return False

def get_existing_content(tsr_id: str) -> str:
    """Obtiene el contenido existente de un archivo si existe."""
    file_path = OUTPUT_DIR / f"TSR_{tsr_id}_genealogia.md"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def process_tsr(tsr_id: str, concept: str) -> bool:
    """Procesa un único TSR."""
    logger.info(f"\n{'='*80}")
    logger.info(f"PROCESANDO: {tsr_id} - {concept}")
    logger.info(f"{'='*80}")
    
    existing_content = get_existing_content(tsr_id)
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"Intento {attempt}/{MAX_ATTEMPTS}")
        
        data = generate_genealogy(tsr_id, concept, existing_content)
        if not data:
            logger.warning(f"Intento {attempt} fallido")
            time.sleep(INITIAL_DELAY * attempt)
            continue
        
        word_count = len(data.get('contenido', '').split())
        if word_count < 500:
            logger.warning(f"Contenido demasiado corto: {word_count} palabras")
            time.sleep(INITIAL_DELAY * attempt)
            continue
        
        if save_genealogy(tsr_id, data):
            logger.info(f"{tsr_id}: {word_count} palabras {'(ligeramente por debajo del mínimo)' if word_count < 500 else 'OK'}")
            return True
        
        time.sleep(INITIAL_DELAY * attempt)
    
    logger.error(f"No se pudo generar {tsr_id} después de {MAX_ATTEMPTS} intentos")
    return False

def main():
    # TSRs que necesitan corrección con sus conceptos específicos
    tsrs_to_fix = {
        "106": "Colores como botín teológico - Victoria Finlay",
        "109": "El vacío azul como apropiación inmaterial - Yves Klein",
        "111": "Escritura nacida del inventario - Denise Schmandt-Besserat",
        "115": "Eiségesis: el error que somos - Hans-Georg Gadamer",
        "119": "Leer en voz alta: erotizar la sintaxis - Severo Sarduy",
        "120": "Leer para dejar de ser el mismo - Roger Chartier"
    }
    
    logger.info(f"Iniciando corrección de {len(tsrs_to_fix)} TSRs")
    
    success_count = 0
    for tsr_id, concept in tsrs_to_fix.items():
        if process_tsr(tsr_id, concept):
            success_count += 1
        time.sleep(5)  # Pequeña pausa entre TSRs
    
    logger.info("\n" + "="*50)
    logger.info(f"PROCESO COMPLETADO")
    logger.info("="*50)
    logger.info(f"Éxitos: {success_count}/{len(tsrs_to_fix)}")
    logger.info(f"Log guardado en: {log_file}")
    logger.info("="*50 + "\n")

if __name__ == "__main__":
    main()
