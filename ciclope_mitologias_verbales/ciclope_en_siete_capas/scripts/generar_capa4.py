#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR CAPA 4: RESONANCIAS INTERDISCIPLINARIAS
Sistema modular de 7 capas para Cíclope: Mitologías Verbales

Genera resonancias interdisciplinarias que conectan la problematización
contemporánea con campos diversos (artes, ciencias, tecnología, cultura popular).

Uso:
    python scripts/generar_capa4.py --modelo sonar --all
    python scripts/generar_capa4.py --modelo sonar --tsr 102
"""

import os
import sys
import json
import time
import random
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

# ============================================================================
# CONFIGURACIÓN DE RETRY CON BACKOFF EXPONENCIAL
# ============================================================================

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    """
    Decorador para reintentos con backoff exponencial.
    Lección de Windsurf: siempre retry logic en APIs externas.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        print(f"[ERROR] Máximo de reintentos alcanzado ({retries})")
                        raise e
                    else:
                        sleep_time = (backoff_in_seconds * 2 ** x + 
                                    random.uniform(0, 1))
                        print(f"[RETRY] Intento {x+1}/{retries} falló. "
                              f"Reintentando en {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                        x += 1
        return wrapper
    return decorator

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
GLOSARIO_PATH = BASE_DIR / "config" / "GLOSARIO_CICLOPE.json"
CAPA2_PATH = BASE_DIR / "capas" / "CAPA2_genealogia" / "TSR_CAPA2_FINAL_CONSOLIDADO.json"
CAPA3_PATH = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"
PROMPT_PATH = BASE_DIR / "config" / "PROMPTS_POR_CAPA" / "CAPA4_prompt.txt"
OUTPUT_JSON = BASE_DIR / "capas" / "CAPA4_resonancias" / "TSR_CAPA4_FINAL.json"

# API Keys
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def cargar_json(path: Path) -> Optional[Dict]:
    """Carga archivo JSON con manejo de errores"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON inválido en {path}: {str(e)}")
        return None

def cargar_texto(path: Path) -> Optional[str]:
    """Carga archivo de texto"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {path}")
        return None

def validar_extension(texto: str, min_palabras: int, max_palabras: int) -> tuple[bool, int]:
    """Valida que la extensión esté en rango"""
    palabras = len(texto.split())
    valido = min_palabras <= palabras <= max_palabras
    return valido, palabras

def cargar_genealogia(tsr_id: int, capa2_data: Dict) -> Optional[str]:
    """
    Extrae genealogía de CAPA 2 (formato Windsurf consolidado).
    """
    tsr_key = str(tsr_id)
    if tsr_key not in capa2_data:
        print(f"[WARN] TSR {tsr_id} no encontrado en CAPA2")
        return None
    
    return capa2_data[tsr_key].get('contenido', '')

def cargar_problematizacion(tsr_id: int, capa3_data: Dict) -> Optional[str]:
    """
    Extrae problematización de CAPA 3.
    """
    if 'estructura' not in capa3_data:
        print(f"[ERROR] CAPA3 sin estructura")
        return None
    
    for tsr in capa3_data['estructura']:
        if tsr.get('tsr') == tsr_id:
            return tsr.get('problematizacion', '')
    
    print(f"[WARN] TSR {tsr_id} no encontrado en CAPA3")
    return None

def extraer_terminos_glosario(glosario: Dict) -> str:
    """
    Extrae términos clave del glosario para inyectar en prompt.
    """
    if not glosario or 'terminos_nucleares' not in glosario:
        return ""
    
    terminos = []
    for termino, definicion in glosario['terminos_nucleares'].items():
        desc = definicion.get('descripcion', '')
        terminos.append(f"**{termino}:** {desc}")
    
    return "\n".join(terminos)

# ============================================================================
# GENERACIÓN CON API
# ============================================================================

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def generar_resonancias_sonar(tsr_id: int, genealogia: str, problematizacion: str, 
                               prompt_template: str, glosario_texto: str) -> str:
    """
    Genera resonancias usando Perplexity Sonar Pro.
    Incluye retry logic con backoff exponencial (lección Windsurf).
    """
    
    # Construir prompt con contexto completo
    prompt = prompt_template.replace("{GLOSARIO_TERMINOS}", glosario_texto)
    prompt = prompt.replace("{TSR_ID}", str(tsr_id))
    prompt = prompt.replace("{GENEALOGIA_CAPA2}", genealogia[:1000])  # Reducido para 400-600 palabras
    prompt = prompt.replace("{PROBLEMATIZACION_CAPA3}", problematizacion[:1500])  # Reducido para 400-600 palabras
    
    # Llamada API con timeout explícito (lección Windsurf)
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un pensador interdisciplinario experto en generar resonancias conceptuales entre campos diversos. Tu estilo es denso, preciso, y siempre sostiene tensiones dialécticas sin resolverlas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 800,
            "temperature": 0.7
        },
        timeout=60  # Timeout explícito
    )
    
    # Validar respuesta (lección Windsurf: validar antes de parsear)
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code} - {response.text}")
    
    try:
        data = response.json()
    except json.JSONDecodeError:
        raise ValueError("Respuesta no es JSON válido")
    
    # Validar estructura
    if not data.get('choices') or not data['choices'][0].get('message'):
        raise ValueError("Estructura de respuesta inválida")
    
    contenido = data['choices'][0]['message']['content']
    
    # Validar contenido no vacío
    if len(contenido.strip()) < 100:
        raise ValueError("Contenido generado vacío o muy corto")
    
    return contenido

# ============================================================================
# PROCESAMIENTO BATCH
# ============================================================================

def procesar_tsr(tsr_id: int, capa2_data: Dict, capa3_data: Dict, 
                 prompt_template: str, glosario_texto: str) -> Optional[Dict]:
    """
    Procesa un TSR individual generando sus resonancias.
    """
    print(f"\n[GENERANDO] TSR {tsr_id}...")
    
    # Cargar contexto
    genealogia = cargar_genealogia(tsr_id, capa2_data)
    problematizacion = cargar_problematizacion(tsr_id, capa3_data)
    
    if not genealogia:
        print(f"[ERROR] TSR {tsr_id}: Sin genealogía")
        return None
    
    if not problematizacion:
        print(f"[ERROR] TSR {tsr_id}: Sin problematización")
        return None
    
    # Generar resonancias
    try:
        resonancias = generar_resonancias_sonar(
            tsr_id, genealogia, problematizacion, 
            prompt_template, glosario_texto
        )
    except Exception as e:
        print(f"[ERROR] TSR {tsr_id}: {str(e)}")
        return None
    
    # Validar extensión
    valido, num_palabras = validar_extension(resonancias, 400, 600)
    
    if not valido:
        print(f"[WARN] TSR {tsr_id}: {num_palabras} palabras (esperado: 400-600)")
    else:
        print(f"[OK] TSR {tsr_id}: {num_palabras} palabras generadas")
    
    # Extraer campos explorados (heurística simple)
    campos = []
    keywords_campos = {
        "Cine": ["cine", "película", "film", "director"],
        "Música": ["música", "canción", "álbum", "artista"],
        "Artes visuales": ["pintura", "escultura", "instalación", "performance"],
        "Ciencia": ["física", "biología", "neurociencia", "investigación"],
        "Tecnología": ["biotecnología", "quantum", "neurotecnología"],
        "Filosofía política": ["poder", "resistencia", "gubernamentalidad", "activismo"],
        "Cultura popular": ["meme", "videojuego", "TikTok", "viral"],
        "Pedagogía": ["educación", "pedagogía", "aprendizaje"]
    }
    
    for campo, keywords in keywords_campos.items():
        if any(kw in resonancias.lower() for kw in keywords):
            campos.append(campo)
    
    return {
        "tsr": tsr_id,
        "resonancias": resonancias,
        "num_palabras": num_palabras,
        "campos_explorados": campos,
        "validacion_extension": valido,
        "tension_explicita": "schlegel" in resonancias.lower() and "blanchot" in resonancias.lower(),
        "modelo_usado": "sonar-pro",
        "fecha_generacion": datetime.now().isoformat()
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generador CAPA 4: Resonancias Interdisciplinarias"
    )
    parser.add_argument("--modelo", default="sonar", choices=["sonar"],
                       help="Modelo a usar (actualmente solo sonar)")
    parser.add_argument("--tsr", type=int, help="TSR específico a generar")
    parser.add_argument("--all", action="store_true", 
                       help="Generar todos los TSR (102-120)")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("GENERADOR DE CAPA 4: RESONANCIAS INTERDISCIPLINARIAS")
    print("=" * 70)
    print()
    
    # Validar API key
    if not PERPLEXITY_API_KEY:
        print("[ERROR] PERPLEXITY_API_KEY no configurada")
        return 1
    
    # Cargar dependencias
    print("[INFO] Cargando dependencias...")
    capa2 = cargar_json(CAPA2_PATH)
    capa3 = cargar_json(CAPA3_PATH)
    glosario = cargar_json(GLOSARIO_PATH)
    prompt_template = cargar_texto(PROMPT_PATH)
    
    if not capa2 or not capa3:
        print("[ERROR] No se pudieron cargar CAPA2 o CAPA3")
        return 1
    
    if not prompt_template:
        print("[WARN] Prompt no encontrado, usando template básico")
        prompt_template = "Genera resonancias interdisciplinarias para TSR {TSR_ID}..."
    
    if not glosario:
        print("[WARN] Glosario no encontrado")
        glosario_texto = ""
    else:
        glosario_texto = extraer_terminos_glosario(glosario)
    
    total_tsr = len(capa2.keys()) if capa2 else 0
    print(f"[OK] CAPA 2 cargada: {total_tsr} genealogías")
    print(f"[OK] CAPA 3 cargada: {len(capa3.get('estructura', []))} problematizaciones")
    if glosario_texto:
        print(f"[OK] Glosario cargado: {len(glosario.get('terminos_nucleares', {}))} términos")
    print()
    
    # Determinar rango de TSR
    if args.all:
        tsr_range = range(102, 121)
    elif args.tsr:
        tsr_range = [args.tsr]
    else:
        print("[ERROR] Especifica --tsr N o --all")
        return 1
    
    # Generar resonancias
    resultados = []
    exitosos = 0
    fallidos = 0
    total_palabras = 0
    
    for tsr_id in tsr_range:
        resultado = procesar_tsr(tsr_id, capa2, capa3, prompt_template, glosario_texto)
        
        if resultado:
            resultados.append(resultado)
            exitosos += 1
            total_palabras += resultado['num_palabras']
        else:
            fallidos += 1
    
    # Guardar resultados
    if resultados:
        output_data = {
            "metadata": {
                "capa": "CAPA 4: Resonancias interdisciplinarias",
                "fecha_generacion": datetime.now().isoformat(),
                "total_tsr": len(resultados),
                "exitosos": exitosos,
                "fallidos": fallidos,
                "modelo": args.modelo
            },
            "estructura": resultados
        }
        
        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print()
        print("=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"TSR generados: {exitosos}")
        print(f"TSR fallidos: {fallidos}")
        print(f"Total palabras: {total_palabras:,}")
        if exitosos > 0:
            print(f"Promedio por TSR: {total_palabras // exitosos} palabras")
        print(f"Archivo guardado: {OUTPUT_JSON}")
        print("=" * 70)
    else:
        print("[ERROR] No se generó ningún TSR")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
