#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR CAPA 6: GUIONES DE TALLER — APLICACIÓN PEDAGÓGICA OPERATIVA
Sistema modular de 7 capas para Cíclope: Mitologías Verbales

Genera guiones de taller ejecutables (300-500 palabras) que operativizan
los conceptos de cada TSR en 3 contextos: docencia, mediación de lectura,
gestión cultural. Incluye evaluación de segundo orden (proceso, no resultado).

Dependencias: CAPA2 (genealogía) + CAPA3 (problematización) + CAPA5 (meta-análisis)
Secundarias:  CAPA1 (bibliografía, para datos de autor/obra) + CAPA4 (resonancias, opcional)

Lecciones de CAPA5 aplicadas:
- Triple cliente API (MiniMax directo, Perplexity fallback, OpenCode subprocess)
- Retry con backoff exponencial (sin random — arreglado de CAPA5)
- Post-procesamiento duro: truncamiento, filtrado artefactos multilingües
- Salida dual: JSON + .md por TSR (como CAPA5)

Uso:
    python scripts/generar_capa6.py --modelo minimax --all
    python scripts/generar_capa6.py --modelo minimax --tsr 102
    python scripts/generar_capa6.py --modelo sonar --rango 115 120
    python scripts/generar_capa6.py --modelo opencode --all
"""

import os
import sys
import re
import json
import time
import argparse
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
GLOSARIO_PATH = BASE_DIR / "config" / "GLOSARIO_CICLOPE.json"
CAPA1_PATH = BASE_DIR / "capas" / "CAPA1_bibliografia" / "TSR_CAPA1_FINAL.json"
CAPA2_PATH = BASE_DIR / "capas" / "CAPA2_genealogia" / "TSR_CAPA2_FINAL_CONSOLIDADO.json"
CAPA3_PATH = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"
CAPA4_PATH = BASE_DIR / "capas" / "CAPA4_resonancias" / "TSR_CAPA4_FINAL.json"
CAPA5_PATH = BASE_DIR / "capas" / "CAPA5_metanalisis" / "TSR_CAPA5_FINAL.json"
PROMPT_PATH = BASE_DIR / "config" / "PROMPTS_POR_CAPA" / "CAPA6_prompt.txt"
OUTPUT_DIR = BASE_DIR / "capas" / "CAPA6_talleres"
OUTPUT_JSON = OUTPUT_DIR / "TSR_CAPA6_FINAL.json"

# API Keys desde entorno
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")

# Constantes de validación
MIN_PALABRAS = 300
MAX_PALABRAS = 500
# Rango real de MiniMax (observado en CAPA5: tiende a 600-800)
MIN_PALABRAS_FLEX = 250
MAX_PALABRAS_FLEX = 600

# ============================================================================
# POST-PROCESAMIENTO: FILTRADO DE ARTEFACTOS
# Lección CAPA5: MiniMax sangra caracteres chinos/rusos del thinking interno
# ============================================================================

def filtrar_artefactos_multilingues(texto: str) -> str:
    """
    Filtra artefactos multilingües del thinking interno del modelo.
    Mantiene español, portugués, inglés, alemán, francés, italiano, latín.
    Elimina caracteres CJK, cirílicos, y secuencias no-Latin sospechosas.
    """
    patron_no_latin = re.compile(
        r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF\u00A1\u00A9\u00AB\u00AE\u00B0'
        r'\u00BB\u00BF\u2010-\u2027\u2030-\u205E\u2070-\u209F\u20A0-\u20CF'
        r'\u2100-\u214F\u2190-\u21FF\u2200-\u22FF\u2300-\u23FF\u25A0-\u25FF'
        r'\u2600-\u26FF\u2700-\u27BF\s\n\r\t.,;:!?\'"()\[\]{}\-–—/<>@#$%^&*+=|~`]'
    )
    
    lineas = texto.split('\n')
    lineas_filtradas = []
    
    for linea in lineas:
        artefactos = patron_no_latin.findall(linea)
        if len(artefactos) > 3:
            continue
        if artefactos:
            linea = patron_no_latin.sub('', linea)
        lineas_filtradas.append(linea)
    
    return '\n'.join(lineas_filtradas)


def truncar_palabras(texto: str, max_palabras: int = MAX_PALABRAS) -> str:
    """
    Trunca el texto al máximo de palabras respetando estructura Markdown.
    Si un párrafo excede el límite, lo corta a nivel de palabras con elipsis.
    """
    palabras = texto.split()
    if len(palabras) <= max_palabras:
        return texto
    
    lineas = texto.split('\n')
    resultado = []
    conteo = 0
    
    for linea in lineas:
        palabras_linea = linea.split()
        palabras_faltantes = max_palabras - conteo
        
        if palabras_faltantes <= 0:
            break
        
        if len(palabras_linea) <= palabras_faltantes:
            resultado.append(linea)
            conteo += len(palabras_linea)
        else:
            resultado.append(' '.join(palabras_linea[:palabras_faltantes]) + '...')
            conteo += palabras_faltantes
            break
    
    texto_truncado = '\n'.join(resultado)
    
    if conteo < len(palabras) * 0.9:
        texto_truncado += f"\n\n> [Nota: texto truncado a {conteo} palabras del original {len(palabras)}]"
    
    return texto_truncado


def postprocesar(texto: str) -> Tuple[str, Dict]:
    """
    Pipeline completo de post-procesamiento del output del modelo.
    Returns: (texto_procesado, metadata_procesamiento)
    """
    metadata = {
        "palabras_originales": len(texto.split()),
        "artefactos_filtrados": False,
        "truncado": False
    }
    
    # Paso 1: Filtrar artefactos multilingües
    texto_limpio = filtrar_artefactos_multilingues(texto)
    if len(texto_limpio) != len(texto):
        metadata["artefactos_filtrados"] = True
    
    # Paso 2: Truncar si excede máximo flexible
    palabras_post = len(texto_limpio.split())
    if palabras_post > MAX_PALABRAS_FLEX:
        texto_limpio = truncar_palabras(texto_limpio, MAX_PALABRAS)
        metadata["truncado"] = True
    
    metadata["palabras_finales"] = len(texto_limpio.split())
    
    return texto_limpio, metadata


# ============================================================================
# CONFIGURACIÓN DE RETRY CON BACKOFF EXPONENCIAL
# Sin random — arreglado de CAPA5 (random.uniform causaba no-determinismo)
# ============================================================================

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    """Decorador para reintentos con backoff exponencial determinista."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        print(f"[ERROR] Máximo de reintentos alcanzado ({retries})")
                        raise e
                    sleep_time = backoff_in_seconds * (2 ** attempt)
                    print(f"[RETRY] Intento {attempt+1}/{retries} falló. "
                          f"Reintentando en {sleep_time}s... Error: {str(e)[:80]}")
                    time.sleep(sleep_time)
                    attempt += 1
        return wrapper
    return decorator


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def cargar_json(path: Path) -> Optional[Dict]:
    """Carga archivo JSON con manejo de errores"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] Archivo no encontrado: {path}")
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
        return None


def validar_extension(texto: str, min_pal: int, max_pal: int) -> Tuple[bool, int, str]:
    """
    Valida extensión con 3 niveles:
    - 'ok': dentro de rango objetivo
    - 'flexible': fuera de objetivo pero en rango aceptable
    - 'fuera': necesita revisión manual
    """
    palabras = len(texto.split())
    if min_pal <= palabras <= max_pal:
        return True, palabras, 'ok'
    elif MIN_PALABRAS_FLEX <= palabras <= MAX_PALABRAS_FLEX:
        return False, palabras, 'flexible'
    else:
        return False, palabras, 'fuera'


# ============================================================================
# EXTRACTOR DE DATOS POR TSR
# Adapta las 5 estructuras JSON distintas del pipeline
# ============================================================================

def extraer_datos_tsr(tsr_id: int,
                      capa1: Optional[Dict],
                      capa2: Optional[Dict],
                      capa3: Optional[Dict],
                      capa4: Optional[Dict],
                      capa5: Optional[Dict]) -> Dict:
    """
    Extrae y consolida datos de todas las capas para un TSR específico.
    
    Estructuras conocidas:
    - CAPA1: clusters -> {cluster_name: [{tsr, titulo, fuentes, ...}, ...]}
    - CAPA2: dict directo por TSR ID -> {"102": {contenido, titulo, autor, obra, ...}}
    - CAPA3: {estructura: [{tsr, problematizacion, ...}, ...]}
    - CAPA4: {estructura: [{tsr, resonancias, ...}, ...]} o {metadata, estructura}
    - CAPA5: dict directo por TSR ID -> {"102": {metaanalisis, estadisticas, ...}}
    """
    datos = {"tsr_id": tsr_id}
    tsr_str = str(tsr_id)
    
    # --- CAPA1: Bibliografía (estructura anidada por clusters) ---
    bibliografia = {}
    if capa1:
        clusters = capa1.get("clusters", {})
        for cluster_name, tsrs in clusters.items():
            for tsr in tsrs:
                if tsr.get("tsr") == tsr_str:
                    bibliografia = {
                        "titulo": tsr.get("titulo", ""),
                        "autores_clave": [f.get("autor", "") for f in tsr.get("fuentes", []) if f.get("autor")],
                        "obras_clave": [f.get("titulo", "") for f in tsr.get("fuentes", []) if f.get("titulo")][:3],
                        "cluster": cluster_name
                    }
                    break
            if bibliografia:
                break
    datos["bibliografia"] = bibliografia
    
    # --- CAPA2: Genealogía (dict directo) ---
    genealogia = {}
    if capa2 and tsr_str in capa2:
        tsr_data = capa2[tsr_str]
        contenido = tsr_data.get("contenido", "")
        genealogia = {
            "titulo": tsr_data.get("titulo", ""),
            "autor": tsr_data.get("autor", ""),
            "obra": tsr_data.get("obra", ""),
            "año": tsr_data.get("año", ""),
            "concepto_central": tsr_data.get("concepto_central", ""),
            "cluster": tsr_data.get("cluster", ""),
            "keywords": tsr_data.get("keywords", []),
            "conexion_RH": tsr_data.get("conexion_RH", ""),
            "resumen": (contenido[:400] + "..." + contenido[-200:]) if len(contenido) > 600 else contenido
        }
    elif capa2 and isinstance(capa2.get("estructura"), list):
        for item in capa2["estructura"]:
            if str(item.get("tsr", item.get("tsr_id", ""))) == tsr_str:
                contenido = item.get("genealogia", item.get("contenido", ""))
                genealogia = {
                    "titulo": item.get("titulo", ""),
                    "autor": item.get("autor", ""),
                    "obra": item.get("obra", ""),
                    "año": item.get("año", ""),
                    "concepto_central": item.get("concepto_central", ""),
                    "resumen": (contenido[:400] + "..." + contenido[-200:]) 
                if len(contenido) > 600 else contenido
                }
                break
    datos["genealogia"] = genealogia
    
    # --- CAPA3: Problematización (estructura como array) ---
    problematizacion = ""
    if capa3 and isinstance(capa3, dict):
        items = capa3.get("estructura", [])
        if not items and tsr_str in capa3:
            problematizacion = capa3[tsr_str].get("problematizacion", "")
        for item in items:
            if str(item.get("tsr", item.get("tsr_id", ""))) == tsr_str:
                problematizacion = item.get("problematizacion", "")
                break
    datos["problematizacion"] = problematizacion[:600] if problematizacion else ""
    
    # --- CAPA4: Resonancias (estructura como array, opcional) ---
    resonancias = ""
    if capa4 and isinstance(capa4, dict):
        items = capa4.get("estructura", [])
        if not items and tsr_str in capa4:
            resonancias = capa4[tsr_str].get("resonancias", "")
        for item in items:
            if str(item.get("tsr", item.get("tsr_id", ""))) == tsr_str:
                resonancias = item.get("resonancias", "")
                break
    datos["resonancias"] = resonancias[:300] if resonancias else ""
    
    # --- CAPA5: Meta-análisis (dict directo) ---
    metaanalisis = ""
    if capa5 and tsr_str in capa5:
        metaanalisis = capa5[tsr_str].get("metaanalisis", "")
        datos["concepto_principal_capa5"] = capa5[tsr_str].get("concepto_principal", "")
    datos["metaanalisis"] = metaanalisis[:500] if metaanalisis else ""
    
    return datos


# ============================================================================
# CLIENTES API — TRIPLE CLIENTE
# ============================================================================

@retry_with_backoff(retries=3)
def api_perplexity(prompt: str, model="sonar") -> Optional[str]:
    """Cliente para API de Perplexity (Sonar / Sonar Pro)"""
    if not PERPLEXITY_API_KEY:
        print("[ERROR] PERPLEXITY_API_KEY no configurada")
        return None
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    model_name = f"llama-3.1-{model}-70b-online"
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "Eres un diseñador pedagógico experto en teoría crítica. Respondes SOLO en español."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.65,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] API Perplexity ({model_name}): {str(e)}")
        return None


@retry_with_backoff(retries=3)
def api_minimax(prompt: str, model="minimax-text-01") -> Optional[str]:
    """Cliente para API de MiniMax directo"""
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
        "messages": [
            {"role": "system", "content": "Eres un diseñador pedagógico experto en teoría crítica. Respondes SOLO en español. Genera guiones de taller operativos."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] API MiniMax: {str(e)}")
        return None


def api_opencode_minimax(prompt: str) -> Optional[str]:
    """Cliente para OpenCode MiniMax M2.5-free (vía subprocess)"""
    try:
        cmd = [
            "opencode", "--model", "opencode/minimax-m2.5-free",
            "run", prompt
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
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
            
            output = '\n'.join(response_lines) if response_lines else result.stdout
            
            if len(output.strip()) < 50:
                print(f"[WARN] OpenCode respuesta sospechosamente corta: {len(output)} chars")
                return None
            
            return output
        else:
            print(f"[ERROR] OpenCode exit code {result.returncode}: {result.stderr[:100]}")
            return None
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout en OpenCode (120s)")
        return None
    except FileNotFoundError:
        print("[ERROR] 'opencode' no encontrado en PATH. ¿Estás en WSL?")
        return None
    except Exception as e:
        print(f"[ERROR] OpenCode: {str(e)}")
        return None


def llamar_api(prompt: str, modelo: str) -> Optional[str]:
    """
    Despacha al cliente API correcto según modelo seleccionado.
    Estrategia de fallback: si el modelo primario falla, intenta con secundario.
    """
    if modelo == "opencode":
        return api_opencode_minimax(prompt)
    elif modelo == "minimax":
        resultado = api_minimax(prompt)
        if not resultado and PERPLEXITY_API_KEY:
            print("[FALLBACK] MiniMax falló, intentando Perplexity Sonar...")
            resultado = api_perplexity(prompt, "sonar")
        return resultado
    elif modelo in ("sonar", "sonar-pro"):
        resultado = api_perplexity(prompt, modelo)
        if not resultado and MINIMAX_API_KEY:
            print("[FALLBACK] Perplexity falló, intentando MiniMax...")
            resultado = api_minimax(prompt)
        return resultado
    else:
        print(f"[ERROR] Modelo no reconocido: {modelo}")
        return None


# ============================================================================
# CONSTRUCTOR DE PROMPT
# ============================================================================

def construir_prompt_taller(datos_tsr: Dict, prompt_base: str) -> str:
    """
    Construye el prompt final para generación del guion de taller.
    Inyecta datos de CAPA2 (genealogía), CAPA3 (problematización), CAPA5 (meta-análisis).
    """
    tsr_id = datos_tsr["tsr_id"]
    
    gen = datos_tsr.get("genealogia", {})
    titulo = gen.get("titulo", datos_tsr.get("bibliografia", {}).get("titulo", f"TSR{tsr_id}"))
    autor = gen.get("autor", "")
    obra = gen.get("obra", "")
    concepto = gen.get("concepto_central", "")
    keywords = gen.get("keywords", [])
    
    genealogia_texto = ""
    if gen.get("resumen"):
        genealogia_texto = (
            f"Autor principal: {autor}. Obra: {obra}. "
            f"Concepto central: {concepto}. "
            f"Keywords: {', '.join(keywords[:5])}. "
            f"Resumen genealógico: {gen['resumen']}"
        )
    
    problem_texto = datos_tsr.get("problematizacion", "") or "No disponible"
    meta_texto = datos_tsr.get("metaanalisis", "") or "No disponible"
    
    glosario_texto = "Términos canónicos: fragmento (Schlegel vs Blanchot), aura (Benjamin), autor (Barthes/Foucault/Eco), archivo (Foucault/Derrida), episteme (Foucault), glitch (error como método)."
    
    prompt_final = prompt_base
    prompt_final = prompt_final.replace("{TSR_ID}", str(tsr_id))
    prompt_final = prompt_final.replace("{TITULO}", titulo)
    prompt_final = prompt_final.replace("{GENEALOGIA_CAPA2}", genealogia_texto)
    prompt_final = prompt_final.replace("{PROBLEMATIZACION_CAPA3}", problem_texto[:500])
    prompt_final = prompt_final.replace("{METAANALISIS_CAPA5}", meta_texto[:400])
    prompt_final = prompt_final.replace("{GLOSARIO_TERMINOS}", glosario_texto)
    
    return prompt_final


# ============================================================================
# GENERACIÓN DE GUIONES
# ============================================================================

def generar_guion_tsr(datos_tsr: Dict, prompt_base: str, modelo: str) -> Optional[Dict]:
    """
    Genera el guion de taller completo para un TSR.
    Incluye: llamada API, post-procesamiento, validación, salida dual (JSON + .md).
    """
    tsr_id = datos_tsr["tsr_id"]
    
    print(f"\n{'='*60}")
    print(f"[INFO] Generando guion de taller TSR{tsr_id} con modelo {modelo}...")
    print(f"{'='*60}")
    
    if not datos_tsr.get("genealogia") and not datos_tsr.get("bibliografia"):
        print(f"[ERROR] TSR{tsr_id}: sin datos de genealogía ni bibliografía. Saltando.")
        return None
    
    prompt = construir_prompt_taller(datos_tsr, prompt_base)
    resultado_raw = llamar_api(prompt, modelo)
    
    if not resultado_raw:
        print(f"[ERROR] TSR{tsr_id}: la API no devolvió contenido")
        return None
    
    resultado_limpio, metadata_pp = postprocesar(resultado_raw)
    
    valido, palabras, nivel = validar_extension(resultado_limpio, MIN_PALABRAS, MAX_PALABRAS)
    
    if nivel == 'ok':
        print(f"[OK] TSR{tsr_id}: {palabras} palabras (rango objetivo)")
    elif nivel == 'flexible':
        print(f"[WARN] TSR{tsr_id}: {palabras} palabras (fuera de objetivo pero aceptable)")
    else:
        print(f"[ALERTA] TSR{tsr_id}: {palabras} palabras (FUERA DE RANGO — requiere revisión manual)")
    
    if metadata_pp["artefactos_filtrados"]:
        print(f"[POST-PROC] TSR{tsr_id}: artefactos multilingües filtrados")
    if metadata_pp["truncado"]:
        print(f"[POST-PROC] TSR{tsr_id}: texto truncado de {metadata_pp['palabras_originales']} a {metadata_pp['palabras_finales']} palabras")
    
    titulo_tsr = datos_tsr.get("genealogia", {}).get("titulo", f"TSR{tsr_id}")
    md_path = OUTPUT_DIR / f"TSR{tsr_id}_GUION_TALLER.md"
    
    contenido_md = f"""# GUIÓN DE TALLER: TSR{tsr_id}

## {titulo_tsr}

**Proyecto:** Cíclope · Mitologías Verbales
**Fecha de generación:** {datetime.now().strftime('%d.%m.%Y')}
**Modelo:** {modelo}
**Palabras:** {palabras}
**Validación:** {nivel}

---

{resultado_limpio}

---

*Generado por Cíclope CAPA6 · Sistema de Guiones de Taller*
*Proyecto Cíclope · Mitologías Verbales · 2026*
"""
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(contenido_md)
    print(f"[GUARDADO] TSR{tsr_id}: {md_path}")
    
    return {
        "tsr_id": tsr_id,
        "titulo": titulo_tsr,
        "guion_taller": resultado_limpio,
        "estadisticas": {
            "palabras": palabras,
            "modelo_usado": modelo,
            "fecha_generacion": datetime.now().isoformat(),
            "validacion_extension": nivel,
            "postprocesamiento": metadata_pp
        },
        "metadata_entrada": {
            "genealogia_disponible": bool(datos_tsr.get("genealogia")),
            "problematizacion_disponible": bool(datos_tsr.get("problematizacion")),
            "metaanalisis_disponible": bool(datos_tsr.get("metaanalisis")),
            "autor_principal": datos_tsr.get("genealogia", {}).get("autor", ""),
            "concepto_central": datos_tsr.get("genealogia", {}).get("concepto_central", "")
        }
    }


# ============================================================================
# PROCESAMIENTO POR LOTES
# ============================================================================

def procesar_lote(tsr_ids: List[int],
                  capa1: Optional[Dict],
                  capa2: Optional[Dict],
                  capa3: Optional[Dict],
                  capa4: Optional[Dict],
                  capa5: Optional[Dict],
                  prompt_base: str,
                  modelo: str) -> Tuple[Dict, List]:
    """Procesa un lote de TSRs generando guiones de taller"""
    
    resultados = {}
    fallidos = []
    
    for i, tsr_id in enumerate(tsr_ids, 1):
        print(f"\n[PROGRESO] {i}/{len(tsr_ids)} — TSR{tsr_id}")
        
        datos_tsr = extraer_datos_tsr(tsr_id, capa1, capa2, capa3, capa4, capa5)
        resultado = generar_guion_tsr(datos_tsr, prompt_base, modelo)
        
        if resultado:
            resultados[str(tsr_id)] = resultado
        else:
            fallidos.append(tsr_id)
        
        if i < len(tsr_ids):
            time.sleep(2)
    
    return resultados, fallidos


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generador CAPA 6: Guiones de Taller — Aplicación Pedagógica Operativa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/generar_capa6.py --modelo minimax --all
  python scripts/generar_capa6.py --modelo opencode --all
  python scripts/generar_capa6.py --modelo sonar --tsr 102
  python scripts/generar_capa6.py --modelo minimax --rango 115 120
        """
    )
    parser.add_argument("--modelo", 
                        choices=["sonar", "sonar-pro", "minimax", "opencode"],
                        default="minimax",
                        help="Modelo a usar (default: minimax)")
    parser.add_argument("--tsr", type=int, 
                        help="TSR específico a procesar (ej: 102)")
    parser.add_argument("--all", action="store_true", 
                        help="Procesar todos los TSRs (102-120)")
    parser.add_argument("--rango", nargs=2, type=int, metavar=("INICIO", "FIN"),
                        help="Rango de TSRs (ej: --rango 115 120)")
    parser.add_argument("--no-postproc", action="store_true",
                        help="Desactivar post-procesamiento (truncamiento + filtrado)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar datos que se usarían sin llamar a la API")
    
    args = parser.parse_args()
    
    if not any([args.tsr, args.all, args.rango]):
        parser.error("Debe especificar --tsr, --all o --rango")
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           CÍCLOPE · CAPA 6: GUIONES DE TALLER              ║
║           Sistema de Generación Automatizada                ║
║           {datetime.now().strftime('%d.%m.%Y %H:%M')}                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # CARGA DE DATOS
    print("[INFO] Cargando datos de capas anteriores...")
    
    capa1 = cargar_json(CAPA1_PATH)
    capa2 = cargar_json(CAPA2_PATH)
    capa3 = cargar_json(CAPA3_PATH)
    capa4 = cargar_json(CAPA4_PATH)
    capa5 = cargar_json(CAPA5_PATH)
    
    print(f"  CAPA1 (bibliografía):    {'✓' if capa1 else '✗'}")
    print(f"  CAPA2 (genealogía):      {'✓' if capa2 else '✗'} [REQUERIDA]")
    print(f"  CAPA3 (problematización): {'✓' if capa3 else '✗'} [REQUERIDA]")
    print(f"  CAPA4 (resonancias):     {'✓' if capa4 else '✗'} [opcional]")
    print(f"  CAPA5 (meta-análisis):   {'✓' if capa5 else '✗'} [recomendada]")
    
    if not capa2:
        print("[ERROR CRÍTICO] CAPA2 (genealogía) es requerida. Abortando.")
        sys.exit(1)
    if not capa3:
        print("[ERROR CRÍTICO] CAPA3 (problematización) es requerida. Abortando.")
        sys.exit(1)
    
    glosario = cargar_json(GLOSARIO_PATH)
    print(f"  GLOSARIO:                {'✓' if glosario else '✗'}")
    
    prompt_base = cargar_texto(PROMPT_PATH)
    if not prompt_base:
        print("[WARN] CAPA6_prompt.txt está vacío o no existe. Usando prompt embebido.")
        prompt_base = _prompt_embebido()
    else:
        print(f"  PROMPT CAPA6:            ✓ ({len(prompt_base)} chars)")
    
    # DETERMINAR TSRs
    if args.tsr:
        tsr_ids = [args.tsr]
    elif args.rango:
        tsr_ids = list(range(args.rango[0], args.rango[1] + 1))
    else:
        tsr_ids = list(range(102, 121))
    
    print(f"\n[INFO] TSRs a procesar: {len(tsr_ids)} ({tsr_ids[0]}-{tsr_ids[-1]})")
    print(f"[INFO] Modelo: {args.modelo}")
    
    # DRY RUN
    if args.dry_run:
        print("\n[DRY RUN] Mostrando datos que se usarían para cada TSR:\n")
        for tsr_id in tsr_ids:
            datos = extraer_datos_tsr(tsr_id, capa1, capa2, capa3, capa4, capa5)
            gen = datos.get("genealogia", {})
            print(f"  TSR{tsr_id}: {gen.get('titulo', 'SIN TÍTULO')}")
            print(f"    Autor: {gen.get('autor', 'N/A')}")
            print(f"    Concepto: {gen.get('concepto_central', 'N/A')}")
            print(f"    Genealogía: {'✓' if gen else '✗'}")
            print(f"    Problematización: {'✓' if datos.get('problematizacion') else '✗'}")
            print(f"    Meta-análisis: {'✓' if datos.get('metaanalisis') else '✗'}")
            print()
        return
    
    # VERIFICAR API
    if args.modelo == "opencode":
        print("[INFO] Usando OpenCode MiniMax M2.5-free (sin API key requerida)")
    elif args.modelo == "minimax":
        if not MINIMAX_API_KEY:
            print("[WARN] MINIMAX_API_KEY no configurada. Se usará fallback a Perplexity si falla.")
        else:
            print("[INFO] MINIMAX_API_KEY detectada ✓")
    else:
        if not PERPLEXITY_API_KEY:
            print("[WARN] PERPLEXITY_API_KEY no configurada. Se usará fallback a MiniMax si falla.")
        else:
            print("[INFO] PERPLEXITY_API_KEY detectada ✓")
    
    # CREAR DIRECTORIO DE SALIDA
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Directorio de salida: {OUTPUT_DIR}")
    
    # PROCESAR
    if args.no_postproc:
        print("[INFO] Post-procesamiento DESACTIVADO (--no-postproc)")
    
    print(f"\n[INFO] Iniciando generación de {len(tsr_ids)} guiones de taller...")
    
    resultados, fallidos = procesar_lote(
        tsr_ids, capa1, capa2, capa3, capa4, capa5,
        prompt_base, args.modelo
    )
    
    # GUARDAR JSON CONSOLIDADO
    resultados_existentes = {}
    if OUTPUT_JSON.exists():
        resultados_existentes = cargar_json(OUTPUT_JSON) or {}
    
    resultados_existentes.update(resultados)
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(resultados_existentes, f, indent=2, ensure_ascii=False)
    
    # RESUMEN
    total = len(resultados_existentes)
    print(f"\n{'='*60}")
    print(f"[RESUMEN] Generación de guiones CAPA6 completada")
    print(f"{'='*60}")
    print(f"  TSRs procesados esta ejecución: {len(resultados)}/{len(tsr_ids)}")
    print(f"  Total TSRs en archivo JSON:     {total}")
    print(f"  Archivos .md generados:          {len(resultados)}")
    print(f"  Archivo JSON consolidado:        {OUTPUT_JSON}")
    
    if fallidos:
        print(f"\n  TSRs FALLIDOS: {fallidos}")
        print(f"  → Para reintentar: python scripts/generar_capa6.py --modelo {args.modelo} --tsr {' '.join(str(f) for f in fallidos)}")
    
    ok_count = sum(1 for r in resultados.values() 
                   if r["estadisticas"]["validacion_extension"] == "ok")
    flex_count = sum(1 for r in resultados.values() 
                     if r["estadisticas"]["validacion_extension"] == "flexible")
    alert_count = sum(1 for r in resultados.values() 
                      if r["estadisticas"]["validacion_extension"] == "fuera")
    
    print(f"\n[CALIDAD]")
    print(f"  ✓ En rango objetivo ({MIN_PALABRAS}-{MAX_PALABRAS}):  {ok_count}")
    print(f"  ~ Fuera pero aceptable:                            {flex_count}")
    print(f"  ✗ Requieren revisión manual:                       {alert_count}")


def _prompt_embebido():
    """Prompt de emergencia si CAPA6_prompt.txt no existe"""
    return """Genera un guion de taller de 300-500 palabras para TSR{TSR_ID}.

El taller debe tener:
- Título provocador
- 3 módulos: Docencia, Mediación de lectura, Gestión cultural
- Actividades ejecutables con pasos concretos
- Evaluación de segundo orden (observar el proceso, no el resultado)
- Cierre con 3 preguntas abiertas

Datos del TSR:
Genealogía: {GENEALOGIA_CAPA2}
Problematización: {PROBLEMATIZACION_CAPA3}
Meta-análisis: {METAANALISIS_CAPA5}

Tono: institucional, exigente. No marketero. Sin emojis. Sin KPIs."""


if __name__ == "__main__":
    main()