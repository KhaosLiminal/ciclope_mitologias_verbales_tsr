#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR CAPA 6: GUIONES DE TALLER (Versión OpenCode)
Sistema modular de 7 capas para Cíclope: Mitologías Verbales

Versión limpia para ejecución vía OpenCode en WSL.
Sin retry decorator, sin imports innecesarios, sin argparse complejo.
Diseñada para: opencode --model opencode/minimax-m2.5-free run ...

Uso:
    python scripts/generar_capa6_opencode.py --all
    python scripts/generar_capa6_opencode.py --tsr 102
"""

import os
import sys
import re
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
CAPA1_PATH = BASE_DIR / "capas" / "CAPA1_bibliografia" / "TSR_CAPA1_FINAL.json"
CAPA2_PATH = BASE_DIR / "capas" / "CAPA2_genealogia" / "TSR_CAPA2_FINAL_CONSOLIDADO.json"
CAPA3_PATH = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"
CAPA4_PATH = BASE_DIR / "capas" / "CAPA4_resonancias" / "TSR_CAPA4_FINAL.json"
CAPA5_PATH = BASE_DIR / "capas" / "CAPA5_metanalisis" / "TSR_CAPA5_FINAL.json"
PROMPT_PATH = BASE_DIR / "config" / "PROMPTS_POR_CAPA" / "CAPA6_prompt.txt"
OUTPUT_DIR = BASE_DIR / "capas" / "CAPA6_talleres"
OUTPUT_JSON = OUTPUT_DIR / "TSR_CAPA6_FINAL.json"

MIN_PALABRAS = 300
MAX_PALABRAS = 500

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def cargar_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def cargar_texto(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def filtrar_artefactos(texto):
    patron = re.compile(
        r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF\u00A1\u00A9\u00AB\u00AE\u00B0'
        r'\u00BB\u00BF\u2010-\u2027\u2030-\u205E\u2070-\u209F\u20A0-\u20CF'
        r'\u2100-\u214F\u2190-\u21FF\u2200-\u22FF\u2300-\u23FF\u25A0-\u25FF'
        r'\u2600-\u26FF\u2700-\u27BF\s\n\r\t.,;:!?\'"()\[\]{}\-–—/<>@#$%^&*+=|~`]'
    )
    lineas = texto.split('\n')
    filtradas = []
    for linea in lineas:
        artefactos = patron.findall(linea)
        if len(artefactos) > 3:
            continue
        if artefactos:
            linea = patron.sub('', linea)
        filtradas.append(linea)
    return '\n'.join(filtradas)

def truncar(texto, max_pal=500):
    palabras = texto.split()
    if len(palabras) <= max_pal:
        return texto
    lineas = texto.split('\n')
    resultado = []
    conteo = 0
    for linea in lineas:
        p_linea = linea.split()
        faltantes = max_pal - conteo
        if faltantes <= 0:
            break
        if len(p_linea) <= faltantes:
            resultado.append(linea)
            conteo += len(p_linea)
        else:
            resultado.append(' '.join(p_linea[:faltantes]) + '...')
            conteo += faltantes
            break
    t = '\n'.join(resultado)
    if conteo < len(palabras) * 0.9:
        t += f"\n\n> [Truncado: {conteo}/{len(palabras)} palabras]"
    return t

# ============================================================================
# EXTRACTOR DE DATOS
# ============================================================================

def extraer_datos(tsr_id, capa1, capa2, capa3, capa4, capa5):
    datos = {"tsr_id": tsr_id}
    tsr_str = str(tsr_id)
    
    # CAPA1
    bibliografia = {}
    if capa1:
        for cluster_name, tsrs in capa1.get("clusters", {}).items():
            for tsr in tsrs:
                if tsr.get("tsr") == tsr_str:
                    bibliografia = {"titulo": tsr.get("titulo", ""), "cluster": cluster_name}
                    break
            if bibliografia:
                break
    datos["bibliografia"] = bibliografia
    
    # CAPA2
    genealogia = {}
    if capa2 and tsr_str in capa2:
        t = capa2[tsr_str]
        c = t.get("contenido", "")
        genealogia = {
            "titulo": t.get("titulo", ""),
            "autor": t.get("autor", ""),
            "obra": t.get("obra", ""),
            "año": t.get("año", ""),
            "concepto_central": t.get("concepto_central", ""),
            "keywords": t.get("keywords", []),
            "conexion_RH": t.get("conexion_RH", ""),
            "resumen": (c[:400] + "..." + c[-200:]) if len(c) > 600 else c
        }
    datos["genealogia"] = genealogia
    
    # CAPA3
    problematizacion = ""
    if capa3:
        for item in capa3.get("estructura", []):
            if str(item.get("tsr", "")) == tsr_str:
                problematizacion = item.get("problematizacion", "")
                break
    datos["problematizacion"] = problematizacion[:600] if problematizacion else ""
    
    # CAPA4
    resonancias = ""
    if capa4:
        for item in capa4.get("estructura", []):
            if str(item.get("tsr", "")) == tsr_str:
                resonancias = item.get("resonancias", "")
                break
    datos["resonancias"] = resonancias[:300] if resonancias else ""
    
    # CAPA5
    metaanalisis = ""
    if capa5 and tsr_str in capa5:
        metaanalisis = capa5[tsr_str].get("metaanalisis", "")
        datos["concepto_principal_capa5"] = capa5[tsr_str].get("concepto_principal", "")
    datos["metaanalisis"] = metaanalisis[:500] if metaanalisis else ""
    
    return datos

# ============================================================================
# CLIENTE OPENCODE
# ============================================================================

def api_opencode(prompt):
    try:
        cmd = ["opencode", "--model", "opencode/minimax-m2.5-free", "run", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
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
            if len(output.strip()) < 50:
                return None
            return output
        return None
    except:
        return None

# ============================================================================
# CONSTRUCTOR DE PROMPT
# ============================================================================

def construir_prompt(datos, prompt_base):
    tsr_id = datos["tsr_id"]
    gen = datos.get("genealogia", {})
    titulo = gen.get("titulo", datos.get("bibliografia", {}).get("titulo", f"TSR{tsr_id}"))
    
    gen_texto = ""
    if gen.get("resumen"):
        gen_texto = (
            f"Autor: {gen.get('autor', '')}. Obra: {gen.get('obra', '')}. "
            f"Concepto: {gen.get('concepto_central', '')}. "
            f"Keywords: {', '.join(gen.get('keywords', [])[:5])}. "
            f"Resumen: {gen['resumen']}"
        )
    
    glosario = "Términos canónicos: fragmento (Schlegel vs Blanchot), aura (Benjamin), autor (Barthes/Foucault/Eco), archivo (Foucault/Derrida), episteme (Foucault), glitch."
    
    p = prompt_base
    p = p.replace("{TSR_ID}", str(tsr_id))
    p = p.replace("{TITULO}", titulo)
    p = p.replace("{GENEALOGIA_CAPA2}", gen_texto)
    p = p.replace("{PROBLEMATIZACION_CAPA3}", datos.get("problematizacion", "No disponible")[:500])
    p = p.replace("{METAANALISIS_CAPA5}", datos.get("metaanalisis", "No disponible")[:400])
    p = p.replace("{GLOSARIO_TERMINOS}", glosario)
    return p

# ============================================================================
# GENERACIÓN
# ============================================================================

def generar_guion(datos, prompt_base):
    tsr_id = datos["tsr_id"]
    print(f"\n[INFO] TSR{tsr_id}...")
    
    if not datos.get("genealogia"):
        print(f"[ERROR] TSR{tsr_id}: sin genealogía. Saltando.")
        return None
    
    prompt = construir_prompt(datos, prompt_base)
    resultado = api_opencode(prompt)
    
    if not resultado:
        print(f"[ERROR] TSR{tsr_id}: sin respuesta del modelo")
        return None
    
    # Post-procesamiento
    resultado = filtrar_artefactos(resultado)
    if len(resultado.split()) > 600:
        resultado = truncar(resultado, 500)
    
    palabras = len(resultado.split())
    valido = MIN_PALABRAS <= palabras <= MAX_PALABRAS
    nivel = "ok" if valido else ("flexible" if 250 <= palabras <= 600 else "fuera")
    print(f"[{'OK' if nivel == 'ok' else 'WARN'}] TSR{tsr_id}: {palabras} pal ({nivel})")
    
    # Guardar .md
    titulo = datos.get("genealogia", {}).get("titulo", f"TSR{tsr_id}")
    md_path = OUTPUT_DIR / f"TSR{tsr_id}_GUION_TALLER.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# GUIÓN DE TALLER: TSR{tsr_id}\n\n## {titulo}\n\n"
                f"**Fecha:** {datetime.now().strftime('%d.%m.%Y')}\n"
                f"**Palabras:** {palabras}\n**Validación:** {nivel}\n\n---\n\n"
                f"{resultado}\n\n---\n*Cíclope CAPA6 · 2026*\n")
    
    return {
        "tsr_id": tsr_id,
        "titulo": titulo,
        "guion_taller": resultado,
        "estadisticas": {
            "palabras": palabras,
            "modelo_usado": "opencode-minimax-m2.5-free",
            "fecha_generacion": datetime.now().isoformat(),
            "validacion_extension": nivel
        }
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    tsr_ids = []
    for arg in sys.argv[1:]:
        if arg == "--all":
            tsr_ids = list(range(102, 121))
            break
        elif arg.startswith("--tsr="):
            tsr_ids = [int(arg.split("=")[1])]
        elif arg.isdigit():
            tsr_ids.append(int(arg))
    
    if not tsr_ids:
        tsr_ids = list(range(102, 121))
    
    print(f"[INFO] Cíclope CAPA6 — {len(tsr_ids)} TSRs a procesar")
    
    capa1 = cargar_json(CAPA1_PATH)
    capa2 = cargar_json(CAPA2_PATH)
    capa3 = cargar_json(CAPA3_PATH)
    capa4 = cargar_json(CAPA4_PATH)
    capa5 = cargar_json(CAPA5_PATH)
    
    if not capa2 or not capa3:
        print("[ERROR] CAPA2 y CAPA3 son requeridas")
        return
    
    prompt_base = cargar_texto(PROMPT_PATH) or _prompt_embebido()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    resultados = {}
    fallidos = []
    
    for tsr_id in tsr_ids:
        datos = extraer_datos(tsr_id, capa1, capa2, capa3, capa4, capa5)
        r = generar_guion(datos, prompt_base)
        if r:
            resultados[str(tsr_id)] = r
        else:
            fallidos.append(tsr_id)
        time.sleep(2)
    
    # Guardar JSON consolidado
    existentes = {}
    if OUTPUT_JSON.exists():
        existentes = cargar_json(OUTPUT_JSON) or {}
    existentes.update(resultados)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(existentes, f, indent=2, ensure_ascii=False)
    
    print(f"\n[RESUMEN] {len(resultados)}/{len(tsr_ids)} exitosos")
    if fallidos:
        print(f"[FALLIDOS] {fallidos}")

def _prompt_embebido():
    return """Genera un guion de taller de 300-500 palabras para TSR{TSR_ID}.
Incluye: título, 3 módulos (docencia, mediación, gestión cultural), actividades ejecutables,
evaluación de segundo orden, 3 preguntas abiertas de cierre.
Datos: Genealogía: {GENEALOGIA_CAPA2}. Problematización: {PROBLEMATIZACION_CAPA3}.
Meta-análisis: {METAANALISIS_CAPA5}. Tono institucional. Sin emojis."""

if __name__ == "__main__":
    main()