#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR CAPA 5: META-ANÁLISIS CONCEPTUAL
Sistema modular de 7 capas para Cíclope: Mitologías Verbales

Genera meta-análisis conceptual que sintetiza patrones, tensiones y resonancias
identificadas en las capas anteriores (bibliografía, genealogía, problematización,
resonancias) para identificar estructuras conceptuales profundas.

Uso:
    python scripts/generar_capa5.py --modelo minimax --all
    python scripts/generar_capa5.py --modelo minimax --tsr 102
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
from typing import Dict, Optional, List, Tuple

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
CAPA1_PATH = BASE_DIR / "capas" / "CAPA1_bibliografia" / "TSR_CAPA1_FINAL.json"
CAPA2_PATH = BASE_DIR / "capas" / "CAPA2_genealogia" / "TSR_CAPA2_FINAL_CONSOLIDADO.json"
CAPA3_PATH = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"
CAPA4_PATH = BASE_DIR / "capas" / "CAPA4_resonancias" / "TSR_CAPA4_FINAL.json"
PROMPT_PATH = BASE_DIR / "config" / "PROMPTS_POR_CAPA" / "CAPA5_prompt.txt"
OUTPUT_JSON = BASE_DIR / "capas" / "CAPA5_metanalisis" / "TSR_CAPA5_FINAL.json"

# API Keys
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")

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

def validar_extension(texto: str, min_palabras: int, max_palabras: int) -> Tuple[bool, int]:
    """Valida que la extensión esté en rango"""
    palabras = len(texto.split())
    valido = min_palabras <= palabras <= max_palabras
    return valido, palabras

def extraer_datos_tsr(tsr_id: int, *capas_data) -> Dict:
    """Extrae y consolida datos de todas las capas para un TSR"""
    
    # CAPA1: Estructura anidada por clusters
    bibliografia = {}
    if capas_data[0]:
        capa1_data = capas_data[0]
        # Buscar en todos los clusters
        for cluster_name, tsrs in capa1_data.get("clusters", {}).items():
            for tsr in tsrs:
                if tsr.get("tsr") == str(tsr_id):
                    bibliografia = {
                        "concepto_principal": tsr.get("titulo", ""),
                        "autores_clave": [f.get("autor", "") for f in tsr.get("fuentes", []) if f.get("autor")],
                        "obras_fundamentales": [f.get("titulo", "") for f in tsr.get("fuentes", []) if f.get("titulo")],
                        "tendencias_actuales": [f.get("notas", "") for f in tsr.get("fuentes", []) if f.get("notas")]
                    }
                    break
    
    # CAPA2: Estructura directa por TSR ID
    genealogia = {}
    if capas_data[1]:
        tsr_data = capas_data[1].get(str(tsr_id), {})
        genealogia = {
            "origenes_historicos": tsr_data.get("contenido", "")[:500] if tsr_data.get("contenido") else "",
            "evolucion_conceptual": tsr_data.get("contenido", "")[500:1000] if tsr_data.get("contenido") and len(tsr_data.get("contenido", "")) > 500 else "",
            "momentos_clave": tsr_data.get("keywords", [])
        }
    
    # CAPA3: Estructura en array con clave "tsr"
    problematizacion = {}
    if capas_data[2]:
        for item in capas_data[2].get("estructura", []):
            if item.get("tsr") == tsr_id:
                problematizacion = {
                    "tensiones_contemporaneas": item.get("problematizacion", "")[:500] if item.get("problematizacion") else "",
                    "debates_actuales": ["IA y autoría", "Verdad algorítmica", "Archivo digital"],
                    "cuestiones_abiertas": ["¿Quién detenta la verdad cuando el autor se disuelve?"]
                }
                break
    
    # CAPA4: Estructura en array con clave "tsr"
    resonancias = {}
    if capas_data[3]:
        for item in capas_data[3].get("estructura", []):
            if item.get("tsr") == tsr_id:
                resonancias = {
                    "conexiones_interdisciplinares": item.get("resonancias", "")[:300] if item.get("resonancias") else "",
                    "aplicaciones_creative": ["Arte digital", "Filosofía política", "Tecnología crítica"],
                    "impacto_cultural": "Resonancias con Reflejos Híbridos y cultura contemporánea"
                }
                break
    
    return {
        "tsr_id": tsr_id,
        "concepto_principal": bibliografia.get("concepto_principal", ""),
        "bibliografia": {
            "concepto": bibliografia.get("concepto_principal", ""),
            "autores_clave": bibliografia.get("autores_clave", []),
            "obras_fundamentales": bibliografia.get("obras_fundamentales", []),
            "tendencias_actuales": bibliografia.get("tendencias_actuales", [])
        },
        "genealogia": {
            "origenes_historicos": genealogia.get("origenes_historicos", ""),
            "evolucion_conceptual": genealogia.get("evolucion_conceptual", ""),
            "momentos_clave": genealogia.get("momentos_clave", [])
        },
        "problematizacion": {
            "tensiones_contemporaneas": problematizacion.get("tensiones_contemporaneas", ""),
            "debates_actuales": problematizacion.get("debates_actuales", []),
            "cuestiones_abiertas": problematizacion.get("cuestiones_abiertas", [])
        },
        "resonancias": {
            "conexiones_interdisciplinares": resonancias.get("conexiones_interdisciplinares", ""),
            "aplicaciones_creative": resonancias.get("aplicaciones_creative", []),
            "impacto_cultural": resonancias.get("impacto_cultural", "")
        }
    }

# ============================================================================
# CLIENTES API
# ============================================================================

@retry_with_backoff(retries=3)
def api_perplexity(prompt: str, model="sonar") -> Optional[str]:
    """Cliente para API de Perplexity"""
    if not PERPLEXITY_API_KEY:
        print("[ERROR] PERPLEXITY_API_KEY no configurada")
        return None
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": f"llama-3.1-{model}-70b-online",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] API Perplexity: {str(e)}")
        return None

@retry_with_backoff(retries=3)
def api_minimax(prompt: str, model="minimax-text-01") -> Optional[str]:
    """Cliente para API de MiniMax"""
    if not MINIMAX_API_KEY:
        print("[ERROR] MINIMAX_API_KEY no configurada")
        return None
    
    url = "https://api.minimax.chat/v1/text/chatcompletion"
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] API MiniMax: {str(e)}")
        return None

def api_opencode_minimax(prompt: str) -> Optional[str]:
    """Cliente para OpenCode MiniMax M2.5-free"""
    try:
        import subprocess
        # Ejecutar OpenCode con el prompt
        cmd = ["opencode", "--model", "opencode/minimax-m2.5-free", "run", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # Extraer solo la respuesta del modelo (eliminar metadatos)
            lines = result.stdout.split('\n')
            response_lines = []
            capturing = False
            
            for line in lines:
                if '> build · minimax-m2.5-free' in line:
                    capturing = True
                    continue
                elif capturing and line.startswith('$'):
                    break
                elif capturing and line.strip():
                    response_lines.append(line.strip())
            
            return '\n'.join(response_lines) if response_lines else result.stdout
        else:
            print(f"[ERROR] OpenCode: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en OpenCode")
        return None
    except Exception as e:
        print(f"[ERROR] OpenCode: {str(e)}")
        return None

# ============================================================================
# GENERACIÓN DE META-ANÁLISIS
# ============================================================================

def construir_prompt_metaanalisis(datos_tsr: Dict, prompt_base: str) -> str:
    """Construye prompt personalizado para meta-análisis"""
    
    contexto = f"""
## DATOS CONSOLIDADOS TSR{datos_tsr['tsr_id']}: {datos_tsr['concepto_principal']}

### BIBLIOGRAFÍA
- Concepto: {datos_tsr['bibliografia']['concepto']}
- Autores clave: {', '.join(datos_tsr['bibliografia']['autores_clave'])}
- Obras fundamentales: {', '.join(datos_tsr['bibliografia']['obras_fundamentales'])}
- Tendencias actuales: {datos_tsr['bibliografia']['tendencias_actuales']}

### GENEALOGÍA
- Orígenes históricos: {datos_tsr['genealogia']['origenes_historicos']}
- Evolución conceptual: {datos_tsr['genealogia']['evolucion_conceptual']}
- Momentos clave: {', '.join(datos_tsr['genealogia']['momentos_clave'])}

### PROBLEMATIZACIÓN
- Tensiones contemporáneas: {datos_tsr['problematizacion']['tensiones_contemporaneas']}
- Debates actuales: {', '.join(datos_tsr['problematizacion']['debates_actuales'])}
- Cuestiones abiertas: {', '.join(datos_tsr['problematizacion']['cuestiones_abiertas'])}

### RESONANCIAS
- Conexiones interdisciplinares: {datos_tsr['resonancias']['conexiones_interdisciplinares']}
- Aplicaciones creativas: {', '.join(datos_tsr['resonancias']['aplicaciones_creative'])}
- Impacto cultural: {datos_tsr['resonancias']['impacto_cultural']}

## TAREA DE META-ANÁLISIS
Realiza un meta-análisis conceptual que:
1. Identifique patrones recurrentes entre las capas
2. Sintetice tensiones conceptuales profundas
3. Revele estructuras epistemológicas subyacentes
4. Proponga marcos de análisis integradores
5. Mantenga las contradicciones productivas sin resolverlas

Extensión: 800-1200 palabras
Estilo: Analítico, integrador, riguroso
"""
    
    return f"{prompt_base}\n\n{contexto}"

def generar_metaanalisis_tsr(datos_tsr: Dict, prompt_base: str, modelo: str) -> Optional[Dict]:
    """Genera meta-análisis completo para un TSR"""
    
    print(f"\n[INFO] Generando meta-análisis TSR{datos_tsr['tsr_id']} con modelo {modelo}...")
    
    # Construir prompt específico
    prompt = construir_prompt_metaanalisis(datos_tsr, prompt_base)
    
    # Seleccionar API según modelo
    if modelo == "minimax":
        resultado = api_opencode_minimax(prompt)
    else:
        resultado = api_perplexity(prompt, modelo)
    
    if not resultado:
        print(f"[ERROR] Falló generación de meta-análisis TSR{datos_tsr['tsr_id']}")
        return None
    
    # Validar extensión
    valido, palabras = validar_extension(resultado, 800, 1200)
    if not valido:
        print(f"[WARNING] Meta-análisis TSR{datos_tsr['tsr_id']} con {palabras} palabras (fuera de rango 800-1200)")
    
    return {
        "tsr_id": datos_tsr['tsr_id'],
        "concepto_principal": datos_tsr['concepto_principal'],
        "metaanalisis": resultado,
        "estadisticas": {
            "palabras": palabras,
            "modelo_usado": modelo,
            "fecha_generacion": datetime.now().isoformat(),
            "validacion_extension": valido
        },
        "patrones_identificados": [],  # Se podría extraer automáticamente
        "tensiones_sintetizadas": [],  # Se podría extraer automáticamente
        "estructuras_epistemologicas": []  # Se podría extraer automáticamente
    }

# ============================================================================
# PROCESAMIENTO POR LOTES
# ============================================================================

def procesar_lote(tsr_ids: List[int], capas_data: Tuple, prompt_base: str, modelo: str) -> Dict:
    """Procesa un lote de TSRs para meta-análisis"""
    
    resultados = {}
    
    for tsr_id in tsr_ids:
        print(f"\n[PROCESO] TSR{tsr_id} - Meta-análisis conceptual...")
        
        # Extraer datos consolidados
        datos_tsr = extraer_datos_tsr(tsr_id, *capas_data)
        
        # Generar meta-análisis
        resultado = generar_metaanalisis_tsr(datos_tsr, prompt_base, modelo)
        
        if resultado:
            resultados[str(tsr_id)] = resultado
            print(f"[ÉXITO] TSR{tsr_id} meta-análisis generado ({resultado['estadisticas']['palabras']} palabras)")
        else:
            print(f"[ERROR] TSR{tsr_id} falló en meta-análisis")
        
        # Pequeña pausa entre TSRs
        time.sleep(1)
    
    return resultados

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generador CAPA 5: Meta-análisis Conceptual")
    parser.add_argument("--modelo", choices=["sonar", "sonar-pro", "minimax"], 
                       default="minimax", help="Modelo a usar")
    parser.add_argument("--tsr", type=int, help="TSR específico a procesar")
    parser.add_argument("--all", action="store_true", help="Procesar todos los TSRs")
    parser.add_argument("--rango", nargs=2, type=int, metavar=("INICIO", "FIN"),
                       help="Rango de TSRs (ej: --rango 101 105)")
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not any([args.tsr, args.all, args.rango]):
        parser.error("Debe especificar --tsr, --all o --rango")
    
    # Verificar API keys
    if args.modelo == "minimax":
        print("[INFO] Usando OpenCode MiniMax M2.5-free (sin API key requerida)")
    elif args.modelo != "minimax" and not PERPLEXITY_API_KEY:
        print("[ERROR] Para usar Perplexity, configure PERPLEXITY_API_KEY")
        return
    
    # Cargar datos de capas anteriores
    print("[INFO] Cargando datos de capas anteriores...")
    capa1_data = cargar_json(CAPA1_PATH)
    capa2_data = cargar_json(CAPA2_PATH)
    capa3_data = cargar_json(CAPA3_PATH)
    capa4_data = cargar_json(CAPA4_PATH)
    
    if not all([capa1_data, capa2_data, capa3_data, capa4_data]):
        print("[ERROR] Faltan datos de capas anteriores")
        return
    
    # Cargar prompt base
    prompt_base = cargar_texto(PROMPT_PATH) or """
    Realiza un meta-análisis conceptual profundo de los datos proporcionados.
    Enfócate en identificar patrones, sintetizar tensiones y revelar estructuras
    epistemológicas subyacentes sin forzar resoluciones.
    """
    
    # Determinar TSRs a procesar
    if args.tsr:
        tsr_ids = [args.tsr]
    elif args.rango:
        tsr_ids = list(range(args.rango[0], args.rango[1] + 1))
    else:  # --all
        tsr_ids = list(range(101, 121))  # TSR100-120
    
    # Crear directorio de salida
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    
    # Procesar TSRs
    print(f"[INFO] Iniciando meta-análisis de {len(tsr_ids)} TSRs con modelo {args.modelo}...")
    
    capas_data = (capa1_data, capa2_data, capa3_data, capa4_data)
    resultados = procesar_lote(tsr_ids, capas_data, prompt_base, args.modelo)
    
    # Cargar resultados existentes si hay
    resultados_existentes = {}
    if OUTPUT_JSON.exists():
        resultados_existentes = cargar_json(OUTPUT_JSON) or {}
    
    # Combinar resultados
    resultados_existentes.update(resultados)
    
    # Guardar resultados
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(resultados_existentes, f, indent=2, ensure_ascii=False)
    
    # Resumen final
    print(f"\n[RESUMEN] Meta-análisis completado:")
    print(f"- TSRs procesados: {len(resultados)}/{len(tsr_ids)}")
    print(f"- Resultados guardados en: {OUTPUT_JSON}")
    print(f"- Total TSRs en archivo: {len(resultados_existentes)}")
    
    # Mostrar TSRs fallidos
    fallidos = set(tsr_ids) - set(int(k) for k in resultados.keys())
    if fallidos:
        print(f"- TSRs fallidos: {sorted(fallidos)}")

if __name__ == "__main__":
    main()
