#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TSR_CAPA2_Genealogias_Batch.py
Genera genealogías en lotes más pequeños para asegurar calidad
"""

import json
import requests
import time
import logging
import os
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SONAR_API_URL = "https://api.perplexity.ai/chat/completions"
SONAR_MODEL = "sonar-pro"

# Headers de API
SONAR_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not SONAR_API_KEY:
    raise ValueError("ERROR: PERPLEXITY_API_KEY no está configurada")

HEADERS = {
    "Authorization": f"Bearer {SONAR_API_KEY}",
    "Content-Type": "application/json"
}

# Configuración de lotes
BATCH_SIZE = 5  # 5 genealogías por llamada para asegurar calidad
MAX_ATTEMPTS = 3
INITIAL_DELAY = 5
TIMEOUT = 180

# Logging
LOG_DIR = Path("logs/CAPA2_Batch")
LOG_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"CAPA2_batch_{TIMESTAMP}.log"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# UTILIDADES
# ============================================================================

def estimate_tokens(text: str) -> int:
    """Estimate token count for a given text."""
    return math.ceil(len(text) / 3)

def load_metadata() -> List[Dict]:
    """Carga metadatos de TSRs desde archivo JSON."""
    metadata_file = Path("../resultados/TSR_CAPA1_FINAL.json")
    
    if not metadata_file.exists():
        logger.error(f"ERROR: No se encuentra {metadata_file}")
        return []
    
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        tsrs = []
        if 'clusters' in datos:
            for cluster in datos['clusters'].values():
                tsrs.extend(cluster)
        elif 'resultados' in datos:
            tsrs = datos['resultados']
        elif isinstance(datos, list):
            tsrs = datos
        
        # Filtrar solo TSRs 102-120
        metadata = []
        for tsr in tsrs:
            num = tsr.get('tsr', tsr.get('numero', 0))
            try:
                num = int(num)
            except (ValueError, TypeError):
                continue
                
            if 102 <= num <= 120:
                metadata.append({
                    "numero": num,
                    "concepto_central": tsr.get('titulo', f'TSR {num}'),
                    "cluster": tsr.get('cluster', 'Sin cluster')
                })
        
        metadata.sort(key=lambda x: x['numero'])
        logger.info(f"OK: {len(metadata)} TSRs cargados (102-120)")
        return metadata
        
    except Exception as e:
        logger.error(f"ERROR cargando metadatos: {str(e)}")
        return []

def generate_batch_prompt(batch_metadata: List[Dict]) -> str:
    """Genera prompt para un lote de genealogías."""
    prompt = f"""
TAREA CRÍTICA: Genealogías de {len(batch_metadata)} conceptos filosóficos (500-700 palabras c/u)
=============================================================================

Formato requerido: JSON estructurado con esta forma EXACTA:

{{
  "genealogias": [
    {{
      "tsr": {batch_metadata[0]['numero']},
      "concepto": "{batch_metadata[0]['concepto_central']}",
      "genealogia": "[500-700 palabras aquí]"
    }},
    ...
  ]
}}

REQUISITOS CRÍTICOS:
  ✓ Total: {len(batch_metadata)} genealogías
  ✓ Rango: 500-700 palabras POR GENEALOGÍA
  ✓ Estructura: 4 fases (origen, autor, crítica, presente)
  ✓ JSON válido (sin markdown)
  ✓ Responde SOLO JSON

CONCEPTOS A PROCESAR:
"""
    
    for i, tsr in enumerate(batch_metadata, 1):
        prompt += f"\n{i}. TSR#{tsr['numero']}: {tsr['concepto_central']}"
    
    prompt += "\n\n¿LISTO? Devuelve las genealogías en JSON puro."
    
    return prompt

def call_sonar_with_retries(prompt: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Llama Sonar API con reintentos."""
    estimated_input_tokens = estimate_tokens(prompt)
    max_output_tokens = 8000  # Reducido para mayor calidad
    max_tokens = min(max_output_tokens, 128000 - estimated_input_tokens - 1000)
    
    logger.info(f"  Tokens input: {estimated_input_tokens}, output: {max_tokens}")
    
    payload = {
        "model": SONAR_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "search_mode": "academic",
        "web_search_options": {"search_context_size": "high"},
        "search_language_filter": ["es", "en", "fr", "de"],
        "stream": False
    }
    
    metadata_respuesta = {"intent": 0, "citations": [], "search_results": []}
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            logger.info(f"INTENTO {attempt}/{MAX_ATTEMPTS}")
            
            response = requests.post(SONAR_API_URL, headers=HEADERS, json=payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                response_json = response.json()
                
                if "choices" not in response_json or not response_json["choices"]:
                    logger.error("ERROR: Estructura de respuesta inválida")
                    return None, metadata_respuesta
                    
                genealogias_text = response_json["choices"][0]["message"]["content"]
                citations = response_json.get("citations", [])
                search_results = response_json.get("search_results", [])
                
                metadata_respuesta["citations"] = citations
                metadata_respuesta["search_results"] = search_results
                metadata_respuesta["intent"] = attempt
                
                logger.info(f"OK: {len(genealogias_text)} caracteres, {len(citations)} citations")
                return genealogias_text, metadata_respuesta
                
            else:
                logger.error(f"ERROR HTTP {response.status_code}")
                return None, metadata_respuesta
                
        except Exception as e:
            logger.error(f"ERROR en intento {attempt}: {str(e)}")
            if attempt == MAX_ATTEMPTS:
                return None, metadata_respuesta
            time.sleep(INITIAL_DELAY * (2 ** (attempt - 1)))
    
    return None, metadata_respuesta

def clean_json_response(text: str) -> str:
    """Limpia respuesta JSON si viene envuelta en bloques markdown."""
    text = text.strip()
    
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    
    return text.strip()

def process_batch(batch_text: str, batch_num: int) -> List[Dict]:
    """Procesa un lote de genealogías."""
    try:
        batch_text_clean = clean_json_response(batch_text)
        batch_data = json.loads(batch_text_clean)
        genealogias = batch_data.get("genealogias", [])
        
        logger.info(f"Lote {batch_num}: {len(genealogias)} genealogías procesadas")
        
        # Validar palabras
        for gen in genealogias:
            palabras = len(gen.get("genealogia", "").split())
            if palabras < 500:
                logger.warning(f"TSR{gen.get('tsr', '?')}: {palabras} palabras (menos de 500)")
            elif palabras > 700:
                logger.warning(f"TSR{gen.get('tsr', '?')}: {palabras} palabras (más de 700)")
            else:
                logger.info(f"TSR{gen.get('tsr', '?')}: {palabras} palabras OK")
        
        return genealogias
        
    except Exception as e:
        logger.error(f"ERROR procesando lote {batch_num}: {str(e)}")
        return []

def save_results(all_genealogias: List[Dict]) -> None:
    """Guarda todas las genealogías en archivos individuales."""
    results_dir = Path("resultados/TSR_CAPA2_Genealogias_Batch")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Guardando {len(all_genealogias)} genealogías...")
    
    for gen in all_genealogias:
        try:
            tsr = gen.get("tsr")
            concepto = gen.get("concepto", "Unknown")
            genealogia = gen.get("genealogia", "")
            
            filename = results_dir / f"TSR_{tsr:03d}_genealogia.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# TSR {tsr}: {concepto}\n\n")
                f.write(genealogia)
            
            logger.info(f"Guardado: TSR{tsr:03d}")
            
        except Exception as e:
            logger.error(f"ERROR guardando TSR{gen.get('tsr', '?')}: {str(e)}")

# ============================================================================
# MAIN
# ============================================================================

def main() -> bool:
    """Orquesta el procesamiento por lotes."""
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("INICIANDO GENERACIÓN DE GENEALOGÍAS (MODO BATCH)")
    logger.info("=" * 80)
    
    # Cargar metadatos
    metadata = load_metadata()
    if len(metadata) != 19:
        logger.error("ERROR: Se requieren exactamente 19 TSRs (102-120)")
        return False
    
    # Dividir en lotes
    batches = [metadata[i:i + BATCH_SIZE] for i in range(0, len(metadata), BATCH_SIZE)]
    logger.info(f"Procesando {len(batches)} lotes de {BATCH_SIZE} genealogías cada uno")
    
    all_genealogias = []
    successful_batches = 0
    
    # Procesar cada lote
    for i, batch in enumerate(batches, 1):
        logger.info(f"\nLOTE {i}/{len(batches)}: TSRs {batch[0]['numero']}-{batch[-1]['numero']}")
        
        # Generar prompt para el lote
        prompt = generate_batch_prompt(batch)
        
        # Llamar a API
        batch_text, metadata_resp = call_sonar_with_retries(prompt)
        
        if batch_text:
            # Procesar lote
            genealogias = process_batch(batch_text, i)
            all_genealogias.extend(genealogias)
            successful_batches += 1
            
            logger.info(f"Lote {i} completado: {len(genealogias)} genealogías")
        else:
            logger.error(f"Lote {i} falló")
        
        # Pausa entre lotes
        if i < len(batches):
            logger.info("Pausa 10 segundos antes del siguiente lote...")
            time.sleep(10)
    
    # Guardar resultados
    if all_genealogias:
        save_results(all_genealogias)
        
        # Estadísticas
        total_palabras = sum(len(gen.get("genealogia", "").split()) for gen in all_genealogias)
        promedio = total_palabras / len(all_genealogias) if all_genealogias else 0
        
        logger.info("\n" + "=" * 80)
        logger.info("PROCESO COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"Lotes exitosos: {successful_batches}/{len(batches)}")
        logger.info(f"Genealogías totales: {len(all_genealogias)}")
        logger.info(f"Palabras totales: {total_palabras:,}")
        logger.info(f"Promedio palabras: {promedio:.1f}")
        logger.info(f"Tiempo total: {time.time() - start_time:.2f}s")
        logger.info("=" * 80)
        
        return len(all_genealogias) == 19
    else:
        logger.error("ERROR: No se generaron genealogías")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
