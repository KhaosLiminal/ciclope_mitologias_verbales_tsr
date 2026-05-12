#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de CodeMaps con metadatos enriquecidos para el proyecto Cíclope.

Este script analiza la estructura del proyecto y genera una representación visual
interactiva con metadatos detallados sobre cada componente.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import networkx as nx
from pyvis.network import Network

class CodeMapGenerator:
    # ... (código completo de la clase como se mostró anteriormente)

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Genera un CodeMap interactivo del proyecto.')
    parser.add_argument('--dir', type=str, default='.', 
                       help='Directorio raíz del proyecto (por defecto: directorio actual)')
    parser.add_argument('--output-html', type=str, 
                       help='Ruta de salida para el HTML interactivo')
    parser.add_argument('--output-json', type=str, 
                       help='Ruta de salida para el archivo JSON de metadatos')
    
    args = parser.parse_args()
    
    # Crear generador y analizar proyecto
    print("🚀 Iniciando generación de CodeMap...")
    generator = CodeMapGenerator(args.dir)
    generator.analyze_project_structure()
    
    # Generar visualización interactiva
    html_path = generator.generate_visualization(args.output_html)
    
    # Exportar metadatos
    json_path = generator.export_metadata(args.output_json)
    
    print("\n🎉 Proceso completado exitosamente!")
    print(f"- Visualización interactiva: {html_path}")
    print(f"- Metadatos completos: {json_path}")
    print("\n💡 Abre el archivo HTML en tu navegador para explorar el CodeMap interactivo.")

if __name__ == "__main__":
    main()
    