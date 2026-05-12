#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TSR_CAPA2_Estandarizacion.py
Estandariza las genealogías según la auditoría realizada
"""

import json
import os
import requests
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SONAR_API_URL = "https://api.perplexity.ai/chat/completions"
SONAR_MODEL = "sonar-pro"

# Configuración de API
SONAR_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not SONAR_API_KEY:
    raise ValueError("ERROR: PERPLEXITY_API_KEY no está configurada")

HEADERS = {
    "Authorization": f"Bearer {SONAR_API_KEY}",
    "Content-Type": "application/json"
}

# Configuración de reintentos
MAX_ATTEMPTS = 3
INITIAL_DELAY = 5  # segundos
TIMEOUT = 180  # segundos

# Directorios
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "resultados" / "TSR_CAPA2_Genealogias_Batch"
LOG_DIR = BASE_DIR / "logs" / "CAPA2_Estandarizacion"

# Asegurar que existan los directorios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de logging
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"estandarizacion_{timestamp}.log"
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
# FUNCIONES AUXILIARES
# ============================================================================

def make_api_call(prompt: str, max_tokens: int = 4000) -> Optional[Dict]:
    """Realiza una llamada a la API de Perplexity."""
    messages = [
        {
            "role": "system",
            "content": "Eres un experto en filosofía, teoría crítica y estudios culturales. Tu tarea es generar análisis genealógicos profundos y bien documentados."
        },
        {"role": "user", "content": prompt}
    ]
    
    data = {
        "model": SONAR_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
    }
    
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.post(
                SONAR_API_URL,
                headers=HEADERS,
                json=data,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            delay = INITIAL_DELAY * (2 ** attempt)
            logger.warning(f"Intento {attempt + 1}/{MAX_ATTEMPTS} fallido: {str(e)}. Reintentando en {delay}s...")
            time.sleep(delay)
    
    return None

def leer_genealogia_existente(archivo: Path) -> Dict:
    """Lee una genealogía existente y extrae su contenido."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Extraer título
        titulo_match = re.search(r'^# (.+)$', contenido, re.MULTILINE)
        titulo = titulo_match.group(1) if titulo_match else "Sin título"
        
        # Extraer contenido principal
        contenido_principal = contenido
        if '## Referencias' in contenido:
            contenido_principal = contenido.split('## Referencias')[0]
        
        # Eliminar título del contenido principal
        contenido_principal = re.sub(r'^# .+$\n\n', '', contenido_principal, flags=re.MULTILINE)
        
        return {
            'titulo': titulo,
            'contenido': contenido_principal.strip(),
            'palabras': len(contenido_principal.split()),
            'archivo': archivo
        }
    except Exception as e:
        logger.error(f"Error al leer {archivo}: {str(e)}")
        return None

def generar_seccion_rh(concepto: str, autor: str) -> str:
    """Genera la sección de Resonancias en Reflejos Híbridos."""
    prompt = f"""
    Genera una sección de 100-150 palabras sobre "Resonancias en Reflejos Híbridos" para el concepto: "{concepto}" de {autor}.
    
    La sección debe conectar el concepto con:
    - Universo Silicon Blood
    - Glitch Ritual
    - Identidades fragmentadas
    - El ecosistema narrativo de Reflejos Híbridos
    
    Usa un estilo académico pero accesible, con densidad conceptual.
    No incluyas encabezados, solo el texto de la sección.
    """
    
    response = make_api_call(prompt, max_tokens=1000)
    if not response or "choices" not in response or not response["choices"]:
        return f"[Sección RH pendiente para {concepto}]"
    
    try:
        content = response["choices"][0]["message"]["content"]
        # Limpiar el contenido
        if "```" in content:
            content = re.sub(r'```[^`]*```', '', content).strip()
        return content
    except Exception as e:
        logger.error(f"Error generando sección RH: {str(e)}")
        return f"[Error generando sección RH para {concepto}]"

def generar_referencias_apa(concepto: str, contenido: str) -> List[str]:
    """Genera referencias en formato APA basadas en el contenido."""
    prompt = f"""
    Extrae las referencias bibliográficas mencionadas en este texto sobre "{concepto}" y formátelas en APA 7ma edición.
    
    Si no hay suficientes referencias explícitas, genera referencias relevantes basadas en el contenido.
    
    Texto:
    {contenido}
    
    Devuelve SOLO las referencias, una por línea, en formato APA completo.
    """
    
    response = make_api_call(prompt, max_tokens=1500)
    if not response or "choices" not in response or not response["choices"]:
        return ["[Referencias pendientes]"]
    
    try:
        content = response["choices"][0]["message"]["content"]
        # Limpiar y procesar
        if "```" in content:
            content = re.sub(r'```[^`]*```', '', content).strip()
        
        # Dividir por líneas y limpiar
        referencias = [ref.strip() for ref in content.split('\n') if ref.strip()]
        return referencias[:5]  # Máximo 5 referencias
    except Exception as e:
        logger.error(f"Error generando referencias: {str(e)}")
        return ["[Error generando referencias]"]

def estandarizar_estructura(genealogia: Dict) -> Dict:
    """Estandariza la estructura de una genealogía."""
    contenido = genealogia['contenido']
    
    # 1. Eliminar títulos duplicados
    lineas = contenido.split('\n')
    lineas_filtradas = []
    for i, linea in enumerate(lineas):
        if linea.startswith('# '):
            if i == 0:  # Mantener solo el primer título
                lineas_filtradas.append(linea)
            else:
                # Convertir títulos H1 adicionales a H2
                lineas_filtradas.append(linea.replace('# ', '## '))
        else:
            lineas_filtradas.append(linea)
    
    contenido = '\n'.join(lineas_filtradas)
    
    # 2. Verificar secciones estándar
    secciones_requeridas = [
        "## Origen y Contexto Histórico",
        "## Desarrollo Conceptual", 
        "## Críticas y Debates Actuales",
        "## Resonancias en Reflejos Híbridos"
    ]
    
    # Si no tienen las secciones, agregarlas (esto requeriría regeneración)
    for seccion in secciones_requeridas:
        if seccion not in contenido:
            logger.warning(f"Falta sección: {seccion}")
    
    return {
        'titulo': genealogia['titulo'],
        'contenido': contenido,
        'palabras': genealogia['palabras'],
        'archivo': genealogia['archivo']
    }

def guardar_genealogia_estandarizada(tsr_id: str, datos: Dict, seccion_rh: str, referencias: List[str]) -> bool:
    """Guarda la genealogía con formato estandarizado."""
    try:
        output_file = OUTPUT_DIR / f"TSR_{tsr_id}_genealogia.md"
        
        # Formatear el contenido en Markdown estandarizado
        contenido_formateado = f"""# {datos['titulo']}

## Origen y Contexto Histórico
{extraer_seccion(datos['contenido'], 'Origen')}

## Desarrollo Conceptual
{extraer_seccion(datos['contenido'], 'Desarrollo')}

## Críticas y Debates Actuales
{extraer_seccion(datos['contenido'], 'Crítica')}

## Resonancias en Reflejos Híbridos
{seccion_rh}

## Referencias
{chr(10).join(f"- {ref}" for ref in referencias)}
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(contenido_formateado)
        
        word_count = len(contenido_formateado.split())
        logger.info(f"Guardado: {output_file.name} ({word_count} palabras)")
        return True
    except Exception as e:
        logger.error(f"Error al guardar {tsr_id}: {str(e)}")
        return False

def extraer_seccion(contenido: str, tipo: str) -> str:
    """Extrae una sección específica del contenido."""
    patrones = {
        'Origen': [r'## Origen.*?(?=##|$)', r'## Fase 1.*?(?=##|$)', r'Origen.*?(?=##|$)'],
        'Desarrollo': [r'## Desarrollo.*?(?=##|$)', r'## Fase 2.*?(?=##|$)', r'Desarrollo.*?(?=##|$)'],
        'Crítica': [r'## Crític.*?(?=##|$)', r'## Fase 3.*?(?=##|$)', r'Crític.*?(?=##|$)']
    }
    
    for patron in patrones.get(tipo, []):
        match = re.search(patron, contenido, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return f"[Sección de {tipo} pendiente de desarrollo]"

def main():
    """Función principal de estandarización."""
    logger.info("Iniciando proceso de estandarización de genealogías")
    
    # Obtener todos los archivos de genealogías
    archivos_genealogias = list(OUTPUT_DIR.glob("TSR_*_genealogia.md"))
    archivos_genealogias.sort()
    
    logger.info(f"Se encontraron {len(archivos_genealogias)} genealogías para procesar")
    
    # Metadatos para obtener conceptos
    metadatos_file = BASE_DIR.parent / "datos" / "tsr_metadatos.json"
    with open(metadatos_file, 'r', encoding='utf-8') as f:
        metadatos = json.load(f)
    
    # Crear diccionario de metadatos
    metadatos_dict = {item['numero']: item for item in metadatos}
    
    procesados = 0
    exitosos = 0
    
    for archivo in archivos_genealogias:
        tsr_id = archivo.stem.split('_')[1]  # Extraer número del TSR
        
        logger.info(f"\n{'='*80}")
        logger.info(f"PROCESANDO: TSR_{tsr_id}")
        logger.info(f"{'='*80}")
        
        # Leer genealogía existente
        genealogia = leer_genealogia_existente(archivo)
        if not genealogia:
            continue
        
        # Estandarizar estructura
        genealogia_estandar = estandarizar_estructura(genealogia)
        
        # Obtener metadatos
        metadata = metadatos_dict.get(tsr_id, {})
        concepto = metadata.get('titulo', 'Concepto desconocido')
        autor = metadata.get('autor_primario', 'Autor desconocido')
        
        # Generar sección RH
        logger.info("Generando sección de Resonancias en Reflejos Híbridos...")
        seccion_rh = generar_seccion_rh(concepto, autor)
        
        # Generar referencias APA
        logger.info("Generando referencias en formato APA...")
        referencias = generar_referencias_apa(concepto, genealogia_estandar['contenido'])
        
        # Guardar versión estandarizada
        if guardar_genealogia_estandarizada(tsr_id, genealogia_estandar, seccion_rh, referencias):
            exitosos += 1
        
        procesados += 1
        time.sleep(3)  # Pausa entre procesamientos
    
    logger.info("\n" + "="*50)
    logger.info("PROCESO COMPLETADO")
    logger.info("="*50)
    logger.info(f"Procesados: {procesados}/{len(archivos_genealogias)}")
    logger.info(f"Exitosos: {exitosos}/{procesados}")
    logger.info(f"Log guardado en: {log_file}")
    logger.info("="*50 + "\n")

if __name__ == "__main__":
    main()
