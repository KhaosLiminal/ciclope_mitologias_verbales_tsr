#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraer_texto_capa3.py - Extracción AGRESIVA de texto plano de CAPA 3
===========================================================

Extrae TODO el contenido textual de TSR_CAPA3_FINAL.json
Método lento pero agresivo: recursivo, sin filtros, todo adentro.
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
import re

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
CAPA3_PATH = BASE_DIR / "capas" / "CAPA3_problematizacion" / "TSR_CAPA3_FINAL.json"
OUTPUT_DIR = BASE_DIR / "outputs" / "TEXTO_CAPA3_EXTRAIDO"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp para archivos
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================================
# EXTRACTOR AGRESIVO
# ============================================================================

class ExtractorAgresivo:
    """Extractor que NO perdona nada de texto"""
    
    def __init__(self):
        self.texto_completo = []
        self.estadisticas = {
            'caracteres_total': 0,
            'palabras_total': 0,
            'lineas_total': 0,
            'tsr_procesados': 0,
            'caminos_encontrados': set(),
            'textos_plano': [],
            'metadata_extraida': []
        }
    
    def extraer_recursivo(self, obj: Any, camino: str = "") -> None:
        """
        Extrae texto de manera recursiva y agresiva.
        NO FILTRA NADA. TODO VA ADENTRO.
        """
        if isinstance(obj, str):
            # Texto plano encontrado
            self.texto_completo.append(obj)
            self.estadisticas['caracteres_total'] += len(obj)
            self.estadisticas['palabras_total'] += len(obj.split())
            self.estadisticas['lineas_total'] += obj.count('\n') + 1
            self.estadisticas['caminos_encontrados'].add(camino)
            
            # Guardar texto plano individual
            if len(obj.strip()) > 10:  # Ignorar textos muy cortos
                self.estadisticas['textos_plano'].append({
                    'camino': camino,
                    'texto': obj,
                    'caracteres': len(obj),
                    'palabras': len(obj.split())
                })
        
        elif isinstance(obj, dict):
            # Recorrer diccionario
            for key, value in obj.items():
                nuevo_camino = f"{camino}.{key}" if camino else key
                self.extraer_recursivo(value, nuevo_camino)
                
                # Extraer metadata si parece relevante
                if isinstance(key, str) and any(palabra in key.lower() 
                    for palabra in ['fecha', 'modelo', 'tsr', 'palabras', 'generacion']):
                    self.estadisticas['metadata_extraida'].append({
                        'campo': key,
                        'valor': str(value),
                        'camino': nuevo_camino
                    })
        
        elif isinstance(obj, list):
            # Recorrer lista
            for i, item in enumerate(obj):
                nuevo_camino = f"{camino}[{i}]" if camino else f"[{i}]"
                self.extraer_recursivo(item, nuevo_camino)
        
        elif obj is not None:
            # Cualquier otro tipo (números, booleanos, etc.)
            texto_repr = str(obj)
            if texto_repr and texto_repr != 'None':
                self.texto_completo.append(texto_repr)
                self.estadisticas['caminos_encontrados'].add(f"{camino} (repr)")
    
    def procesar_capa3(self) -> Dict:
        """Procesa el archivo CAPA3 completo"""
        print("🔥 INICIANDO EXTRACCIÓN AGRESIVA DE CAPA 3")
        print("=" * 60)
        
        if not CAPA3_PATH.exists():
            raise FileNotFoundError(f"No existe: {CAPA3_PATH}")
        
        # Cargar JSON
        print(f"📁 Cargando: {CAPA3_PATH}")
        with open(CAPA3_PATH, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        print(f"✅ JSON cargado: {len(str(datos)):,} caracteres")
        print()
        
        # Extracción agresiva
        print("🔪 EXTRAYENDO TEXTO (modo agresivo)...")
        inicio = time.time()
        
        self.extraer_recursivo(datos)
        
        fin = time.time()
        duracion = fin - inicio
        
        print(f"⚡ Extracción completada en {duracion:.2f} segundos")
        print()
        
        # Estadísticas finales
        self.estadisticas['tsr_procesados'] = len([t for t in self.estadisticas['textos_plano'] 
                                                  if 'tsr' in t['camino'].lower() and 'problematizacion' in t['camino']])
        
        return self.generar_reporte()
    
    def generar_reporte(self) -> Dict:
        """Genera reporte completo de la extracción"""
        print("📊 GENERANDO REPORTE DE EXTRACCIÓN")
        print("-" * 40)
        
        # Estadísticas generales
        print(f"📈 Estadísticas:")
        print(f"   • Caracteres totales: {self.estadisticas['caracteres_total']:,}")
        print(f"   • Palabras totales: {self.estadisticas['palabras_total']:,}")
        print(f"   • Líneas totales: {self.estadisticas['lineas_total']:,}")
        print(f"   • TSRs con problematización: {self.estadisticas['tsr_procesados']}")
        print(f"   • Textos plano extraídos: {len(self.estadisticas['textos_plano'])}")
        print(f"   • Caminos únicos: {len(self.estadisticas['caminos_encontrados'])}")
        print()
        
        # Análisis de textos principales
        textos_principales = [t for t in self.estadisticas['textos_plano'] 
                            if 'problematizacion' in t['camino']]
        
        print("📝 TEXTOS PRINCIPALES (PROBLEMATIZACIONES):")
        for texto in textos_principales:
            tsr_match = re.search(r'tsr[:\s]*(\d+)', texto['camino'], re.IGNORECASE)
            tsr_num = tsr_match.group(1) if tsr_match else "??"
            print(f"   • TSR {tsr_num}: {texto['palabras']:,} palabras ({texto['caracteres']:,} chars)")
        print()
        
        # Guardar archivos
        return self.guardar_resultados()
    
    def guardar_resultados(self) -> Dict:
        """Guarda todos los resultados en archivos"""
        print("💾 GUARDANDO RESULTADOS...")
        
        archivos_generados = {}
        
        # 1. Texto completo unificado
        texto_unificado = "\n\n".join([t for t in self.texto_completo if len(t.strip()) > 10])
        archivo_unificado = OUTPUT_DIR / f"CAPA3_TEXTO_COMPLETO_{timestamp}.txt"
        
        with open(archivo_unificado, 'w', encoding='utf-8') as f:
            f.write(f"# TEXTO COMPLETO CAPA 3 - EXTRAÍDO AGRESIVAMENTE\n")
            f.write(f"# Fecha: {datetime.now().isoformat()}\n")
            f.write(f"# TSRs: {self.estadisticas['tsr_procesados']}\n")
            f.write(f"# Palabras: {self.estadisticas['palabras_total']:,}\n")
            f.write(f"# Caracteres: {self.estadisticas['caracteres_total']:,}\n")
            f.write("=" * 80 + "\n\n")
            f.write(texto_unificado)
        
        archivos_generados['texto_completo'] = str(archivo_unificado)
        print(f"   ✅ Texto completo: {archivo_unificado.name}")
        
        # 2. Problematicaciones individuales
        archivo_problematicaciones = OUTPUT_DIR / f"CAPA3_PROBLEMATIZACIONES_{timestamp}.md"
        
        with open(archivo_problematicaciones, 'w', encoding='utf-8') as f:
            f.write(f"# CAPA 3: PROBLEMATIZACIONES INDIVIDUALES\n\n")
            f.write(f"**Fecha extracción:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"**Total TSRs:** {self.estadisticas['tsr_procesados']}\n\n")
            f.write("---\n\n")
            
            textos_problematizacion = [t for t in self.estadisticas['textos_plano'] 
                                     if 'problematizacion' in t['camino']]
            
            for texto in textos_problematizacion:
                tsr_match = re.search(r'tsr[:\s]*(\d+)', texto['camino'], re.IGNORECASE)
                tsr_num = tsr_match.group(1) if tsr_match else "??"
                
                f.write(f"## TSR {tsr_num}\n\n")
                f.write(f"**Palabras:** {texto['palabras']:,}\n")
                f.write(f"**Caracteres:** {texto['caracteres']:,}\n")
                f.write(f"**Camino:** `{texto['camino']}`\n\n")
                f.write(texto['texto'])
                f.write("\n\n---\n\n")
        
        archivos_generados['problematicaciones'] = str(archivo_problematicaciones)
        print(f"   ✅ Problematicaciones: {archivo_problematicaciones.name}")
        
        # 3. Estadísticas detalladas
        archivo_stats = OUTPUT_DIR / f"CAPA3_ESTADISTICAS_{timestamp}.json"
        
        # Convertir set a list para JSON serialización
        stats_para_json = self.estadisticas.copy()
        stats_para_json['caminos_encontrados'] = list(self.estadisticas['caminos_encontrados'])
        
        with open(archivo_stats, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'estadisticas': stats_para_json,
                'archivos_generados': archivos_generados
            }, f, indent=2, ensure_ascii=False)
        
        archivos_generados['estadisticas'] = str(archivo_stats)
        print(f"   ✅ Estadísticas: {archivo_stats.name}")
        
        # 4. Metadata extraída
        if self.estadisticas['metadata_extraida']:
            archivo_metadata = OUTPUT_DIR / f"CAPA3_METADATA_{timestamp}.txt"
            
            with open(archivo_metadata, 'w', encoding='utf-8') as f:
                f.write("# METADATA EXTRAÍDA DE CAPA 3\n\n")
                for meta in self.estadisticas['metadata_extraida']:
                    f.write(f"**{meta['campo']}**: {meta['valor']}\n")
                    f.write(f"   Camino: `{meta['camino']}`\n\n")
            
            archivos_generados['metadata'] = str(archivo_metadata)
            print(f"   ✅ Metadata: {archivo_metadata.name}")
        
        # 5. Análisis de caminos
        archivo_caminos = OUTPUT_DIR / f"CAPA3_CAMINOS_{timestamp}.txt"
        
        with open(archivo_caminos, 'w', encoding='utf-8') as f:
            f.write("# CAMINOS ENCONTRADOS EN CAPA 3\n\n")
            f.write(f"Total caminos únicos: {len(self.estadisticas['caminos_encontrados'])}\n\n")
            
            for camino in sorted(self.estadisticas['caminos_encontrados']):
                f.write(f"• {camino}\n")
        
        archivos_generados['caminos'] = str(archivo_caminos)
        print(f"   ✅ Caminos: {archivo_caminos.name}")
        
        print()
        print(f"🎁 TODOS LOS ARCHIVOS GUARDADOS EN: {OUTPUT_DIR}")
        print()
        
        return archivos_generados

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal de extracción agresiva"""
    try:
        extractor = ExtractorAgresivo()
        archivos = extractor.procesar_capa3()
        
        print("🎉 EXTRACCIÓN AGRESIVA COMPLETADA")
        print("=" * 60)
        print("📁 Archivos generados:")
        for tipo, path in archivos.items():
            print(f"   • {tipo}: {Path(path).name}")
        print()
        print("⚡ LISTO PARA ANÁLISIS POSTERIOR")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
