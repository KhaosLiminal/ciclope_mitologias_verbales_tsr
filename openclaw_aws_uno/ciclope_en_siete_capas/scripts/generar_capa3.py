#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_capa3.py (Mejorado con Retry Logic de Windsurf)
========================================================
Genera CAPA 3: Problematización contemporánea con validación robusta
"""

import json
import os
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from functools import wraps
import sys

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# RETRY LOGIC (inspirado en Windsurf)
# ============================================================================

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    """
    Decorador que implementa reintentos con backoff exponencial + jitter.
    Lección aprendida de Windsurf: APIs externas necesitan retry logic robusto.
    """
    def decorator(func):
        @wraps(func)
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
                        sleep_time = (backoff_in_seconds * 2 ** x + random.uniform(0, 1))
                        print(f"[RETRY] Intento {x+1}/{retries} falló. Reintentando en {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                        x += 1
        return wrapper
    return decorator

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
GLOSARIO_PATH = BASE_DIR / "config" / "GLOSARIO_CICLOPE.json"

METADATOS_PATH = BASE_DIR / "config" / "METADATOS_PROYECTO.json"
# CORRECCIÓN: Usar versión consolidada de Windsurf (más metadata)
CAPA2_PATH = BASE_DIR / "capas" / "CAPA2_genealogia" / "TSR_CAPA2_FINAL_CONSOLIDADO.json"
OUTPUT_JSON = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"

# API Keys (configura según tu modelo)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

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

def validar_extension(texto: str, min_palabras: int, max_palabras: int) -> tuple[bool, int]:
    """Valida que la extensión esté en rango"""
    palabras = len(texto.split())
    valido = min_palabras <= palabras <= max_palabras
    return valido, palabras

def cargar_genealogia(tsr_id: int, capa2_data: Dict) -> Optional[str]:
    """
    Extrae genealogía de CAPA 2.
    Adaptado para formato Windsurf: {"102": {...}, "103": {...}}
    """
    tsr_key = str(tsr_id)
    if tsr_key not in capa2_data:
        print(f"[WARN] TSR {tsr_id} no encontrado en CAPA2")
        return None
    
    return capa2_data[tsr_key].get('contenido', '')

def cargar_metadata_tsr(tsr_id: int, capa2_data: Dict) -> Optional[Dict]:
    """
    Extrae metadata enriquecida de CAPA 2 (keywords, autor, cluster).
    Solo disponible en formato Windsurf CONSOLIDADO.
    """
    tsr_key = str(tsr_id)
    if tsr_key not in capa2_data:
        return None
    
    tsr_data = capa2_data[tsr_key]
    return {
        'autor': tsr_data.get('autor'),
        'obra': tsr_data.get('obra'),
        'año': tsr_data.get('año'),
        'concepto_central': tsr_data.get('concepto_central'),
        'keywords': tsr_data.get('keywords', []),
        'cluster': tsr_data.get('cluster'),
        'conexion_RH': tsr_data.get('conexion_RH')
    }


# ============================================================================
# GENERACIÓN CON PERPLEXITY SONAR (con retry logic de Windsurf)
# ============================================================================

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def generar_problematizacion_sonar(tsr_id: int, genealogia: str, glosario: Dict) -> str:
    """
    Genera problematización usando Perplexity Sonar Pro.
    Con retry logic + validación JSON + integración glosario.
    """
    import requests
    
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY no configurada")
    
    # Extraer términos relevantes del glosario
    terminos_relevantes = ""
    if glosario and 'terminos_nucleares' in glosario:
        for termino, definicion in glosario['terminos_nucleares'].items():
            definicion_schlegel = definicion.get('definicion_schlegel', '')
            definicion_blanchot = definicion.get('definicion_blanchot', '')
            tension = definicion.get('tension_dialectica', '')
            
            if definicion_schlegel or definicion_blanchot:
                terminos_relevantes += f"\n{termino.upper()}:\n"
                if definicion_schlegel:
                    terminos_relevantes += f"- Schlegel: {definicion_schlegel}\n"
                if definicion_blanchot:
                    terminos_relevantes += f"- Blanchot: {definicion_blanchot}\n"
                if tension:
                    terminos_relevantes += f"- Tensión: {tension}\n"
    
    prompt = f"""
Genera una PROBLEMATIZACIÓN CONTEMPORÁNEA para TSR{tsr_id}.

GLOSARIO CICLOPE - USAR ESTAS DEFINICIONES CANÓNICAS:
{terminos_relevantes}

GENEALOGÍA PREVIA:
{genealogia[:800]}...

TAREA:
Escribe 1200-1500 palabras conectando el concepto con:
- Inteligencia Artificial (LLMs, autoría algorítmica)
- NFT y blockchain (arte digital, tokenización)
- Plataformas digitales (algoritmos, economía atención)
- Cultura visual algorítmica (deepfakes, filtros)

ESTRUCTURA:
1. Apertura transicional (150 palabras)
2. Problematización en presente (900 palabras)
3. Resonancia con Reflejos Híbridos (150 palabras)
4. Cierre abierto con preguntas (150 palabras)

TONO: Crítico-poético, método socrático, español mexicano.
USA LOS TÉRMINOS DEL GLOSARIO SEGÚN SUS DEFINICIONES.
SI HAY TENSIÓN DIALÉCTICA, MENCIONARLA EXPLÍCITAMENTE.
NO uses bullet points. NO cierres con respuestas definitivas.
"""
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2500
    }
    
    # Validación pre-request (lección Windsurf)
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=60  # Timeout explícito (lección Windsurf)
        )
        
        # Validar status code
        if response.status_code != 200:
            raise ValueError(f"API error: {response.status_code} - {response.text}")
        
        # Validar respuesta JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ValueError("Respuesta API no es JSON válido")
        
        # Extraer contenido
        if not data.get('choices') or not data['choices'][0].get('message'):
            raise ValueError("Estructura de respuesta inválida")
        
        contenido = data['choices'][0]['message']['content']
        
        # Validar que no esté vacío
        if not contenido or len(contenido.strip()) < 100:
            raise ValueError("Contenido generado vacío o muy corto")
        
        return contenido
        
    except requests.exceptions.Timeout:
        raise ValueError("Timeout en request a Perplexity API")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error de red: {str(e)}")

# ============================================================================
# GENERACIÓN PRINCIPAL
# ============================================================================

def generar_capa3_tsr(tsr_id: int, modelo: str, capa2_data: Dict, glosario: Dict) -> Dict:
    """Genera problematización para un TSR específico"""
    print(f"\n[GENERANDO] TSR {tsr_id}...")
    
    # Cargar genealogía
    genealogia = cargar_genealogia(tsr_id, capa2_data)
    if not genealogia:
        print(f"[ERROR] No se encontró genealogía para TSR {tsr_id}")
        return None
    
    # Generar según modelo
    try:
        if modelo == "sonar":
            problematizacion = generar_problematizacion_sonar(tsr_id, genealogia, glosario)
        else:
            problematizacion = f"[Placeholder para modelo {modelo}]"
        
        # Validar extensión
        valida, num_palabras = validar_extension(problematizacion, 1000, 1500)
        
        if not valida:
            print(f"[WARN] TSR {tsr_id}: {num_palabras} palabras (esperado: 1000-1500)")
        
        print(f"[OK] TSR {tsr_id}: {num_palabras} palabras generadas")
        
        return {
            "tsr": tsr_id,
            "problematizacion": problematizacion,
            "num_palabras": num_palabras,
            "validacion_extension": valida,
            "modelo_usado": modelo,
            "fecha_generacion": datetime.now().isoformat(),
            "glosario_utilizado": True
        }
        
    except Exception as e:
        print(f"[ERROR] TSR {tsr_id}: {str(e)}")
        return None

# ============================================================================
# CLI PRINCIPAL
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera CAPA 3 con retry logic')
    parser.add_argument('--modelo', choices=['sonar', 'claude'], default='sonar')
    parser.add_argument('--tsr', type=int, help='TSR específico (102-120)')
    parser.add_argument('--all', action='store_true', help='Generar todos')
    parser.add_argument('--validar-antes', action='store_true')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("GENERADOR DE CAPA 3: PROBLEMATIZACIÓN CONTEMPORÁNEA")
    print("=" * 70)
    print()
    
    # Cargar dependencias
    print("[INFO] Cargando dependencias...")
    capa2 = cargar_json(CAPA2_PATH)
    glosario = cargar_json(GLOSARIO_PATH)
    
    if not capa2:
        print("[FATAL] No se pudo cargar CAPA 2")
        return 1
    
    if not glosario:
        print("[WARN] Glosario no encontrado, generando sin definiciones canónicas")
        glosario = {}
    
    # CORRECCIÓN: Formato Windsurf no tiene metadata a nivel raíz
    total_tsr = len(capa2.keys()) if capa2 else 0
    print(f"[OK] CAPA 2 cargada: {total_tsr} genealogías")
    if glosario:
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
    
    # Generar problematizaciones
    resultados = []
    exitosos = 0
    fallidos = 0
    
    for tsr_id in tsr_range:
        resultado = generar_capa3_tsr(tsr_id, args.modelo, capa2, glosario)
        if resultado:
            resultados.append(resultado)
            exitosos += 1
        else:
            fallidos += 1
    
    # Guardar resultados
    output_data = {
        "metadata": {
            "capa": "CAPA 3: Problematización contemporánea",
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
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Estadísticas finales
    total_palabras = sum(r['num_palabras'] for r in resultados)
    promedio = total_palabras / len(resultados) if resultados else 0
    
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"TSR generados: {exitosos}")
    print(f"TSR fallidos: {fallidos}")
    print(f"Total palabras: {total_palabras:,}")
    print(f"Promedio por TSR: {promedio:.0f} palabras")
    print(f"Archivo guardado: {OUTPUT_JSON}")
    print("=" * 70)
    
    return 0 if fallidos == 0 else 1

if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Generación cancelada por usuario")
        exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
