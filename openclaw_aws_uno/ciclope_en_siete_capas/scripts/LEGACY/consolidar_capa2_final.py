#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
consolidar_capa2_final.py
Consolida CAPA2 en un solo JSON y un solo MD
Última versión optimizada para economía de tokens
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any
import logging

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
CAPA2_DIR = BASE_DIR / "capas" / "CAPA2_genealogia"
OUTPUT_DIR = CAPA2_DIR
LOG_DIR = CAPA2_DIR / "logs"

# Asegurar directorios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configuración logging
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"consolidacion_final_{timestamp}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIONES
# ============================================================================

def cargar_metadatos() -> Dict:
    """Carga metadatos de TSRs"""
    metadatos_file = BASE_DIR / "config" / "tsr_metadatos.json"
    with open(metadatos_file, 'r', encoding='utf-8') as f:
        metadatos = json.load(f)
    return {item['numero']: item for item in metadatos}

def cargar_json_existente() -> Dict:
    """Carga JSON consolidado existente si existe"""
    json_file = CAPA2_DIR / "TSR_CAPA2_FINAL.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def extraer_mejor_genealogia(tsr_id: str, logs_dir: Path) -> Dict:
    """Extrae la mejor versión de genealogía del JSON consolidado existente"""
    
    # Primero intentar cargar desde el JSON existente
    json_file = CAPA2_DIR / "TSR_CAPA2_FINAL.json"
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                datos_json = json.load(f)
            
            # Buscar en la estructura del JSON
            if 'estructura' in datos_json:
                for item in datos_json['estructura']:
                    if str(item['tsr']) == tsr_id:
                        palabras = item.get('num_palabras', 0)
                        
                        return {
                            'tsr_id': tsr_id,
                            'palabras': palabras,
                            'fuente': 'TSR_CAPA2_FINAL.json',
                            'calidad': 'excelente' if palabras >= 600 else 'buena' if palabras >= 500 else 'regular',
                            'contenido': item.get('genealogia', ''),
                            'titulo': item.get('titulo', ''),
                            'archivo_origen': item.get('archivo_origen', ''),
                            'tamano_bytes': item.get('tamano_bytes', 0)
                        }
            
            # Si no está en estructura, buscar directamente
            elif tsr_id in datos_json:
                tsr_data = datos_json[tsr_id]
                palabras = tsr_data.get('palabras', 0)
                
                return {
                    'tsr_id': tsr_id,
                    'palabras': palabras,
                    'fuente': 'TSR_CAPA2_FINAL.json',
                    'calidad': 'excelente' if palabras >= 600 else 'buena' if palabras >= 500 else 'regular',
                    'contenido': tsr_data.get('contenido', '')
                }
        except Exception as e:
            logger.warning(f"Error leyendo JSON existente: {str(e)}")
    
    return None

def generar_md_consolidado(datos_json: Dict) -> str:
    """Genera un único archivo MD con todas las genealogías"""
    
    contenido_md = "# TSR CAPA 2: GENEALOGÍAS CONSOLIDADAS\n\n"
    contenido_md += f"**Total TSRs:** {len(datos_json)}\n"
    contenido_md += f"**Fecha:** {time.strftime('%d.%m.%Y')}\n"
    contenido_md += f"**Total palabras:** {sum(d['palabras'] for d in datos_json.values())}\n\n"
    contenido_md += "---\n\n"
    
    # Ordenar por número de TSR
    for tsr_id in sorted(datos_json.keys(), key=int):
        tsr_data = datos_json[tsr_id]
        
        contenido_md += f"# TSR {tsr_id}: {tsr_data['titulo']}\n\n"
        contenido_md += f"**Autor:** {tsr_data['autor']}\n"
        contenido_md += f"**Palabras:** {tsr_data['palabras']}\n"
        contenido_md += f"**Calidad:** {tsr_data.get('calidad', 'buena')}\n\n"
        contenido_md += f"{tsr_data['contenido']}\n\n"
        contenido_md += "---\n\n"
    
    return contenido_md

def main():
    """Función principal"""
    logger.info("🚀 Iniciando consolidación final de CAPA 2")
    
    # 1. Cargar metadatos
    logger.info("📚 Cargando metadatos...")
    metadatos = cargar_metadatos()
    
    # 2. Cargar JSON existente
    logger.info("📄 Cargando JSON existente...")
    datos_existentes = cargar_json_existente()
    
    # 3. Extraer mejores versiones
    logger.info("🔍 Extrayendo mejores versiones de genealogías...")
    datos_consolidados = {}
    
    for tsr_id in metadatos.keys():
        if tsr_id == '101':  # Skip TSR101
            continue
            
        mejor_version = extraer_mejor_genealogia(tsr_id, LOG_DIR)
        
        if mejor_version:
            # Enriquecer con metadatos
            metadata = metadatos[tsr_id]
            datos_consolidados[tsr_id] = {
                **mejor_version,
                'titulo': metadata['titulo'],
                'autor': metadata['autor_primario'],
                'obra': metadata['obra_primaria'],
                'año': metadata['año'],
                'concepto_central': metadata['concepto_central'],
                'cluster': metadata['cluster'],
                'keywords': metadata['keywords'],
                'conexion_RH': metadata['conexion_RH']
            }
            
            # Si existe en JSON anterior, agregar contenido
            if tsr_id in datos_existentes:
                datos_consolidados[tsr_id]['contenido'] = datos_existentes[tsr_id].get('contenido', '')
            
            logger.info(f"✅ TSR {tsr_id}: {mejor_version['palabras']} palabras ({mejor_version['calidad']})")
        else:
            logger.warning(f"⚠️ TSR {tsr_id}: No se encontró versión")
    
    # 4. Guardar JSON consolidado
    logger.info("💾 Guardando JSON consolidado...")
    json_file = OUTPUT_DIR / "TSR_CAPA2_FINAL_CONSOLIDADO.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(datos_consolidados, f, ensure_ascii=False, indent=2)
    
    # 5. Generar MD consolidado
    logger.info("📝 Generando MD consolidado...")
    contenido_md = generar_md_consolidado(datos_consolidados)
    md_file = OUTPUT_DIR / "TSR_CAPA2_FINAL_CONSOLIDADO.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(contenido_md)
    
    # 6. Estadísticas finales
    total_tsr = len(datos_consolidados)
    total_palabras = sum(d['palabras'] for d in datos_consolidados.values())
    promedio = total_palabras / total_tsr if total_tsr > 0 else 0
    
    logger.info("\n" + "="*60)
    logger.info("📊 ESTADÍSTICAS FINALES")
    logger.info("="*60)
    logger.info(f"✅ TSRs procesados: {total_tsr}")
    logger.info(f"📚 Total palabras: {total_palabras:,}")
    logger.info(f"📈 Promedio por TSR: {promedio:.0f} palabras")
    logger.info(f"📁 JSON guardado: {json_file}")
    logger.info(f"📄 MD guardado: {md_file}")
    logger.info("="*60)
    
    return 0

if __name__ == "__main__":
    import time
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Consolidación cancelada por usuario")
        exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
