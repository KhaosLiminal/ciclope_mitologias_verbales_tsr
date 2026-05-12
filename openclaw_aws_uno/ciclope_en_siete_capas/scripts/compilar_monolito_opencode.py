#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPILADOR MONOLITO — VERSIÓN OPENCODE CLI
Sistema de redacción final de TSRs completos mediante OpenCode CLI.

Diferencias con compilar_monolito.py:
- Sin argparse (usa sys.argv simple)
- Sin decoradores (retry inline)
- OpenCode como único cliente
- Sin dependencias de API keys
- Mismo extractor de datos, mismo prompt

Uso:
    python scripts/compilar_monolito_opencode.py --all
    python scripts/compilar_monolito_opencode.py --tsr 102
    python scripts/compilar_monolito_opencode.py 102 103 104
    python scripts/compilar_monolito_opencode.py --dry-run
"""

import os
import sys
import re
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
CAPA0_PATH = BASE_DIR / "capas" / "CAPA0_semilla" / "CAPA0_TSR101-120QUOTES.md"
CAPA1_PATH = BASE_DIR / "capas" / "CAPA1_bibliografia" / "TSR_CAPA1_FINAL.json"
CAPA2_PATH = BASE_DIR / "capas" / "CAPA2_genealogia" / \
    "TSR_CAPA2_FINAL_CONSOLIDADO.json"
CAPA3_PATH = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"
CAPA4_PATH = BASE_DIR / "capas" / "CAPA4_resonancias" / "TSR_CAPA4_FINAL.json"
CAPA5_PATH = BASE_DIR / "capas" / "CAPA5_metanalisis" / "TSR_CAPA5_FINAL.json"
CAPA6_PATH = BASE_DIR / "capas" / "CAPA6_talleres" / "TSR_CAPA6_FINAL.json"
CAPA7_PATH = BASE_DIR / "capas" / "CAPA7_casos" / "TSR_CAPA7_FINAL.json"
PROMPT_PATH = BASE_DIR / "config" / "PROMPTS_POR_CAPA" / "PROMPT_MONOLITO_2.txt"
OUTPUT_DIR = BASE_DIR / "outputs" / "TSR_COMPILAR_MONOLITOS_OPENCODE"

TSR_MIN = 102
TSR_MAX = 120


# ============================================================================
# EXTRACTOR DE DATOS — SIN TRUNCACIÓN
# ============================================================================

def cargar_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] No encontrado: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON inválido en {path}: {str(e)[:80]}")
        return None


def cargar_texto(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def extraer_semilla(capa0_text, tsr_id):
    if not capa0_text:
        return "Semilla no disponible."
    patron = re.compile(
        rf'##\s*TSR{tsr_id}\b[^\n]*\n(.*?)(?=\n##\s*TSR|\Z)',
        re.DOTALL
    )
    match = patron.search(capa0_text)
    if match:
        return match.group(1).strip()
    return "Semilla no encontrada para este TSR."


def extraer_bibliografia(capa1, tsr_id):
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
                for f in fuentes[:15]:
                    autor = f.get("autor", "")
                    titulo = f.get("titulo", "")
                    anio = f.get("año", "")
                    if autor and titulo:
                        refs.append(f"{autor}. {titulo}. {anio}.")
                return "\n".join(refs) if refs else "Sin fuentes con datos completos."
    return "Bibliografía no encontrada para este TSR."


def extraer_genealogia(capa2, tsr_id):
    tsr_str = str(tsr_id)
    metadata = {}
    if not capa2 or tsr_str not in capa2:
        return "Genealogía no disponible.", metadata
    data = capa2[tsr_str]
    texto = data.get("contenido", "")
    metadata = {
        "titulo": data.get("titulo", ""),
        "autor": data.get("autor", ""),
        "obra": data.get("obra", ""),
        "concepto_central": data.get("concepto_central", ""),
        "cluster": data.get("cluster", ""),
        "keywords": data.get("keywords", []),
    }
    # SIN truncar
    return texto if texto else "Sin contenido genealógico.", metadata


def extraer_problematizacion(capa3, tsr_id):
    if not capa3:
        return "Problematización no disponible."
    for item in capa3.get("estructura", []):
        if str(item.get("tsr", "")) == str(tsr_id):
            texto = item.get("problematizacion", "")
            # SIN truncar
            return texto if texto else "Sin contenido."
    return "Problematización no encontrada."


def extraer_resonancias(capa4, tsr_id):
    if not capa4:
        return "Resonancias no disponibles."
    for item in capa4.get("estructura", []):
        if str(item.get("tsr", "")) == str(tsr_id):
            texto = item.get("resonancias", "")
            # SIN truncar
            return texto if texto else "Sin contenido."
    return "Resonancias no encontradas."


def extraer_metaanalisis(capa5, tsr_id):
    tsr_str = str(tsr_id)
    if not capa5 or tsr_str not in capa5:
        return "Meta-análisis no disponible."
    texto = capa5[tsr_str].get("metaanalisis", "")
    # SIN truncar
    return texto if texto else "Sin contenido de meta-análisis."


def extraer_guion_taller(capa6, tsr_id):
    tsr_str = str(tsr_id)
    if not capa6 or tsr_str not in capa6:
        return "Guion de taller no disponible."
    texto = capa6[tsr_str].get("guion_taller", "")
    # SIN truncar
    return texto if texto else "Sin contenido de taller."


def extraer_caso_aplicacion(capa7, tsr_id):
    tsr_str = str(tsr_id)
    if not capa7 or tsr_str not in capa7:
        return "Caso de aplicación no disponible."
    texto = capa7[tsr_str].get("caso_aplicacion", "")
    # SIN truncar
    return texto if texto else "Sin contenido de caso."


def extraer_tsr_completo(tsr_id, c0, c1, c2, c3, c4, c5, c6, c7):
    tsr_str = str(tsr_id)
    genealogia_text, genealogia_meta = extraer_genealogia(c2, tsr_id)
    titulo = genealogia_meta.get("titulo", f"TSR{tsr_id}")
    if titulo == f"TSR{tsr_id}" and c5 and tsr_str in c5:
        titulo = c5[tsr_str].get("concepto_principal", titulo)
    return {
        "tsr_id": tsr_id,
        "titulo": titulo,
        "semilla": extraer_semilla(c0, tsr_id),
        "bibliografia": extraer_bibliografia(c1, tsr_id),
        "genealogia": genealogia_text,
        "problematizacion": extraer_problematizacion(c3, tsr_id),
        "resonancias": extraer_resonancias(c4, tsr_id),
        "metaanalisis": extraer_metaanalisis(c5, tsr_id),
        "guion_taller": extraer_guion_taller(c6, tsr_id),
        "caso_aplicacion": extraer_caso_aplicacion(c7, tsr_id),
        "metadata": genealogia_meta,
    }


# ============================================================================
# POST-PROCESAMIENTO LIGERO
# ============================================================================

def filtrar_artefactos(texto):
    """Filtra caracteres no-latinos agresivos (CJK, Cirílico)."""
    patron = re.compile(
        r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF\u00A1\u00A9\u00AB\u00AE'
        r'\u00B0\u00BB\u00BF\u2010-\u2027\u2030-\u205E\u2070-\u209F'
        r'\u20A0-\u20CF\u2100-\u214F\u2190-\u21FF\u2200-\u22FF\u2300-\u23FF'
        r'\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF\s\n\r\t.,;:!?\'"()\[\]'
        r'{}\-\u2013\u2014/<>@#$%^&*+=|~`]'
    )
    lineas = texto.split('\n')
    filtradas = []
    for linea in lineas:
        artefactos = patron.findall(linea)
        if len(artefactos) > 5:
            continue  # Descartar línea con demasiados caracteres extraños
        if artefactos:
            linea = patron.sub('', linea)
        filtradas.append(linea)
    return '\n'.join(filtradas)


def postprocesar(texto):
    """Post-procesamiento mínimo: filtrar artefactos, NO truncar palabras."""
    limpio = filtrar_artefactos(texto)
    palabras = len(limpio.split())
    return limpio, palabras


# ============================================================================
# OPENCODE CLIENTE
# ============================================================================

def llamar_opencode(prompt, retries=2):
    """
    Llama a OpenCode CLI con retry simple.
    Usa opencode/minimax-m2.5-free como modelo por defecto.
    """
    for intento in range(1, retries + 1):
        try:
            cmd = [
                "opencode",
                "--model", "opencode/minimax-m2.5-free",
                "run", prompt
            ]
            print(f"  [OPENCODE] Llamando... (intento {intento}/{retries})")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=240
            )
            if result.returncode == 0:
                # Extraer respuesta del output de OpenCode
                lines = result.stdout.split('\n')
                resp = []
                capturing = False
                for line in lines:
                    if '> build' in line or 'minimax' in line.lower():
                        capturing = True
                        continue
                    elif capturing and line.startswith('$'):
                        break
                    elif capturing and line.strip():
                        resp.append(line.strip())

                output = '\n'.join(resp) if resp else result.stdout.strip()
                if len(output) < 200:
                    print(f"  [WARN] Respuesta muy corta: {len(output)} chars")
                    if intento < retries:
                        time.sleep(5)
                        continue
                    return None
                return output
            else:
                stderr = result.stderr[:200] if result.stderr else "sin stderr"
                print(
                    f"  [ERROR] OpenCode return code {result.returncode}: {stderr}")
        except subprocess.TimeoutExpired:
            print(f"  [ERROR] Timeout OpenCode (240s) en intento {intento}")
        except FileNotFoundError:
            print("[ERROR] 'opencode' no encontrado en PATH.")
            print("  ¿Estás en WSL o tiene OpenCode instalado?")
            return None
        except Exception as e:
            print(f"  [ERROR] OpenCode: {str(e)[:80]}")

        if intento < retries:
            espera = 5 * intento
            print(f"  [RETRY] Esperando {espera}s...")
            time.sleep(espera)

    return None


# ============================================================================
# CONSTRUCTOR DE PROMPT
# ============================================================================

def construir_prompt(datos_tsr, prompt_base):
    """Inyecta las 7 capas en el prompt maestro."""
    p = prompt_base
    p = p.replace("{TSR_ID}", str(datos_tsr["tsr_id"]))
    p = p.replace("{TITULO}", datos_tsr["titulo"])
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

def generar_monolito(datos_tsr, prompt_base):
    tsr_id = datos_tsr["tsr_id"]
    titulo = datos_tsr["titulo"]

    print(f"\n{'='*60}")
    print(f"[MONOLITO] TSR{tsr_id}: {titulo}")
    print(f"{'='*60}")

    # Reportar capas
    no_disponibles = [
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

    capas_ok = 0
    for nombre, campo in [("C0", "semilla"), ("C1", "bibliografia"),
                          ("C2", "genealogia"), ("C3", "problematizacion"),
                          ("C4", "resonancias"), ("C5", "metaanalisis"),
                          ("C6", "guion_taller"), ("C7", "caso_aplicacion")]:
        disponible = datos_tsr[campo] not in no_disponibles
        print(f"  {nombre}: {'OK' if disponible else 'FALTA'}")
        if disponible:
            capas_ok += 1
    print(f"  -> {capas_ok}/8 capas disponibles")

    if capas_ok < 5:
        print(f"  [SKIP] Menos de 5 capas — no hay suficiente materia prima")
        return False

    # Construir prompt
    prompt = construir_prompt(datos_tsr, prompt_base)
    prompt_words = len(prompt.split())
    print(
        f"  Prompt: {prompt_words:,} palabras (~{int(prompt_words*1.3):,} tokens)")

    # Llamar OpenCode
    resultado_raw = llamar_opencode(prompt)
    if not resultado_raw:
        print(f"  [FALLO] TSR{tsr_id}: sin respuesta")
        return False

    # Post-procesar
    resultado_final, palabras = postprocesar(resultado_raw)
    print(f"  Palabras: {palabras:,}")

    # Validar
    if palabras < 2000:
        print(f"  [ALERTA] Menos de 2,000 palabras — probablemente incompleto")
        nivel = "fuera"
    elif palabras < 2500:
        print(f"  [FLEX] 2,000-2,500 — aceptable con revisión")
        nivel = "flexible"
    elif palabras <= 4500:
        print(f"  [OK] En rango objetivo")
        nivel = "ok"
    else:
        print(
            f"  [FLEX] {palabras:,} palabras — más de 4,500, revisar extensión")
        nivel = "flexible"

    # Guardar .md
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUTPUT_DIR / f"TSR{tsr_id}_MONOLITO.md"

    contenido_md = f"""# TSR{tsr_id}: {titulo}

**Proyecto Ciclope · Mitologias Verbales**
**Sistema de Lectura de Segundo Orden (TRCO)**
**Fecha de compilacion:** {datetime.now().strftime('%d.%m.%Y')}
**Modelo:** opencode/minimax-m2.5-free
**Palabras:** {palabras}
**Validacion:** {nivel}
**Capas disponibles:** {capas_ok}/8

---

{resultado_final}

---

*Compilado por Ciclope · Monolito TSR{tsr_id}*
*Proyecto Ciclope · Mitologias Verbales · 2026*
"""
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(contenido_md)
    print(f"  [GUARDADO] {md_path.name}")

    # Verificar corte limpio
    ultima_linea = resultado_final.strip().split('\n')[-1].strip()
    if len(ultima_linea) > 3 and not ultima_linea.endswith(('.', ']', ')', '"', "'", '-', ':')):
        print(f"  [CUIDADO] El texto podria estar truncado al final")
        print(f"  Ultima linea: ...{ultima_linea[-60:]}")

    return True


# ============================================================================
# PARSER DE ARGUMENTOS SIMPLE
# ============================================================================

def parsear_args():
    """Parser simple de argumentos sin argparse."""
    args = {"tsrs": [], "dry_run": False}

    for arg in sys.argv[1:]:
        if arg == "--all":
            args["tsrs"] = list(range(TSR_MIN, TSR_MAX + 1))
        elif arg == "--dry-run":
            args["dry_run"] = True
        elif arg.startswith("--tsr="):
            try:
                args["tsrs"].append(int(arg.split("=")[1]))
            except ValueError:
                print(f"TSR invalido: {arg}")
        elif arg == "--tsr" and len(args["tsrs"]) == 0:
            # next arg should be the tsr number
            pass
        elif arg.isdigit():
            num = int(arg)
            if TSR_MIN <= num <= TSR_MAX:
                args["tsrs"].append(num)
            else:
                print(f"TSR fuera de rango ({TSR_MIN}-{TSR_MAX}): {num}")

    if not args["tsrs"] and not args["dry_run"]:
        args["tsrs"] = list(range(TSR_MIN, TSR_MAX + 1))

    return args


# ============================================================================
# MAIN
# ============================================================================

def main():
    args = parsear_args()

    print(f"""
+=============================================================+
|            CICLOPE · COMPILADOR MONOLITO V2                 |
|          De 7 capas a documentos autonomos                  |
|              {datetime.now().strftime('%d.%m.%Y %H:%M')}                            |
+=============================================================+
""")

    # CARGA DE DATOS
    print("[CARGA] Cargando 7 capas...")
    c0 = cargar_texto(CAPA0_PATH)
    c1 = cargar_json(CAPA1_PATH)
    c2 = cargar_json(CAPA2_PATH)
    c3 = cargar_json(CAPA3_PATH)
    c4 = cargar_json(CAPA4_PATH)
    c5 = cargar_json(CAPA5_PATH)
    c6 = cargar_json(CAPA6_PATH)
    c7 = cargar_json(CAPA7_PATH)

    for nombre, data in [("C0 semilla", c0), ("C1 bibliografia", c1),
                         ("C2 genealogia", c2), ("C3 problematizacion", c3),
                         ("C4 resonancias", c4), ("C5 metanalisis", c5),
                         ("C6 talleres", c6), ("C7 casos", c7)]:
        status = "OK" if data else "FALTA"
        if isinstance(data, dict):
            status = f"OK ({len(data)} items)"
        elif isinstance(data, str):
            status = f"OK ({len(data.split())} palabras)"
        print(f"  {nombre:<22} {status}")

    if not c2:
        print("[ERROR] CAPA2 es requerida. Abortando.")
        sys.exit(1)

    # Prompt maestro
    prompt_base = cargar_texto(PROMPT_PATH)
    if not prompt_base:
        print("[ERROR] PROMPT_MONOLITO.txt no encontrado.")
        print(f"  Buscando en: {PROMPT_PATH}")
        sys.exit(1)
    print(f"  Prompt monolito: OK ({len(prompt_base)} chars)")

    # DRY RUN
    if args["dry_run"]:
        print(f"\n[AUDITORIA] TSRs {args['tsrs'][0] if args['tsrs'] else TSR_MIN}"
              f"-{args['tsrs'][-1] if args['tsrs'] else TSR_MAX}")
        tsr_ids = args["tsrs"] if args["tsrs"] else list(
            range(TSR_MIN, TSR_MAX + 1))

        no_disp = [
            "Semilla no disponible.", "Semilla no encontrada para este TSR.",
            "Bibliografía no disponible.", "Sin fuentes registradas.",
            "Genealogía no disponible.", "Sin contenido genealógico.",
            "Problematización no disponible.", "Sin contenido.",
            "Resonancias no disponibles.", "Resonancias no encontradas.",
            "Meta-análisis no disponible.",
            "Guion de taller no disponible.", "Sin contenido de taller.",
            "Caso de aplicación no disponible.", "Sin contenido de caso."
        ]

        completos = 0
        parciales = 0
        for tsr_id in tsr_ids:
            datos = extraer_tsr_completo(
                tsr_id, c0, c1, c2, c3, c4, c5, c6, c7)
            capas = sum(1 for c in ["semilla", "bibliografia", "genealogia",
                                    "problematizacion", "resonancias", "metaanalisis",
                                    "guion_taller", "caso_aplicacion"]
                        if datos[c] not in no_disp)
            titulo = datos["titulo"][:45]
            icono = "OK" if capas == 8 else ("~" if capas >= 6 else "!")
            print(f"  TSR{tsr_id}: [{icono}] {capas}/8 capas — {titulo}")
            if capas == 8:
                completos += 1
            elif capas >= 6:
                parciales += 1

        print(f"\n  Completos (8/8): {completos}")
        print(f"  Parciales (6-7): {parciales}")
        print(f"  Incompletos (<6): {len(tsr_ids) - completos - parciales}")
        return

    # PROCESAR
    tsr_ids = args["tsrs"]
    print(f"\n[INFO] Procesando {len(tsr_ids)} TSR(s) con OpenCode...")

    exitosos = 0
    fallidos = []

    for i, tsr_id in enumerate(tsr_ids, 1):
        print(f"\n[{i}/{len(tsr_ids)}] TSR{tsr_id}")
        datos = extraer_tsr_completo(tsr_id, c0, c1, c2, c3, c4, c5, c6, c7)
        if generar_monolito(datos, prompt_base):
            exitosos += 1
        else:
            fallidos.append(tsr_id)

        if i < len(tsr_ids):
            pausa = 5
            print(f"  [PAUSA] {pausa}s antes del siguiente...")
            time.sleep(pausa)

    # RESUMEN
    print(f"""
{'='*60}
[RESUMEN]
{'='*60}
  Exitosos: {exitosos}/{len(tsr_ids)}
  Fallidos: {len(fallidos)}/{len(tsr_ids)}
  Salida: {OUTPUT_DIR}/""")

    if fallidos:
        tsr_str = " ".join(str(f) for f in fallidos)
        print(f"\n  Reintentar fallidos:")
        print(
            f"  python scripts/compilar_monolito_opencode.py --tsr={tsr_str}")


if __name__ == "__main__":
    main()
