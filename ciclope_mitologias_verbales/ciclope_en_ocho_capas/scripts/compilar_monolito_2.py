#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPILADOR MONOLITO: REDACCIÓN FINAL DE TSRs COMPLETOS
Sistema modular de 7 capas para Cíclope: Mitologías Verbales

Toma las 7 capas (CAPA0-CAPA7) y genera documentos TSR finales redactados
como monolitos unitarios. Ya no son capas separadas: cada TSR es un texto
autónomo de 2,500-4,000 palabras que funciona sin necesidad del Cíclope.

Dependencias: Todas las capas (CAPA0-CAPA7)
CAPA0: Semilla (Markdown)
CAPA1: Bibliografía (JSON, clusters)
CAPA2: Genealogía (JSON, dict por TSR_ID)
CAPA3: Problematización (JSON, array bajo estructura)
CAPA4: Resonancias (JSON, array bajo estructura)
CAPA5: Meta-análisis (JSON, dict por TSR_ID)
CAPA6: Guiones de Taller (JSON, dict por TSR_ID)
CAPA7: Casos de Aplicación (JSON, dict por TSR_ID)

Maneja las 3 estructuras JSON distintas del pipeline y los nombres de campo
inconsistentes entre capas.

Uso:
    python scripts/compilar_monolito.py --modelo minimax --all
    python scripts/compilar_monolito.py --modelo minimax --tsr 102
    python scripts/compilar_monolito.py --modelo opencode --rango 115 120
    python scripts/compilar_monolito.py --modelo sonar --all --no-postproc
    python scripts/compilar_monolito.py --dry-run  # Solo audit, sin llamar API
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
from typing import Dict, Optional, List, Tuple, Any

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
CAPA0_PATH = BASE_DIR / "capas" / "CAPA0_semilla" / "CAPA0_TSR101-120QUOTES.md"
CAPA1_PATH = BASE_DIR / "capas" / "CAPA1_bibliografia" / "TSR_CAPA1_FINAL.json"
CAPA2_PATH = BASE_DIR / "capas" / "CAPA2_genealogia" / "TSR_CAPA2_FINAL_CONSOLIDADO.json"
CAPA3_PATH = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"
CAPA4_PATH = BASE_DIR / "capas" / "CAPA4_resonancias" / "TSR_CAPA4_FINAL.json"
CAPA5_PATH = BASE_DIR / "capas" / "CAPA5_metanalisis" / "TSR_CAPA5_FINAL.json"
CAPA6_PATH = BASE_DIR / "capas" / "CAPA6_talleres" / "TSR_CAPA6_FINAL.json"
CAPA7_PATH = BASE_DIR / "capas" / "CAPA7_casos" / "TSR_CAPA7_FINAL.json"
PROMPT_PATH = BASE_DIR / "config" / "PROMPTS_POR_CAPA" / "PROMPT_MONOLITO.txt"
OUTPUT_DIR = BASE_DIR / "outputs" / "TSR_MONOLITOS_V2"
OUTPUT_JSON = OUTPUT_DIR / "TSR_MONOLITOS_FINAL.json"

# API Keys
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")

# Constantes de validación
MIN_PALABRAS = 2500
MAX_PALABRAS = 4000
MIN_PALABRAS_FLEX = 2000
MAX_PALABRAS_FLEX = 5000

# TSR range objetivo
TSR_MIN = 102
TSR_MAX = 120


# ============================================================================
# EXTRACTOR DE DATOS — MANEJA LAS 3 ESTRUCTURAS JSON
# ============================================================================

def cargar_json(path: Path) -> Optional[Dict]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] No encontrado: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON inválido en {path}: {str(e)[:80]}")
        return None


def cargar_texto(path: Path) -> Optional[str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def extraer_semilla(capa0_text: Optional[str], tsr_id: int) -> str:
    """Extrae el párrafo de la semilla (CAPA0) para un TSR específico."""
    if not capa0_text:
        return "Semilla no disponible."
    
    # Buscar la sección del TSR en CAPA0
    patron = re.compile(
        rf'##\s*TSR{tsr_id}\b[^\n]*\n(.*?)(?=\n##\s*TSR|\Z)',
        re.DOTALL
    )
    match = patron.search(capa0_text)
    
    if match:
        texto = match.group(1).strip()
        return texto[:800] if len(texto) > 800 else texto
    
    return "Semilla no encontrada para este TSR."


def extraer_bibliografia(capa1: Optional[Dict], tsr_id: int) -> str:
    """Extrae fuentes bibliográficas de CAPA1 (estructura por clusters)."""
    if not capa1:
        return "Bibliografía no disponible."
    
    tsr_str = str(tsr_id)
    clusters = capa1.get("clusters", {})
    
    for cluster_name, tsrs in clusters.items():
        for tsr in tsrs:
            if tsr.get("tsr") == tsr_str:
                fuentes = tsr.get("fuentes", [])
                if not fuentes:
                    return "Sin fuentes registradas."
                
                # Formatear las primeras 10 fuentes
                refs = []
                for f in fuentes[:10]:
                    autor = f.get("autor", "")
                    titulo = f.get("titulo", "")
                    anio = f.get("año", "")
                    if autor and titulo:
                        refs.append(f"{autor}. {titulo}. {anio}.")
                
                return "\n".join(refs) if refs else "Sin fuentes con datos completos."
    
    return "Bibliografía no encontrada para este TSR."


def extraer_genealogia(capa2: Optional[Dict], tsr_id: int) -> Tuple[str, Dict]:
    """
    Extrae genealogía de CAPA2 (dict por TSR_ID).
    Campo real: 'contenido' (no 'genealogia' como esperaba el validador).
    Returns: (texto_genealogia, metadata)
    """
    metadata = {}
    tsr_str = str(tsr_id)
    
    if not capa2 or tsr_str not in capa2:
        return "Genealogía no disponible.", metadata
    
    data = capa2[tsr_str]
    texto = data.get("contenido", "")
    
    metadata = {
        "titulo": data.get("titulo", ""),
        "autor": data.get("autor", ""),
        "obra": data.get("obra", ""),
        "año": data.get("año", ""),
        "concepto_central": data.get("concepto_central", ""),
        "cluster": data.get("cluster", ""),
        "keywords": data.get("keywords", []),
        "conexion_RH": data.get("conexion_RH", "")
    }
    
    # SIN truncar — el modelo necesita contexto completo para redactar
    return texto if texto else "Sin contenido genealógico.", metadata


def extraer_problematizacion(capa3: Optional[Dict], tsr_id: int) -> str:
    """
    Extrae problematización de CAPA3 (array bajo 'estructura').
    Campo real: 'problematizacion' (coincide con validador).
    """
    if not capa3:
        return "Problematización no disponible."
    
    for item in capa3.get("estructura", []):
        # CAPA3 usa tsr como int
        if str(item.get("tsr", "")) == str(tsr_id):
            texto = item.get("problematizacion", "")
            # SIN truncar — contexto completo para redacción
            return texto if texto else "Sin contenido."
    
    return "Problematización no encontrada."


def extraer_resonancias(capa4: Optional[Dict], tsr_id: int) -> str:
    """
    Extrae resonancias de CAPA4 (array bajo 'estructura').
    Campo real: 'resonancias' (plural, no 'resonancia' singular).
    """
    if not capa4:
        return "Resonancias no disponibles."
    
    for item in capa4.get("estructura", []):
        if str(item.get("tsr", "")) == str(tsr_id):
            texto = item.get("resonancias", "")
            # SIN truncar — contexto completo para redacción
            return texto if texto else "Sin contenido."
    
    return "Resonancias no encontradas."


def extraer_metaanalisis(capa5: Optional[Dict], tsr_id: int) -> str:
    """
    Extrae meta-análisis de CAPA5 (dict por TSR_ID).
    Campo real: 'metaanalisis' (sin guion, no 'meta_analisis').
    """
    tsr_str = str(tsr_id)
    
    if not capa5 or tsr_str not in capa5:
        return "Meta-análisis no disponible."
    
    data = capa5[tsr_str]
    texto = data.get("metaanalisis", "")
    # SIN truncar — contexto completo para redacción
    return texto if texto else "Sin contenido de meta-análisis."


def extraer_guion_taller(capa6: Optional[Dict], tsr_id: int) -> str:
    """Extrae guion de taller de CAPA6 (dict por TSR_ID)."""
    tsr_str = str(tsr_id)
    
    if not capa6 or tsr_str not in capa6:
        return "Guion de taller no disponible."
    
    data = capa6[tsr_str]
    texto = data.get("guion_taller", "")
    # SIN truncar — contexto completo para redacción
    return texto if texto else "Sin contenido de taller."


def extraer_caso_aplicacion(capa7: Optional[Dict], tsr_id: int) -> str:
    """Extrae caso de aplicación de CAPA7 (dict por TSR_ID)."""
    tsr_str = str(tsr_id)
    
    if not capa7 or tsr_str not in capa7:
        return "Caso de aplicación no disponible."
    
    data = capa7[tsr_str]
    texto = data.get("caso_aplicacion", "")
    # SIN truncar — contexto completo para redacción
    return texto if texto else "Sin contenido de caso."


def extraer_tsr_completo(tsr_id: int,
                         capa0_text: Optional[str],
                         capa1: Optional[Dict],
                         capa2: Optional[Dict],
                         capa3: Optional[Dict],
                         capa4: Optional[Dict],
                         capa5: Optional[Dict],
                         capa6: Optional[Dict],
                         capa7: Optional[Dict]) -> Dict[str, str]:
    """
    Extrae y consolida todas las capas para un TSR.
    Returns: dict con campos de texto listos para inyectar en el prompt.
    """
    tsr_str = str(tsr_id)
    
    genealogia_text, genealogia_meta = extraer_genealogia(capa2, tsr_id)
    titulo = genealogia_meta.get("titulo", f"TSR{tsr_id}")
    
    # CAPA5 también tiene título — usar como fallback
    if titulo == f"TSR{tsr_id}" and capa5 and tsr_str in capa5:
        titulo = capa5[tsr_str].get("concepto_principal", titulo)
    
    datos = {
        "tsr_id": tsr_id,
        "titulo": titulo,
        "semilla": extraer_semilla(capa0_text, tsr_id),
        "bibliografia": extraer_bibliografia(capa1, tsr_id),
        "genealogia": genealogia_text,
        "problematizacion": extraer_problematizacion(capa3, tsr_id),
        "resonancias": extraer_resonancias(capa4, tsr_id),
        "metaanalisis": extraer_metaanalisis(capa5, tsr_id),
        "guion_taller": extraer_guion_taller(capa6, tsr_id),
        "caso_aplicacion": extraer_caso_aplicacion(capa7, tsr_id),
        "metadata": genealogia_meta
    }
    
    return datos


# ============================================================================
# POST-PROCESAMIENTO
# ============================================================================

def filtrar_artefactos_multilingues(texto: str) -> str:
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
    palabras = texto.split()
    if len(palabras) <= max_palabras:
        return texto
    lineas = texto.split('\n')
    resultado = []
    conteo = 0
    for linea in lineas:
        palabras_linea = linea.split()
        faltantes = max_palabras - conteo
        if faltantes <= 0:
            break
        if len(palabras_linea) <= faltantes:
            resultado.append(linea)
            conteo += len(palabras_linea)
        else:
            resultado.append(' '.join(palabras_linea[:faltantes]) + '...')
            conteo += faltantes
            break
    texto_truncado = '\n'.join(resultado)
    if conteo < len(palabras) * 0.9:
        texto_truncado += f"\n\n> [Nota: texto truncado a {conteo} palabras del original {len(palabras)}]"
    return texto_truncado


def postprocesar(texto: str) -> Tuple[str, Dict]:
    metadata = {
        "palabras_originales": len(texto.split()),
        "artefactos_filtrados": False,
        "truncado": False
    }
    texto_limpio = filtrar_artefactos_multilingues(texto)
    if len(texto_limpio) != len(texto):
        metadata["artefactos_filtrados"] = True
    palabras_post = len(texto_limpio.split())
    if palabras_post > MAX_PALABRAS_FLEX:
        texto_limpio = truncar_palabras(texto_limpio, MAX_PALABRAS)
        metadata["truncado"] = True
    metadata["palabras_finales"] = len(texto_limpio.split())
    return texto_limpio, metadata


# ============================================================================
# RETRY CON BACKOFF DETERMINISTA
# ============================================================================

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        print(f"[ERROR] Máximo reintentos ({retries}): {str(e)[:80]}")
                        raise e
                    sleep_time = backoff_in_seconds * (2 ** attempt)
                    print(f"[RETRY] Intento {attempt+1}/{retries}. Esperando {sleep_time}s...")
                    time.sleep(sleep_time)
                    attempt += 1
        return wrapper
    return decorator


# ============================================================================
# CLIENTES API — TRIPLE CLIENTE
# ============================================================================

@retry_with_backoff(retries=3)
def api_perplexity(prompt: str, model="sonar") -> Optional[str]:
    if not PERPLEXITY_API_KEY:
        return None
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": f"llama-3.1-{model}-70b-online",
        "messages": [
            {"role": "system", "content": "Eres un editor académico senior especializado en teoría crítica. Redactas SOLO en español. Generas documentos monolíticos de alta calidad."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 8192
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=180)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] Perplexity: {str(e)[:80]}")
        return None


@retry_with_backoff(retries=3)
def api_minimax(prompt: str, model="minimax-text-01") -> Optional[str]:
    if not MINIMAX_API_KEY:
        return None
    url = "https://api.minimax.chat/v1/text/chatcompletion"
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Eres un editor académico senior. Redactas SOLO en español. Documentos monolíticos de 2,500-4,000 palabras."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.45,
        "max_tokens": 8192
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=180)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] MiniMax: {str(e)[:80]}")
        return None


def api_opencode_minimax(prompt: str) -> Optional[str]:
    try:
        cmd = ["opencode", "--model", "opencode/minimax-m2.5-free", "run", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            resp = []
            capturing = False
            for line in lines:
                if '> build · minimax-m2.5-free' in line:
                    capturing = True
                    continue
                elif capturing and line.startswith('$'):
                    break
                elif capturing and line.strip():
                    resp.append(line.strip())
            output = '\n'.join(resp) if resp else result.stdout
            if len(output.strip()) < 100:
                return None
            return output
        return None
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout OpenCode (180s)")
        return None
    except FileNotFoundError:
        print("[ERROR] 'opencode' no encontrado. ¿WSL?")
        return None
    except Exception as e:
        print(f"[ERROR] OpenCode: {str(e)[:80]}")
        return None


def llamar_api(prompt: str, modelo: str) -> Optional[str]:
    if modelo == "opencode":
        return api_opencode_minimax(prompt)
    elif modelo == "minimax":
        resultado = api_minimax(prompt)
        if not resultado and PERPLEXITY_API_KEY:
            print("[FALLBACK] MiniMax → Perplexity Sonar...")
            resultado = api_perplexity(prompt, "sonar")
        return resultado
    elif modelo in ("sonar", "sonar-pro"):
        resultado = api_perplexity(prompt, modelo)
        if not resultado and MINIMAX_API_KEY:
            print("[FALLBACK] Perplexity → MiniMax...")
            resultado = api_minimax(prompt)
        return resultado
    else:
        print(f"[ERROR] Modelo no reconocido: {modelo}")
        return None


# ============================================================================
# CONSTRUCTOR DE PROMPT MONOLITO
# ============================================================================

def construir_prompt_monolito(datos_tsr: Dict, prompt_base: str) -> str:
    """Inyecta las 7 capas en el prompt maestro."""
    tsr_id = datos_tsr["tsr_id"]
    titulo = datos_tsr["titulo"]
    
    p = prompt_base
    p = p.replace("{TSR_ID}", str(tsr_id))
    p = p.replace("{TITULO}", titulo)
    p = p.replace("{SEMILLA_CAPA0}", datos_tsr["semilla"])
    p = p.replace("{BIBLIOGRAFIA_CAPA1}", datos_tsr["bibliografia"])
    p = p.replace("{GENEALOGIA_CAPA2}", datos_tsr["genealogia"])
    p = p.replace("{PROBLEMATIZACION_CAPA3}", datos_tsr["problematizacion"])
    p = p.replace("{RESONANCIAS_CAPA4}", datos_tsr["resonancias"])
    p = p.replace("{METAANALISIS_CAPA5}", datos_tsr["metaanalisis"])
    p = p.replace("{GUION_TALLER_CAPA6}", datos_tsr["guion_taller"])
    p = p.replace("{CASO_APLICACION_CAPA7}", datos_tsr["caso_aplicacion"])
    
    return p


# ============================================================================
# GENERACIÓN DE MONOLITO
# ============================================================================

def generar_monolito_tsr(datos_tsr: Dict, prompt_base: str, modelo: str,
                         no_postproc: bool = False) -> Optional[Dict]:
    tsr_id = datos_tsr["tsr_id"]
    titulo = datos_tsr["titulo"]
    
    print(f"\n{'='*70}")
    print(f"[MONOLITO] TSR{tsr_id}: {titulo}")
    print(f"{'='*70}")
    
    # Reportar disponibilidad de capas
    capas_disponibles = []
    for nombre, campo in [("CAPA0", "semilla"), ("CAPA1", "bibliografia"),
                          ("CAPA2", "genealogia"), ("CAPA3", "problematizacion"),
                          ("CAPA4", "resonancias"), ("CAPA5", "metaanalisis"),
                          ("CAPA6", "guion_taller"), ("CAPA7", "caso_aplicacion")]:
        disponible = datos_tsr[campo] not in [
            "Semilla no disponible.", "Semilla no encontrada para este TSR.",
            "Bibliografía no disponible.", "Bibliografía no encontrada para este TSR.",
            "Sin fuentes registradas.", "Sin fuentes con datos completos.",
            "Genealogía no disponible.", "Sin contenido genealógico.",
            "Problematización no disponible.", "Sin contenido.",
            "Resonancias no disponibles.", "Resonancias no encontradas.",
            "Meta-análisis no disponible.",
            "Guion de taller no disponible.", "Sin contenido de taller.",
            "Caso de aplicación no disponible.", "Sin contenido de caso."
        ]
        capas_disponibles.append((nombre, disponible))
    
    for nombre, disp in capas_disponibles:
        print(f"  {nombre}: {'✓' if disp else '✗'}")
    
    capas_ok = sum(1 for _, d in capas_disponibles if d)
    print(f"  → {capas_ok}/8 capas disponibles")
    
    # Construir prompt
    prompt = construir_prompt_monolito(datos_tsr, prompt_base)
    print(f"  Prompt: {len(prompt.split())} palabras")
    
    # Llamar API
    resultado_raw = llamar_api(prompt, modelo)
    
    if not resultado_raw:
        print(f"[ERROR] TSR{tsr_id}: sin respuesta de API")
        return None
    
    # Post-procesar
    if no_postproc:
        resultado_final = resultado_raw
        metadata_pp = {"palabras_originales": len(resultado_raw.split()),
                       "artefactos_filtrados": False, "truncado": False,
                       "palabras_finales": len(resultado_raw.split())}
    else:
        resultado_final, metadata_pp = postprocesar(resultado_raw)
    
    palabras = len(resultado_final.split())
    valido = MIN_PALABRAS <= palabras <= MAX_PALABRAS
    nivel = "ok" if valido else ("flexible" if MIN_PALABRAS_FLEX <= palabras <= MAX_PALABRAS_FLEX else "fuera")
    
    estado = "[OK]" if nivel == "ok" else f"[{'WARN' if nivel == 'flexible' else 'ALERTA'}]"
    print(f"  {estado} {palabras} palabras ({nivel})")
    
    if metadata_pp["artefactos_filtrados"]:
        print(f"  [POST-PROC] Artefactos multilingües filtrados")
    if metadata_pp["truncado"]:
        print(f"  [POST-PROC] Truncado: {metadata_pp['palabras_originales']} → {metadata_pp['palabras_finales']} palabras")
    
    # Guardar .md
    md_path = OUTPUT_DIR / f"TSR{tsr_id}_MONOLITO.md"
    contenido_md = f"""# TSR{tsr_id}: {titulo}

**Proyecto Cíclope · Mitologías Verbales**
**Sistema de Lectura de Segundo Orden (TRCO)**
**Fecha de compilación:** {datetime.now().strftime('%d.%m.%Y')}
**Modelo:** {modelo}
**Palabras:** {palabras}
**Validación:** {nivel}

---

{resultado_final}

---

*Compilado por Cíclope · Monolito TSR{tsr_id}*
*Proyecto Cíclope · Mitologías Verbales · 2026*
"""
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(contenido_md)
    print(f"  [GUARDADO] {md_path}")
    
    return {
        "tsr_id": tsr_id,
        "titulo": titulo,
        "monolito": resultado_final,
        "estadisticas": {
            "palabras": palabras,
            "modelo_usado": modelo,
            "fecha_compilacion": datetime.now().isoformat(),
            "validacion_extension": nivel,
            "postprocesamiento": metadata_pp,
            "capas_disponibles": capas_ok
        },
        "metadata_entrada": {
            **{nombre: disp for nombre, disp in capas_disponibles},
            "autor_principal": datos_tsr["metadata"].get("autor", ""),
            "concepto_central": datos_tsr["metadata"].get("concepto_central", ""),
            "cluster": datos_tsr["metadata"].get("cluster", ""),
            "keywords": datos_tsr["metadata"].get("keywords", [])
        }
    }


# ============================================================================
# PROCESAMIENTO POR LOTES
# ============================================================================

def procesar_lote(tsr_ids: List[int],
                  capa0_text: Optional[str],
                  capa1: Optional[Dict],
                  capa2: Optional[Dict],
                  capa3: Optional[Dict],
                  capa4: Optional[Dict],
                  capa5: Optional[Dict],
                  capa6: Optional[Dict],
                  capa7: Optional[Dict],
                  prompt_base: str,
                  modelo: str,
                  no_postproc: bool = False) -> Tuple[Dict, List]:
    
    resultados = {}
    fallidos = []
    
    for i, tsr_id in enumerate(tsr_ids, 1):
        print(f"\n[PROGRESO] {i}/{len(tsr_ids)} — TSR{tsr_id}")
        
        datos = extraer_tsr_completo(tsr_id, capa0_text, capa1, capa2, capa3, capa4, capa5, capa6, capa7)
        resultado = generar_monolito_tsr(datos, prompt_base, modelo, no_postproc)
        
        if resultado:
            resultados[str(tsr_id)] = resultado
        else:
            fallidos.append(tsr_id)
        
        if i < len(tsr_ids):
            time.sleep(3)  # Más pausa entre monolitos (son pesados)
    
    return resultados, fallidos


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Compilador Monolito: Redacción Final de TSRs Completos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/compilar_monolito.py --modelo minimax --all
  python scripts/compilar_monolito.py --modelo opencode --tsr 102
  python scripts/compilar_monolito.py --modelo sonar --rango 115 120
  python scripts/compilar_monolito.py --dry-run
  python scripts/compilar_monolito.py --modelo minimax --all --no-postproc
        """
    )
    parser.add_argument("--modelo",
                        choices=["sonar", "sonar-pro", "minimax", "opencode"],
                        default="minimax",
                        help="Modelo a usar (default: minimax)")
    parser.add_argument("--tsr", type=int,
                        help="TSR específico (ej: 102)")
    parser.add_argument("--all", action="store_true",
                        help="Compilar todos los TSRs (102-120)")
    parser.add_argument("--rango", nargs=2, type=int, metavar=("INICIO", "FIN"),
                        help="Rango de TSRs (ej: --rango 115 120)")
    parser.add_argument("--no-postproc", action="store_true",
                        help="Desactivar post-procesamiento")
    parser.add_argument("--dry-run", action="store_true",
                        help="Auditar datos disponibles sin llamar a la API")
    
    args = parser.parse_args()
    
    if not any([args.tsr, args.all, args.rango, args.dry_run]):
        parser.error("Debe especificar --tsr, --all, --rango o --dry-run")
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║              CÍCLOPE · COMPILADOR MONOLITO                      ║
║         De 7 capas a 19 documentos autónomos                   ║
║              {datetime.now().strftime('%d.%m.%Y %H:%M')}                            ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # CARGA DE DATOS
    print("[CARGA] Cargando 7 capas de datos...")
    
    capa0_text = cargar_texto(CAPA0_PATH)
    capa1 = cargar_json(CAPA1_PATH)
    capa2 = cargar_json(CAPA2_PATH)
    capa3 = cargar_json(CAPA3_PATH)
    capa4 = cargar_json(CAPA4_PATH)
    capa5 = cargar_json(CAPA5_PATH)
    capa6 = cargar_json(CAPA6_PATH)
    capa7 = cargar_json(CAPA7_PATH)
    
    print(f"  CAPA0 (semilla):         {'✓' if capa0_text else '✗'} [{len(capa0_text.split()) if capa0_text else 0} palabras]")
    print(f"  CAPA1 (bibliografía):     {'✓' if capa1 else '✗'} [7 clusters]")
    print(f"  CAPA2 (genealogía):       {'✓' if capa2 else '✗'} [{len(capa2) if capa2 else 0} TSRs]")
    print(f"  CAPA3 (problematización): {'✓' if capa3 else '✗'} [{len(capa3.get('estructura', [])) if capa3 else 0} TSRs]")
    print(f"  CAPA4 (resonancias):      {'✓' if capa4 else '✗'} [{len(capa4.get('estructura', [])) if capa4 else 0} TSRs]")
    print(f"  CAPA5 (meta-análisis):    {'✓' if capa5 else '✗'} [{len(capa5) if capa5 else 0} TSRs]")
    print(f"  CAPA6 (talleres):         {'✓' if capa6 else '✗'} [{len(capa6) if capa6 else 0} TSRs]")
    print(f"  CAPA7 (casos):            {'✓' if capa7 else '✗'} [{len(capa7) if capa7 else 0} TSRs]")
    
    if not capa2:
        print("[ERROR CRÍTICO] CAPA2 es requerida. Abortando.")
        sys.exit(1)
    
    # Prompt maestro
    prompt_base = cargar_texto(PROMPT_PATH)
    if not prompt_base:
        print("[WARN] PROMPT_MONOLITO.txt no encontrado. Usando prompt embebido.")
        prompt_base = _prompt_embebido()
    else:
        print(f"  PROMPT MONOLITO:         ✓ [{len(prompt_base)} chars]")
    
    # Determinar TSRs
    if args.dry_run:
        tsr_ids = list(range(TSR_MIN, TSR_MAX + 1))
    elif args.tsr:
        tsr_ids = [args.tsr]
    elif args.rango:
        tsr_ids = list(range(args.rango[0], args.rango[1] + 1))
    else:
        tsr_ids = list(range(TSR_MIN, TSR_MAX + 1))
    
    # DRY RUN — Solo auditoría
    if args.dry_run:
        print(f"\n[AUDITORÍA] TSRs {tsr_ids[0]}-{tsr_ids[-1]} ({len(tsr_ids)} TSRs)\n")
        print(f"{'TSR':<6} {'Título':<50} {'Capas':<8} {'Estado'}")
        print(f"{'─'*6} {'─'*50} {'─'*8} {'─'*10}")
        
        completos = 0
        parciales = 0
        vacios = 0
        
        for tsr_id in tsr_ids:
            datos = extraer_tsr_completo(tsr_id, capa0_text, capa1, capa2, capa3, capa4, capa5, capa6, capa7)
            capas_ok = sum(1 for campo in ["semilla", "bibliografia", "genealogia",
                                           "problematizacion", "resonancias", "metaanalisis",
                                           "guion_taller", "caso_aplicacion"]
                          if datos[campo] not in ["no disponible", "no encontrada",
                                                  "Sin fuentes", "Sin contenido"])
            # Check more precisely
            capas_real = 0
            no_disponibles = ["Semilla no disponible.", "Semilla no encontrada para este TSR.",
                             "Bibliografía no disponible.", "Bibliografía no encontrada para este TSR.",
                             "Sin fuentes registradas.", "Sin fuentes con datos completos.",
                             "Genealogía no disponible.", "Sin contenido genealógico.",
                             "Problematización no disponible.", "Sin contenido.",
                             "Resonancias no disponibles.", "Resonancias no encontradas.",
                             "Meta-análisis no disponible.",
                             "Guion de taller no disponible.", "Sin contenido de taller.",
                             "Caso de aplicación no disponible.", "Sin contenido de caso."]
            
            for campo in ["semilla", "bibliografia", "genealogia", "problematizacion",
                          "resonancias", "metaanalisis", "guion_taller", "caso_aplicacion"]:
                if datos[campo] not in no_disponibles:
                    capas_real += 1
            
            titulo_short = datos["titulo"][:48] + ".." if len(datos["titulo"]) > 50 else datos["titulo"]
            estado = "✅" if capas_real == 8 else ("⚠️" if capas_real >= 6 else "🔴")
            
            print(f"{tsr_id:<6} {titulo_short:<50} {capas_real}/8    {estado}")
            
            if capas_real == 8:
                completos += 1
            elif capas_real >= 6:
                parciales += 1
            else:
                vacios += 1
        
        print(f"\n[RESUMEN AUDITORÍA]")
        print(f"  ✅ Completos (8/8 capas):    {completos}")
        print(f"  ⚠️ Parciales (6-7 capas):    {parciales}")
        print(f"  🔴 Incompletos (<6 capas):  {vacios}")
        print(f"\n  Total TSRs auditados:        {len(tsr_ids)}")
        return
    
    # VERIFICAR API
    if args.modelo == "opencode":
        print("[INFO] OpenCode MiniMax M2.5-free (sin API key)")
    elif args.modelo == "minimax":
        print(f"[INFO] MiniMax: {'✓ API key detectada' if MINIMAX_API_KEY else '⚠ Sin API key'}")
    else:
        print(f"[INFO] Perplexity: {'✓ API key detectada' if PERPLEXITY_API_KEY else '⚠ Sin API key'}")
    
    # CREAR DIRECTORIO
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Directorio de salida: {OUTPUT_DIR}")
    
    # PROCESAR
    print(f"\n[INFO] Iniciando compilación de {len(tsr_ids)} monolitos...")
    print(f"[INFO] Modelo: {args.modelo}")
    
    resultados, fallidos = procesar_lote(
        tsr_ids, capa0_text, capa1, capa2, capa3, capa4, capa5, capa6, capa7,
        prompt_base, args.modelo, args.no_postproc
    )
    
    # GUARDAR JSON CONSOLIDADO
    existentes = {}
    if OUTPUT_JSON.exists():
        existentes = cargar_json(OUTPUT_JSON) or {}
    existentes.update(resultados)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(existentes, f, indent=2, ensure_ascii=False)
    
    # RESUMEN
    total = len(existentes)
    print(f"\n{'='*70}")
    print(f"[RESUMEN] Compilación de monolitos completada")
    print(f"{'='*70}")
    print(f"  TSRs compilados esta ejecución: {len(resultados)}/{len(tsr_ids)}")
    print(f"  Total monolitos en archivo:     {total}")
    print(f"  Archivos .md generados:          {len(resultados)}")
    print(f"  JSON consolidado:                {OUTPUT_JSON}")
    
    if fallidos:
        print(f"\n  TSRs FALLIDOS: {fallidos}")
        print(f"  → Reintentar: python scripts/compilar_monolito.py --modelo {args.modelo} --tsr {' '.join(str(f) for f in fallidos)}")
    
    ok_count = sum(1 for r in resultados.values()
                   if r["estadisticas"]["validacion_extension"] == "ok")
    flex_count = sum(1 for r in resultados.values()
                     if r["estadisticas"]["validacion_extension"] == "flexible")
    alert_count = sum(1 for r in resultados.values()
                      if r["estadisticas"]["validacion_extension"] == "fuera")
    
    print(f"\n[CALIDAD]")
    print(f"  ✓ En rango ({MIN_PALABRAS}-{MAX_PALABRAS}):     {ok_count}")
    print(f"  ~ Aceptable:                              {flex_count}")
    print(f"  ✗ Requieren revisión:                     {alert_count}")
    print(f"\n  → Archivos en: {OUTPUT_DIR}/")


def _prompt_embebido():
    return """Redacta el TSR{TSR_ID} completo: "{TITULO}".

Integra estas 7 capas en un documento monolítico de 2,500-4,000 palabras:

CAPA0 (Semilla): {SEMILLA_CAPA0}
CAPA2 (Genealogía): {GENEALOGIA_CAPA2}
CAPA3 (Problematización): {PROBLEMATIZACION_CAPA3}
CAPA4 (Resonancias): {RESONANCIAS_CAPA4}
CAPA5 (Meta-análisis): {METAANALISIS_CAPA5}
CAPA6 (Taller): {GUION_TALLER_CAPA6}

Estructura: Epígrafe → Genealogía → Problematización → Resonancias → Meta-análisis → Taller → Glosario → Fuentes.
Tono: académico, exigente, sin resoluciones. Redacta de nuevo, no copies."""


if __name__ == "__main__":
    main()