#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consolidar_capa2_json.py (Windows-compatible, sin emojis)
"""

import json
from pathlib import Path
from datetime import datetime
import re
import sys

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_MD_DIR = Path(__file__).parent.parent / "outputs" / "TSR_CAPA2_Genealogias_Batch"
OUTPUT_JSON = Path(__file__).parent.parent / "capas" / "CAPA2_genealogia" / "TSR_CAPA2_FINAL.json"

def contar_palabras(texto):
    return len(texto.split())

def extraer_titulo(contenido):
    lineas = contenido.split('\n')
    for linea in lineas:
        if linea.strip().startswith('#'):
            return linea.strip().lstrip('#').strip()
    return "Sin titulo"

def limpiar_markdown(contenido):
    contenido = re.sub(r'\n{3,}', '\n\n', contenido)
    contenido = '\n'.join(line.rstrip() for line in contenido.split('\n'))
    return contenido.strip()

def consolidar_capa2():
    print("=" * 70)
    print("CONSOLIDACION DE CAPA 2: GENEALOGIAS CONCEPTUALES")
    print("=" * 70)
    print()
    
    if not OUTPUT_MD_DIR.exists():
        print(f"[ERROR] No se encontro el directorio {OUTPUT_MD_DIR}")
        return False
    
    print(f"[INFO] Leyendo genealogias desde: {OUTPUT_MD_DIR}")
    print()
    
    estructura = []
    errores = []
    
    for tsr_id in range(102, 121):
        md_file = OUTPUT_MD_DIR / f"TSR_{tsr_id}_genealogia.md"
        
        if not md_file.exists():
            errores.append(f"TSR_{tsr_id}: Archivo no encontrado")
            print(f"[WARN] TSR {tsr_id}: Archivo no encontrado")
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            if len(contenido.strip()) < 100:
                errores.append(f"TSR_{tsr_id}: Contenido muy corto")
                print(f"[WARN] TSR {tsr_id}: Contenido muy corto")
                continue
            
            contenido_limpio = limpiar_markdown(contenido)
            titulo = extraer_titulo(contenido_limpio)
            num_palabras = contar_palabras(contenido_limpio)
            
            estructura.append({
                "tsr": tsr_id,
                "titulo": titulo,
                "genealogia": contenido_limpio,
                "num_palabras": num_palabras,
                "archivo_origen": md_file.name,
                "tamano_bytes": md_file.stat().st_size
            })
            
            print(f"[OK] TSR {tsr_id}: {num_palabras} palabras - {titulo[:50]}...")
            
        except Exception as e:
            errores.append(f"TSR_{tsr_id}: {str(e)}")
            print(f"[ERROR] TSR {tsr_id}: {str(e)}")
    
    print()
    print("-" * 70)
    
    if len(estructura) < 19:
        print(f"[WARN] Solo se encontraron {len(estructura)}/19 genealogias")
    else:
        print(f"[OK] Se consolidaron exitosamente las 19 genealogias")
    
    total_palabras = sum(t['num_palabras'] for t in estructura)
    promedio_palabras = total_palabras / len(estructura) if estructura else 0
    min_palabras = min(t['num_palabras'] for t in estructura) if estructura else 0
    max_palabras = max(t['num_palabras'] for t in estructura) if estructura else 0
    
    print()
    print("ESTADISTICAS:")
    print(f"   Total palabras: {total_palabras:,}")
    print(f"   Promedio por TSR: {promedio_palabras:.0f} palabras")
    print(f"   Rango: {min_palabras} - {max_palabras} palabras")
    
    resultado = {
        "metadata": {
            "capa": "CAPA 2: Genealogia conceptual",
            "descripcion": "Rastreo historico-conceptual de cada termino clave",
            "fecha_consolidacion": datetime.now().isoformat(),
            "total_tsr": len(estructura),
            "fuente": "outputs/TSR_CAPA2_Genealogias_Batch/",
            "modelo": "Perplexity Sonar Pro",
            "generado_por": "Windsurf IDE + script consolidacion",
            "estadisticas": {
                "total_palabras": total_palabras,
                "promedio_palabras": round(promedio_palabras, 2),
                "min_palabras": min_palabras,
                "max_palabras": max_palabras,
                "dispersion": max_palabras - min_palabras
            }
        },
        "estructura": estructura,
        "errores": errores if errores else None
    }
    
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"[SAVED] JSON guardado en: {OUTPUT_JSON}")
    print(f"   Tamano archivo: {OUTPUT_JSON.stat().st_size / 1024:.1f} KB")
    
    if errores:
        print()
        print("[WARN] ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"   - {error}")
    
    print()
    print("=" * 70)
    print("[SUCCESS] CONSOLIDACION COMPLETADA")
    print("=" * 70)
    return True

if __name__ == '__main__':
    try:
        exito = consolidar_capa2()
        if exito:
            print()
            print("Siguiente paso:")
            print("   python scripts/validar_coherencia_capas.py --capa CAPA2 --all")
        exit(0 if exito else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
