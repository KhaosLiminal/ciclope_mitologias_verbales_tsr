#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TSR_CAPA2_Genealogias.py (v2 - MEJORADO)
=========================================================

Estrategia: UN llamado a Sonar con 19 genealogías en 1 prompt.

MEJORAS v2:
  ✓ Parámetros académicos (search_mode, web_search_options)
  ✓ max_tokens: 20000 (no 12000) → evita truncamiento
  ✓ Extrae citations y search_results
  ✓ Limpia JSON si viene envuelto en markdown
  ✓ Usa response_format para JSON válido
  ✓ Logging de citations y search_results

Confianza: 100% en Sonar. Capacidad documentada: 100 token/sec.
"""

import json
import requests
import time
import logging
import os
import re
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

# Reintentos
MAX_ATTEMPTS = 3
INITIAL_DELAY = 5  # segundos
TIMEOUT = 300  # 5 minutos para 32k tokens

# Logging
LOG_DIR = Path("logs/CAPA2")
LOG_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOG_DIR / f"CAPA2_ejecucion_{TIMESTAMP}.log"
RAW_RESPONSE_FILE = LOG_DIR / f"CAPA2_respuesta_cruda_{TIMESTAMP}.txt"
CITATIONS_FILE = LOG_DIR / f"CAPA2_citations_{TIMESTAMP}.json"

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# UTILIDADES DE TOKENS
# ============================================================================

def estimate_tokens(text: str) -> int:
    """Estimate token count for a given text (approximation)."""
    # Rough estimation: 1 token ~= 4 characters in English, 2 in Spanish
    # Using 3 as average to be safe
    return math.ceil(len(text) / 3)

# ============================================================================
# UTILIDADES DE MÉTRICAS
# ============================================================================

def save_execution_metrics(start_time: float, input_tokens: int, output_tokens: int, metadata_resp: Dict) -> None:
    """Guarda métricas de ejecución para análisis posterior."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": time.time() - start_time,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tokens_per_second": output_tokens / (time.time() - start_time) if (time.time() - start_time) > 0 else 0,
        "model": SONAR_MODEL,
        "attempt": metadata_resp.get("intent", 0),
        "citations_count": len(metadata_resp.get("citations", [])),
        "search_results_count": len(metadata_resp.get("search_results", []))
    }
    
    metrics_file = LOG_DIR / "execution_metrics.json"
    try:
        # Load existing metrics if any
        existing = []
        if metrics_file.exists():
            with open(metrics_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = []
        
        # Add new metrics
        existing.append(metrics)
        
        # Save back
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
            
        logger.info(f"Metricas guardadas: {len(existing)} ejecuciones registradas")
        
    except Exception as e:
        logger.error(f"ADVERTENCIA: Error al guardar métricas: {str(e)}")

# ============================================================================
# UTILIDADES DE CARGA DE METADATOS
# ============================================================================

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
        
        # Filtrar solo TSRs 102-120 y extraer campos necesarios
        metadata = []
        for tsr in tsrs:
            num = tsr.get('tsr', tsr.get('numero', 0))
            # Convertir a entero si es string
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
        
        # Ordenar por número
        metadata.sort(key=lambda x: x['numero'])
        
        logger.info(f"OK: {len(metadata)} TSRs cargados (102-120)")
        return metadata
        
    except Exception as e:
        logger.error(f"ERROR cargando metadatos: {str(e)}")
        return []

# ============================================================================
# UTILIDADES DE LIMPIEZA JSON
# ============================================================================

def clean_json_response(text: str) -> str:
    """Limpia respuesta JSON si viene envuelta en bloques markdown."""
    logger.debug("Limpiando JSON...")

    text = text.strip()

    # Si empieza con ```json
    if text.startswith("```json"):
        logger.debug("  - Detectado bloque ```json, extrayendo...")
        text = text[7:]

    # Si empieza con ```
    if text.startswith("```"):
        logger.debug("  - Detectado bloque ```, extrayendo...")
        text = text[3:]

    # Si termina con ```
    if text.endswith("```"):
        logger.debug("  - Removiendo cierre ```")
        text = text[:-3]

    text = text.strip()
    logger.debug(f"  JSON limpio: {len(text)} caracteres")

    return text

# ============================================================================
# FASE 1: GENERAR MEGAPROMPT
# ============================================================================

def generate_megaprompt(metadata: List[Dict]) -> str:
    """Genera megaprompt con 19 genealogías para Sonar."""
    logger.info("FASE 1: GENERACIÓN DE MEGAPROMPT")

    megaprompt = """
TAREA CRÍTICA: Genealogías de 19 conceptos filosóficos (500-700 palabras c/u)
=============================================================================

Formato requerido: JSON estructurado con esta forma EXACTA:

{
  "genealogias": [
    {
      "tsr": 102,
      "concepto": "función-autor",
      "genealogia": "[500-700 palabras aquí]"
    },
    ...
  ]
}

REQUISITOS CRÍTICOS:
  ✓ Total: 19 genealogías (TSR 102-120)
  ✓ Rango: 500-700 palabras POR GENEALOGÍA
  ✓ Estructura: 4 fases (origen, autor, crítica, presente)
  ✓ JSON válido (sin markdown)
  ✓ Responde SOLO JSON

¿LISTO? Devuelve 19 genealogías en JSON puro.
"""

    # Añadir metadata de cada TSR
    for i, tsr in enumerate(metadata, 1):
        megaprompt += f"\nTSR {i}/19 - #{tsr['numero']}: {tsr['concepto_central']}"

    return megaprompt

# ============================================================================
# FASE 2: LLAMADA A SONAR CON REINTENTOS (V2 MEJORADO)
# ============================================================================

def call_sonar_with_retries(megaprompt: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Llama Sonar API con reintentos automáticos y manejo mejorado de tokens."""
    logger.info("FASE 2: LLAMADA A SONAR API (v3 - MEJORADA)")
    
    # Estimate tokens and adjust max_tokens accordingly
    estimated_input_tokens = estimate_tokens(megaprompt)
    max_output_tokens = 32000  # Maximum allowed by API - increased
    safety_margin = 2000  # Increased safety margin
    
    # Ensure we don't exceed model's context window
    max_tokens = min(max_output_tokens, 128000 - estimated_input_tokens - safety_margin)  # Sonar-pro has 128k context
    
    logger.info(f"  Tokens estimados (input): {estimated_input_tokens}")
    logger.info(f"  Tokens máximos (output): {max_tokens}")
    
    # Payload MEJORADO con parámetros académicos
    payload = {
        "model": SONAR_MODEL,
        "messages": [{"role": "user", "content": megaprompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
        # ← NUEVO: Parámetros académicos
        "search_mode": "academic",
        "web_search_options": {"search_context_size": "high"},
        "search_language_filter": ["es", "en", "fr", "de"],
        # ← NUEVO: Forzar JSON válido (Perplexity no soporta response_format)
        # "response_format": {"type": "json_object"},  # No soportado por Perplexity
        "stream": False  # Disable streaming for better error handling
    }
    
    logger.info(f"  max_tokens: {max_tokens} (ajustado dinámicamente)")
    logger.info(f"  search_mode: academic")
    logger.info(f"  response_format: no soportado (usando prompt)")

    metadata_respuesta = {"intent": 0, "tiempo_respuesta": 0, "citations": [], "search_results": []}

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            logger.info(f"INTENTO {attempt}/{MAX_ATTEMPTS}")
            start_time = time.time()

            response = requests.post(SONAR_API_URL, headers=HEADERS, json=payload, timeout=TIMEOUT)
            elapsed = time.time() - start_time
            metadata_respuesta["tiempo_respuesta"] = elapsed

            logger.info(f"  Status: {response.status_code} | Tiempo: {elapsed:.2f}s")

            # Validar status code
            if response.status_code == 401:
                logger.error("ERROR 401 Unauthorized: API key inválida")
                # Mask API key in logs
                masked_key = f"{SONAR_API_KEY[:4]}...{SONAR_API_KEY[-4:]}" if SONAR_API_KEY else "no-key"
                logger.debug(f"API Key usada: {masked_key}")
                raise ValueError("API key invalid")
            elif response.status_code == 429:
                logger.warning("ADVERTENCIA 429 Rate Limited")
                if attempt < MAX_ATTEMPTS:
                    delay = INITIAL_DELAY * (2 ** (attempt - 1))
                    time.sleep(delay)
                    continue
                else:
                    return None, metadata_respuesta

            # ✓ Respuesta 200
            logger.info("OK HTTP 200 OK")

            # Guardar respuesta cruda
            with open(RAW_RESPONSE_FILE, "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info(f"OK Respuesta guardada")

            # Extraer contenido MEJORADO
            response_json = response.json()
            
            # Verificar estructura de respuesta
            if "choices" not in response_json:
                logger.error("ERROR: Respuesta no contiene 'choices'")
                logger.debug(f"Estructura recibida: {list(response_json.keys())}")
                return None, metadata_respuesta
                
            if not response_json["choices"]:
                logger.error("ERROR: 'choices' está vacío")
                return None, metadata_respuesta
                
            genealogias_text = response_json["choices"][0]["message"]["content"]

            # ← NUEVO: Extraer citations y search_results
            citations = response_json.get("citations", [])
            search_results = response_json.get("search_results", [])

            metadata_respuesta["citations"] = citations
            metadata_respuesta["search_results"] = search_results
            metadata_respuesta["intent"] = attempt

            logger.info(f"OK Contenido: {len(genealogias_text)} caracteres")
            logger.info(f"OK Citations académicas: {len(citations)}")
            logger.info(f"OK Search results: {len(search_results)}")

            # Guardar citations
            if citations:
                with open(CITATIONS_FILE, "w", encoding="utf-8") as f:
                    json.dump(citations, f, ensure_ascii=False, indent=2)
                logger.info(f"OK Citations guardadas")

            return genealogias_text, metadata_respuesta

        except requests.exceptions.Timeout:
            logger.warning(f"ADVERTENCIA Timeout")
            if attempt < MAX_ATTEMPTS:
                delay = INITIAL_DELAY * (2 ** (attempt - 1))
                time.sleep(delay)
                continue
            else:
                return None, metadata_respuesta

        except requests.exceptions.RequestException as e:
            logger.error(f"ERROR en la petición: {str(e)}")
            if "401" in str(e):
                logger.error("ERROR de autenticación. Verifica tu API key.")
                # Mask API key in logs
                masked_key = f"{SONAR_API_KEY[:4]}...{SONAR_API_KEY[-4:]}" if SONAR_API_KEY else "no-key"
                logger.debug(f"API Key usada: {masked_key}")
            return None, metadata_respuesta
        except Exception as e:
            logger.error(f"ERROR inesperado: {str(e)}")
            return None, metadata_respuesta

    return None, metadata_respuesta

# ============================================================================
# FASE 3: VALIDACIÓN DE RESPUESTA (V2 MEJORADO)
# ============================================================================

def validate_response(genealogias_text: str) -> Tuple[bool, Dict]:
    """Valida que la respuesta contiene 19 genealogías válidas."""
    logger.info("FASE 3: VALIDACIÓN DE RESPUESTA")

    issues = {
        "json_valid": False,
        "estructura_ok": False,
        "cantidad_ok": False,
        "rango_ok": False,
        "errores": [],
        "genealogias_validadas": []
    }

    try:
        # ← NUEVO: Limpiar JSON si viene envuelto
        genealogias_text_clean = clean_json_response(genealogias_text)
        genealogias_data = json.loads(genealogias_text_clean)
        issues["json_valid"] = True
        logger.info("OK JSON válido")

    except json.JSONDecodeError as e:
        logger.error(f"ERROR JSON inválido: {e}")
        issues["errores"].append(f"JSON parse error: {str(e)}")
        return False, issues

    try:
        if "genealogias" not in genealogias_data:
            raise KeyError("Falta clave 'genealogias'")

        genealogias_list = genealogias_data["genealogias"]
        if not isinstance(genealogias_list, list):
            raise TypeError("'genealogias' debe ser array")

        issues["estructura_ok"] = True
        logger.info("OK Estructura correcta")

    except (KeyError, TypeError) as e:
        logger.error(f"ERROR Estructura: {e}")
        issues["errores"].append(f"Structure error: {str(e)}")
        return False, issues

    try:
        if len(genealogias_list) != 19:
            logger.warning(f"ADVERTENCIA Got {len(genealogias_list)} genealogias, expected 19")
            issues["errores"].append(f"Got {len(genealogias_list)}/19")
        else:
            issues["cantidad_ok"] = True
            logger.info("OK Cantidad: 19 genealogías")

        # ← MEJORADO: Validación granular
        word_counts_ok = 0
        for i, gen in enumerate(genealogias_list):
            validation = {"tsr": None, "ok": False, "palabra_count": 0, "issues": []}

            if "tsr" not in gen or "genealogia" not in gen:
                validation["issues"].append("falta TSR o genealogia")
                issues["errores"].append(f"Gen {i}: {validation['issues'][0]}")
                continue

            validation["tsr"] = gen["tsr"]
            palabras = len(gen["genealogia"].split())
            validation["palabra_count"] = palabras

            if 500 <= palabras <= 700:
                word_counts_ok += 1
                validation["ok"] = True
            else:
                validation["issues"].append(f"{palabras} palabras (500-700 expected)")
                issues["errores"].append(f"TSR{gen['tsr']}: {palabras} palabras")

            if gen["genealogia"].endswith("...") or len(gen["genealogia"]) < 100:
                validation["issues"].append("posible truncamiento")

            issues["genealogias_validadas"].append(validation)

        if word_counts_ok == len(genealogias_list):
            issues["rango_ok"] = True
            logger.info(f"OK Rango: todas en 500-700 palabras")
        else:
            logger.warning(f"ADVERTENCIA {word_counts_ok}/{len(genealogias_list)} en rango correcto")

    except Exception as e:
        logger.error(f"ERROR validando: {e}")
        issues["errores"].append(f"Validation error: {str(e)}")
        return False, issues

    is_valid = (issues["json_valid"] and issues["estructura_ok"] and 
                issues["cantidad_ok"] and issues["rango_ok"])

    if is_valid:
        logger.info("OK VALIDACIÓN EXITOSA")
    else:
        logger.warning(f"ADVERTENCIA {len(issues['errores'])} problemas detectados")

    return is_valid, issues

# ============================================================================
# FASE 4: PROCESAMIENTO Y GUARDADO
# ============================================================================

def process_genealogias(genealogias_text: str) -> Dict:
    """Procesa genealogías y las guarda en archivos."""
    logger.info("FASE 4: PROCESAMIENTO Y GUARDADO")

    results_dir = Path("resultados/TSR_CAPA2_Genealogias")
    results_dir.mkdir(parents=True, exist_ok=True)

    statistics = {
        "total_genealogias": 0,
        "guardadas": 0,
        "palabra_count_total": 0,
        "palabra_count_promedio": 0,
        "errores": []
    }

    try:
        genealogias_text_clean = clean_json_response(genealogias_text)
        genealogias_data = json.loads(genealogias_text_clean)
        genealogias_list = genealogias_data.get("genealogias", [])

        for gen in genealogias_list:
            try:
                tsr = gen.get("tsr")
                concepto = gen.get("concepto", "Unknown")
                genealogia = gen.get("genealogia", "")

                statistics["total_genealogias"] += 1

                filename = results_dir / f"TSR_{tsr:03d}_genealogia.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"# TSR {tsr}: {concepto}\n\n")
                    f.write(genealogia)

                word_count = len(genealogia.split())
                statistics["palabra_count_total"] += word_count
                statistics["guardadas"] += 1

                logger.info(f"OK TSR{tsr:03d}: {word_count} palabras")

            except Exception as e:
                logger.error(f"ERROR: {e}")
                statistics["errores"].append(str(e))

        if statistics["guardadas"] > 0:
            statistics["palabra_count_promedio"] = statistics["palabra_count_total"] // statistics["guardadas"]

    except Exception as e:
        logger.error(f"ERROR procesamiento: {e}")
        statistics["errores"].append(str(e))

    return statistics

# ============================================================================
# MAIN
# ============================================================================

def main() -> bool:
    """Orquesta el flujo completo con mejor manejo de errores."""
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("INICIANDO GENERACIÓN DE GENEALOGÍAS (v3 MEJORADA)")
    logger.info("=" * 80)
    
    try:
        # 1. Cargar metadatos
        logger.info("\nCargando metadatos...")
        metadata = load_metadata()
        if not metadata or len(metadata) != 19:
            logger.error("ERROR: Se requieren exactamente 19 TSRs (102-120)")
            return False
        
        # 2. Generar megaprompt
        logger.info("\nGenerando megaprompt...")
        megaprompt = generate_megaprompt(metadata)
        prompt_tokens = estimate_tokens(megaprompt)
        logger.info(f"  Prompt size: {len(megaprompt)} caracteres, ~{prompt_tokens} tokens")
        
        # 3. Llamar a Sonar
        logger.info("\nEnviando a Sonar...")
        response_text, metadata_resp = call_sonar_with_retries(megaprompt)
        if not response_text:
            return False
            
        # 4. Validar y procesar
        logger.info("\nValidando respuesta...")
        is_valid, issues = validate_response(response_text)
        if not is_valid:
            logger.warning("ADVERTENCIA Validación parcial, continuando...")
            # Guardar respuesta problemática
            with open("error_response.txt", "w", encoding="utf-8") as f:
                f.write(response_text)
            logger.info("Respuesta problemática guardada en 'error_response.txt'")
            
        # 5. Guardar resultados
        logger.info("\nGuardando resultados...")
        statistics = process_genealogias(response_text)
        
        # 6. Guardar métricas
        output_tokens = estimate_tokens(response_text)
        save_execution_metrics(start_time, prompt_tokens, output_tokens, metadata_resp)
        
        # Resumen final
        logger.info("\n" + "=" * 80)
        logger.info("PROCESO COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"Genealogías procesadas: {statistics['guardadas']}/19")
        logger.info(f"Palabras totales: {statistics['palabra_count_total']:,}")
        logger.info(f"Promedio palabras/genealogía: {statistics['palabra_count_promedio']}")
        logger.info(f"Tiempo total: {time.time() - start_time:.2f}s")
        logger.info(f"Citaciones académicas: {len(metadata_resp.get('citations', []))}")
        logger.info(f"Resultados de búsqueda: {len(metadata_resp.get('search_results', []))}")
        
        if not is_valid:
            logger.warning(f"ADVERTENCIA Problemas detectados: {len(issues['errores'])}")
            for error in issues['errores'][:5]:  # Mostrar primeros 5 errores
                logger.warning(f"   - {error}")
        
        success = statistics['guardadas'] == 19 and is_valid
        logger.info(f"\n{'EXITO COMPLETO' if success else 'PROCESO PARCIAL'}")
        logger.info("=" * 80)
        
        return success
        
    except Exception as e:
        logger.error(f"\nERROR CRÍTICO: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)