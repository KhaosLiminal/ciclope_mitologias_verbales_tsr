#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPILADOR MONOLITO - MODO COPY-PASTE CON BIG PICKLE OPENCODE ZEN
Extrae y acomoda las 8 capas usando OpenCode CLI sin API key.
El modelo solo extrae y formatea, no genera contenido nuevo.
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple

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
OUTPUT_DIR = BASE_DIR / "outputs" / "TSR_COMPILADOS"

TSR_MIN = 102
TSR_MAX = 120

# ============================================================================
# EXTRACTOR DE DATOS
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
    if not capa0_text:
        return "Semilla no disponible."
    patron = re.compile(rf'##\s*TSR{tsr_id}\b[^\n]*\n(.*?)(?=\n##\s*TSR|\Z)', re.DOTALL)
    match = patron.search(capa0_text)
    if match:
        texto = match.group(1).strip()
        return texto[:800] if len(texto) > 800 else texto
    return "Semilla no encontrada para este TSR."

def extraer_bibliografia(capa1: Optional[Dict], tsr_id: int) -> str:
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
    return texto[:2000] if texto else "Sin contenido genealógico.", metadata

def extraer_problematizacion(capa3: Optional[Dict], tsr_id: int) -> str:
    if not capa3:
        return "Problematización no disponible."
    for item in capa3.get("estructura", []):
        if str(item.get("tsr", "")) == str(tsr_id):
            texto = item.get("problematizacion", "")
            return texto[:3000] if texto else "Sin contenido."
    return "Problematización no encontrada."

def extraer_resonancias(capa4: Optional[Dict], tsr_id: int) -> str:
    if not capa4:
        return "Resonancias no disponibles."
    for item in capa4.get("estructura", []):
        if str(item.get("tsr", "")) == str(tsr_id):
            texto = item.get("resonancias", "")
            return texto[:1500] if texto else "Sin contenido."
    return "Resonancias no encontradas."

def extraer_metaanalisis(capa5: Optional[Dict], tsr_id: int) -> str:
    tsr_str = str(tsr_id)
    if not capa5 or tsr_str not in capa5:
        return "Meta-análisis no disponible."
    data = capa5[tsr_str]
    texto = data.get("metaanalisis", "")
    return texto[:2000] if texto else "Sin contenido de meta-análisis."

def extraer_guion_taller(capa6: Optional[Dict], tsr_id: int) -> str:
    tsr_str = str(tsr_id)
    if not capa6 or tsr_str not in capa6:
        return "Guion de taller no disponible."
    data = capa6[tsr_str]
    texto = data.get("guion_taller", "")
    return texto[:1500] if texto else "Sin contenido de taller."

def extraer_caso_aplicacion(capa7: Optional[Dict], tsr_id: int) -> str:
    tsr_str = str(tsr_id)
    if not capa7 or tsr_str not in capa7:
        return "Caso de aplicación no disponible."
    data = capa7[tsr_str]
    texto = data.get("caso_aplicacion", "")
    return texto[:1500] if texto else "Sin contenido de caso."

def extraer_tsr_completo(tsr_id: int,
                         capa0_text: Optional[str],
                         capa1: Optional[Dict],
                         capa2: Optional[Dict],
                         capa3: Optional[Dict],
                         capa4: Optional[Dict],
                         capa5: Optional[Dict],
                         capa6: Optional[Dict],
                         capa7: Optional[Dict]) -> Dict[str, str]:
    tsr_str = str(tsr_id)
    genealogia_text, genealogia_meta = extraer_genealogia(capa2, tsr_id)
    titulo = genealogia_meta.get("titulo", f"TSR{tsr_id}")
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
# FORMATEO MONOLÍTICO (COPY-PASTE SIN GENERACIÓN)
# ============================================================================

def llamar_opencode_zens(prompt: str) -> Optional[str]:
    """
    Llama a Big Pickle Opencode Zen vía OpenCode CLI sin API key.
    El modelo solo extrae y formatea, no genera contenido nuevo.
    """
    try:
        cmd = ["opencode", "--model", "bigpickle/opencode-zen", "run", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            resp = []
            capturing = False
            for line in lines:
                if '> build' in line or 'bigpickle' in line.lower():
                    capturing = True
                    continue
                elif capturing and line.startswith('$'):
                    break
                elif capturing and line.strip():
                    resp.append(line.strip())
            output = '\n'.join(resp) if resp else result.stdout
            if len(output.strip()) < 50:
                return None
            return output
        return None
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout OpenCode (180s)")
        return None
    except FileNotFoundError:
        print("[ERROR] 'opencode' no encontrado.")
        return None
    except Exception as e:
        print(f"[ERROR] OpenCode: {str(e)[:80]}")
        return None

def construir_prompt_extraccion(datos_tsr: Dict) -> str:
    """Construye prompt para extracción y acomodación (sin generación)."""
    tsr_id = datos_tsr["tsr_id"]
    titulo = datos_tsr["titulo"]
    
    prompt = f"""EXTRAE Y ACOMODA las siguientes 8 capas en un formato monolítico coherente.
NO generes contenido nuevo. NO redactes. Solo extrae, organiza y formatea.

TSR{tsr_id}: {titulo}

CAPA 0 - Semilla:
{datos_tsr["semilla"]}

CAPA 1 - Bibliografía:
{datos_tsr["bibliografia"]}

CAPA 2 - Genealogía:
{datos_tsr["genealogia"]}

CAPA 3 - Problematización:
{datos_tsr["problematizacion"]}

CAPA 4 - Resonancias:
{datos_tsr["resonancias"]}

CAPA 5 - Meta-análisis:
{datos_tsr["metaanalisis"]}

CAPA 6 - Guion de Taller:
{datos_tsr["guion_taller"]}

CAPA 7 - Caso de Aplicación:
{datos_tsr["caso_aplicacion"]}

INSTRUCCIONES:
1. Extrae el contenido de cada capa exactamente como está
2. Acomódalo en un formato monolítico con encabezados claros
3. NO agregues texto nuevo, NO resumas, NO interpretes
4. Solo organiza y formatea
5. Mantén el tono y estilo original de cada capa

Genera el monolito ahora:
"""
    return prompt

def formatear_monolito_local(datos_tsr: Dict) -> str:
    """Acomoda las 8 capas en formato monolítico localmente sin modelo."""
    tsr_id = datos_tsr["tsr_id"]
    titulo = datos_tsr["titulo"]
    
    contenido = f"""## CAPA 0: Semilla

{datos_tsr["semilla"]}

---

## CAPA 1: Bibliografía

{datos_tsr["bibliografia"]}

---

## CAPA 2: Genealogía

{datos_tsr["genealogia"]}

---

## CAPA 3: Problematización

{datos_tsr["problematizacion"]}

---

## CAPA 4: Resonancias

{datos_tsr["resonancias"]}

---

## CAPA 5: Meta-análisis

{datos_tsr["metaanalisis"]}

---

## CAPA 6: Guion de Taller

{datos_tsr["guion_taller"]}

---

## CAPA 7: Caso de Aplicación

{datos_tsr["caso_aplicacion"]}
"""
    return contenido

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║              CÍCLOPE · COMPILADOR MONOLITO                     ║
║           MODO COPY-PASTE (sin generación API)                  ║
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
    
    print(f"  CAPA0 (semilla):         {'✓' if capa0_text else '✗'}")
    print(f"  CAPA1 (bibliografía):     {'✓' if capa1 else '✗'}")
    print(f"  CAPA2 (genealogía):       {'✓' if capa2 else '✗'}")
    print(f"  CAPA3 (problematización): {'✓' if capa3 else '✗'}")
    print(f"  CAPA4 (resonancias):      {'✓' if capa4 else '✗'}")
    print(f"  CAPA5 (meta-análisis):    {'✓' if capa5 else '✗'}")
    print(f"  CAPA6 (talleres):         {'✓' if capa6 else '✗'}")
    print(f"  CAPA7 (casos):            {'✓' if capa7 else '✗'}")
    
    if not capa2:
        print("[ERROR CRÍTICO] CAPA2 es requerida. Abortando.")
        sys.exit(1)
    
    # CREAR DIRECTORIO
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Directorio de salida: {OUTPUT_DIR}")
    
    # PROCESAR TSRs
    tsr_ids = list(range(TSR_MIN, TSR_MAX + 1))
    print(f"\n[INFO] Iniciando compilación con Big Pickle Opencode Zen de {len(tsr_ids)} monolitos...")
    print("[INFO] Modo: Extracción y acomodación (sin generación)")
    
    exitosos = 0
    fallidos = 0
    
    for i, tsr_id in enumerate(tsr_ids, 1):
        print(f"\n[PROGRESO] {i}/{len(tsr_ids)} — TSR{tsr_id}")
        
        datos = extraer_tsr_completo(tsr_id, capa0_text, capa1, capa2, capa3, capa4, capa5, capa6, capa7)
        
        # Verificar disponibilidad de capas
        capas_ok = sum(1 for campo in ["semilla", "bibliografia", "genealogia", "problematizacion",
                          "resonancias", "metaanalisis", "guion_taller", "caso_aplicacion"]
                          if datos[campo] not in ["Semilla no disponible.", "Semilla no encontrada para este TSR.",
                                                  "Bibliografía no disponible.", "Bibliografía no encontrada para este TSR.",
                                                  "Sin fuentes registradas.", "Sin fuentes con datos completos.",
                                                  "Genealogía no disponible.", "Sin contenido genealógico.",
                                                  "Problematización no disponible.", "Sin contenido.",
                                                  "Resonancias no disponibles.", "Resonancias no encontradas.",
                                                  "Meta-análisis no disponible.",
                                                  "Guion de taller no disponible.", "Sin contenido de taller.",
                                                  "Caso de aplicación no disponible.", "Sin contenido de caso."])
        
        print(f"  Capas disponibles: {capas_ok}/8")
        
        if capas_ok < 6:
            print(f"  [SKIP] TSR{tsr_id} tiene menos de 6 capas")
            fallidos += 1
            continue
        
        # Construir monolito localmente (sin llamar a modelo)
        print(f"  [INFO] Compilando localmente sin modelo externo...")
        
        monolito = formatear_monolito_local(datos)
        palabras = len(monolito.split())
        
        # Agregar header
        titulo = datos["titulo"]
        header = f"""# TSR{tsr_id}: {titulo}

**Proyecto Cíclope · Mitologías Verbales**
**Sistema de Lectura de Segundo Orden (TRCO)**
**Fecha de compilación:** {datetime.now().strftime('%d.%m.%Y')}
**Modo:** Compilación Local (copy-paste sin modelo)
**Palabras:** {palabras}

---

"""
        
        contenido_final = header + monolito + f"""

---

*Compilado por Cíclope · Modo Local · Monolito TSR{tsr_id}*
*Proyecto Cíclope · Mitologías Verbales · 2026*
"""
        
        # Guardar
        md_path = OUTPUT_DIR / f"TSR{tsr_id}_MONOLITO.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(contenido_final)
        
        print(f"  [GUARDADO] {md_path} ({palabras} palabras)")
        exitosos += 1
    
    print(f"\n{'='*70}")
    print(f"[RESUMEN]")
    print(f"  Exitosos: {exitosos}/{len(tsr_ids)}")
    print(f"  Fallidos: {fallidos}/{len(tsr_ids)}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
