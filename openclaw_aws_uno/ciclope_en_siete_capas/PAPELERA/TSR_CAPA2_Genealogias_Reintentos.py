#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TSR_CAPA2_Genealogias_Reintentos.py
Reintenta generar solo las genealogías que están truncadas (< 500 palabras)
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

SONAR_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not SONAR_API_KEY:
    raise ValueError("ERROR: PERPLEXITY_API_KEY no está configurada")

HEADERS = {
    "Authorization": f"Bearer {SONAR_API_KEY}",
    "Content-Type": "application/json"
}

MAX_ATTEMPTS = 3
INITIAL_DELAY = 5
TIMEOUT = 180

# Logging
LOG_DIR = Path("logs/CAPA2_Reintentos")
LOG_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"CAPA2_reintentos_{TIMESTAMP}.log"

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
        return metadata
        
    except Exception as e:
        logger.error(f"ERROR cargando metadatos: {str(e)}")
        return []

def find_truncated_genealogias() -> List[Tuple[int, str]]:
    """Encuentra genealogías truncadas (< 500 palabras)."""
    results_dir = Path("resultados/TSR_CAPA2_Genealogias_Batch")
    truncated = []
    
    if not results_dir.exists():
        logger.error("ERROR: No existe resultados/TSR_CAPA2_Genealogias_Batch")
        return truncated
    
    for tsr_num in range(102, 121):
        filename = results_dir / f"TSR_{tsr_num:03d}_genealogia.md"
        
        if filename.exists():
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                # Contar palabras (excluyendo título)
                lines = content.split('\n')
                if len(lines) >= 3:
                    genealogia_text = '\n'.join(lines[2:])
                    word_count = len(genealogia_text.split())
                    
                    if word_count < 500:
                        concepto = lines[0].replace(f"# TSR {tsr_num}: ", "")
                        truncated.append((tsr_num, concepto))
                        logger.info(f"TSR{tsr_num}: {word_count} palabras (truncada)")
                    else:
                        logger.info(f"TSR{tsr_num}: {word_count} palabras (OK)")
        else:
            logger.warning(f"TSR{tsr_num}: Archivo no encontrado")
            concepto = f"TSR {tsr_num}"
            truncated.append((tsr_num, concepto))
    
    return truncated

def generate_single_prompt(tsr_num: int, concepto: str) -> str:
    """Genera prompt para una sola genealogía."""
    prompt = f"""
TAREA CRÍTICA: Genealogía de un concepto filosófico (500-700 palabras)
=============================================================================

Formato requerido: JSON estructurado con esta forma EXACTA:

{{
  "genealogias": [
    {{
      "tsr": {tsr_num},
      "concepto": "{concepto}",
      "genealogia": "[500-700 palabras aquí]"
    }}
  ]
}}

REQUISITOS CRÍTICOS:
  ✓ TSR: {tsr_num}
  ✓ Concepto: {concepto}
  ✓ Rango: 500-700 palabras exactas
  ✓ Estructura: 4 fases (origen, autor, crítica, presente)
  ✓ JSON válido (sin markdown)
  ✓ Responde SOLO JSON

CONCEPTO A PROCESAR:
TSR#{tsr_num}: {concepto}

¿LISTO? Devuelve la genealogía completa en JSON puro.
"""
    
    return prompt

def call_sonar_with_retries(prompt: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Llama Sonar API con reintentos para una sola genealogía."""
    estimated_input_tokens = estimate_tokens(prompt)
    max_output_tokens = 4000  # Suficiente para una genealogía completa
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

def save_genealogia(tsr_num: int, concepto: str, genealogia: str) -> bool:
    """Guarda una genealogía individual."""
    try:
        results_dir = Path("resultados/TSR_CAPA2_Genealogias_Batch")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        filename = results_dir / f"TSR_{tsr_num:03d}_genealogia.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# TSR {tsr_num}: {concepto}\n\n")
            f.write(genealogia)
        
        word_count = len(genealogia.split())
        logger.info(f"Guardado: TSR{tsr_num} ({word_count} palabras)")
        
        return True
        
    except Exception as e:
        logger.error(f"ERROR guardando TSR{tsr_num}: {str(e)}")
        return False

# ============================================================================
# MAIN
# ============================================================================

def main() -> bool:
    """Reintenta generar genealogías truncadas."""
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("REINTENTOS DE GENEALOGÍAS TRUNCADAS")
    logger.info("=" * 80)
    
    # Encontrar genealogías truncadas
    truncated = find_truncated_genealogias()
    
    if not truncated:
        logger.info("No hay genealogías truncadas. Todas están OK.")
        return True
    
    logger.info(f"Found {len(truncated)} genealogías truncadas:")
    for tsr_num, concepto in truncated:
        logger.info(f"  - TSR{tsr_num}: {concepto}")
    
    # Procesar cada genealogía truncada
    successful = 0
    failed = 0
    
    for i, (tsr_num, concepto) in enumerate(truncated, 1):
        logger.info(f"\nPROCESANDO {i}/{len(truncated)}: TSR{tsr_num}")
        
        # Generar prompt
        prompt = generate_single_prompt(tsr_num, concepto)
        
        # Llamar a API
        response_text, metadata_resp = call_sonar_with_retries(prompt)
        
        if response_text:
            try:
                # Procesar respuesta
                response_clean = clean_json_response(response_text)
                response_data = json.loads(response_clean)
                genealogias = response_data.get("genealogias", [])
                
                if genealogias:
                    genealogia = genealogias[0].get("genealogia", "")
                    word_count = len(genealogia.split())
                    
                    if 500 <= word_count <= 700:
                        # Guardar genealogía completa
                        if save_genealogia(tsr_num, concepto, genealogia):
                            successful += 1
                            logger.info(f"TSR{tsr_num}: {word_count} palabras OK")
                        else:
                            failed += 1
                    else:
                        logger.warning(f"TSR{tsr_num}: {word_count} palabras (fuera de rango)")
                        failed += 1
                else:
                    logger.error(f"TSR{tsr_num}: Sin genealogías en respuesta")
                    failed += 1
                    
            except Exception as e:
                logger.error(f"TSR{tsr_num}: Error procesando respuesta: {str(e)}")
                failed += 1
        else:
            logger.error(f"TSR{tsr_num}: Sin respuesta de API")
            failed += 1
        
        # Pausa entre llamadas
        if i < len(truncated):
            logger.info("Pausa 8 segundos...")
            time.sleep(8)
    
    # Resumen final
    logger.info("\n" + "=" * 80)
    logger.info("PROCESO COMPLETADO")
    logger.info("=" * 80)
    logger.info(f"Exitosos: {successful}")
    logger.info(f"Fallidos: {failed}")
    logger.info(f"Tiempo total: {time.time() - start_time:.2f}s")
    logger.info("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
