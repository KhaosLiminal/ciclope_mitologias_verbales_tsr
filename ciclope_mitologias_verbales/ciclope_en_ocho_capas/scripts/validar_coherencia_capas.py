#!/usr/bin/env python3
"""
VALIDADOR DE COHERENCIA ENTRE CAPAS - CÍCLOPE TSR
==================================================

Verifica que las capas 2-7 usen términos y conceptos consistentemente
según las definiciones canónicas del GLOSARIO_CICLOPE.json

Uso:
    python validar_coherencia_capas.py --capa CAPA3 --tsr 102
    python validar_coherencia_capas.py --capa CAPA4 --all
    python validar_coherencia_capas.py --validar-todo
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
GLOSARIO_PATH = BASE_DIR / "config" / "GLOSARIO_CICLOPE.json"
METADATOS_PATH = BASE_DIR / "config" / "METADATOS_PROYECTO.json"
CAPAS_DIR = BASE_DIR / "capas"

# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class UsoTermino:
    """Registro de uso de un término en una capa"""
    termino: str
    tsr_id: int
    capa: str
    contexto: str  # Fragmento de texto donde aparece
    linea: int
    definicion_usada: str = None  # Si especifica cuál definición usa

@dataclass
class Incoherencia:
    """Incoherencia detectada entre capas"""
    tipo: str  # 'definicion_divergente', 'falta_declaracion', 'contradiccion'
    termino: str
    tsr_id: int
    capa_origen: str
    capa_conflicto: str
    descripcion: str
    severidad: str  # 'critica', 'alta', 'media', 'baja'
    sugerencia: str = None

# ============================================================================
# CARGADORES DE DATOS
# ============================================================================

def cargar_glosario() -> Dict:
    """Carga el glosario canónico de términos"""
    with open(GLOSARIO_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def cargar_metadatos() -> Dict:
    """Carga metadata del proyecto"""
    with open(METADATOS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def cargar_capa(capa_nombre: str) -> Dict:
    """Carga datos de una capa específica"""
    # Mapeo de nombres de capas a directorios reales
    capa_directorios = {
        "CAPA2": "CAPA2_genealogia",
        "CAPA3": "CAPA3_problematizacion",
        "CAPA4": "CAPA4_resonancias",
        "CAPA5": "CAPA5_metanalisis",
        "CAPA6": "CAPA6_talleres",
        "CAPA7": "CAPA7_casos"
    }
    
    directorio = capa_directorios.get(capa_nombre, capa_nombre)
    capa_path = CAPAS_DIR / directorio / f"TSR_{capa_nombre}_FINAL.json"
    
    if not capa_path.exists():
        print(f"⚠️  CAPA {capa_nombre} no existe todavía: {capa_path}")
        return None
    
    with open(capa_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ============================================================================
# EXTRACTORES DE TÉRMINOS
# ============================================================================

def extraer_terminos_usados(texto: str, terminos_clave: List[str]) -> List[Tuple[str, str, int]]:
    """
    Extrae usos de términos clave en un texto.
    
    Returns:
        Lista de (termino, contexto, linea)
    """
    usos = []
    lineas = texto.split('\n')
    
    for termino in terminos_clave:
        # Buscar el término (case-insensitive, pero respetando palabra completa)
        patron = re.compile(r'\b' + re.escape(termino) + r'\b', re.IGNORECASE)
        
        for i, linea in enumerate(lineas, 1):
            if patron.search(linea):
                # Extraer contexto (50 chars antes y después)
                match = patron.search(linea)
                start = max(0, match.start() - 50)
                end = min(len(linea), match.end() + 50)
                contexto = linea[start:end]
                
                usos.append((termino, contexto, i))
    
    return usos

def detectar_definicion_usada(contexto: str, definiciones_posibles: List[str]) -> str:
    """
    Detecta cuál definición de un término se está usando basándose en el contexto.
    
    Por ejemplo, si el contexto menciona "Barthes" y "ficción moderna",
    probablemente se refiere a la definición barthesiana de "autor".
    """
    contexto_lower = contexto.lower()
    
    # Buscar marcadores explícitos
    for def_nombre in definiciones_posibles:
        if def_nombre.lower() in contexto_lower:
            return def_nombre
    
    # Si no hay marcador explícito, retornar None
    return None

# ============================================================================
# VALIDADORES
# ============================================================================

def validar_termino_en_tsr(
    tsr_data: Dict,
    tsr_id: int,
    capa: str,
    termino: str,
    definiciones_glosario: Dict
) -> List[Incoherencia]:
    """
    Valida el uso de un término en un TSR específico de una capa.
    """
    incoherencias = []
    
    # Obtener texto del TSR según la capa
    texto = obtener_texto_tsr(tsr_data, capa)
    
    if not texto:
        return incoherencias
    
    # Extraer usos del término
    usos = extraer_terminos_usados(texto, [termino])
    
    if not usos:
        return incoherencias  # No se usa el término, no hay problema
    
    # Verificar si el término tiene múltiples definiciones
    tiene_multiples_def = isinstance(definiciones_glosario.get(termino), dict) and \
                         len([k for k in definiciones_glosario[termino].keys() if k.startswith('definicion_')]) > 1
    
    if tiene_multiples_def:
        # Verificar que se declare cuál definición se usa
        for _, contexto, linea in usos:
            def_detectada = detectar_definicion_usada(
                contexto,
                [k for k in definiciones_glosario[termino].keys() if k.startswith('definicion_')]
            )
            
            if not def_detectada:
                incoherencias.append(Incoherencia(
                    tipo='falta_declaracion',
                    termino=termino,
                    tsr_id=tsr_id,
                    capa_origen=capa,
                    capa_conflicto=None,
                    descripcion=f"El término '{termino}' tiene múltiples definiciones en el glosario, pero no se declara cuál se usa.",
                    severidad='alta',
                    sugerencia=f"Especificar en el contexto: '{termino} (según Barthes/Foucault/Schlegel/etc.)'"
                ))
    
    return incoherencias

def validar_coherencia_entre_capas(
    capa_anterior: Dict,
    capa_actual: Dict,
    nombre_capa_anterior: str,
    nombre_capa_actual: str,
    terminos_clave: List[str]
) -> List[Incoherencia]:
    """
    Compara dos capas para detectar incoherencias en el uso de términos.
    """
    incoherencias = []
    
    # Para cada TSR, comparar el uso de términos clave
    for tsr_id in range(102, 121):
        tsr_anterior = obtener_tsr_de_capa(capa_anterior, tsr_id)
        tsr_actual = obtener_tsr_de_capa(capa_actual, tsr_id)
        
        if not tsr_anterior or not tsr_actual:
            continue
        
        texto_anterior = obtener_texto_tsr(tsr_anterior, nombre_capa_anterior)
        texto_actual = obtener_texto_tsr(tsr_actual, nombre_capa_actual)
        
        for termino in terminos_clave:
            # Extraer usos en ambas capas
            usos_anterior = extraer_terminos_usados(texto_anterior, [termino])
            usos_actual = extraer_terminos_usados(texto_actual, [termino])
            
            if usos_anterior and usos_actual:
                # Analizar si hay contradicción semántica
                # (Esto es simplificado; en versión real se necesitaría NLP)
                contradiccion = detectar_contradiccion_simple(
                    usos_anterior, usos_actual, termino
                )
                
                if contradiccion:
                    incoherencias.append(contradiccion)
    
    return incoherencias

def detectar_contradiccion_simple(
    usos_anterior: List[Tuple],
    usos_actual: List[Tuple],
    termino: str
) -> Incoherencia:
    """
    Detección simple de contradicciones basada en palabras clave opuestas.
    
    Por ejemplo: Si en CAPA2 dice "fragmento con promesa de totalidad"
    y en CAPA3 dice "fragmento sin promesa", eso es contradicción.
    """
    # Patrones contradictorios conocidos
    patrones_opuestos = {
        'fragmento': [
            (['con promesa', 'promesa de totalidad', 'síntesis'], 
             ['sin promesa', 'irresoluble', 'imposibilidad'])
        ],
        'aura': [
            (['destruida', 'eliminada', 'perdida'],
             ['resucitada', 'restaurada', 'recuperada'])
        ]
    }
    
    if termino not in patrones_opuestos:
        return None
    
    for positivos, negativos in patrones_opuestos[termino]:
        tiene_positivo_anterior = any(
            any(p in contexto.lower() for p in positivos)
            for _, contexto, _ in usos_anterior
        )
        tiene_negativo_actual = any(
            any(n in contexto.lower() for n in negativos)
            for _, contexto, _ in usos_actual
        )
        
        if tiene_positivo_anterior and tiene_negativo_actual:
            return Incoherencia(
                tipo='contradiccion',
                termino=termino,
                tsr_id=None,  # Se detecta a nivel general
                capa_origen='anterior',
                capa_conflicto='actual',
                descripcion=f"Contradicción en '{termino}': anterior usa '{positivos}', actual usa '{negativos}' sin declarar tensión dialéctica.",
                severidad='critica',
                sugerencia="Declarar explícitamente que se trata de una tensión dialéctica entre posiciones."
            )
    
    return None

# ============================================================================
# HELPERS
# ============================================================================

def obtener_texto_tsr(tsr_data: Dict, capa: str) -> str:
    """Extrae el texto del TSR según la estructura de cada capa"""
    if capa == "CAPA2":
        return tsr_data.get('genealogia', '')
    elif capa == "CAPA3":
        return tsr_data.get('problematizacion', '')
    elif capa == "CAPA4":
        return tsr_data.get('resonancia', '')
    elif capa == "CAPA5":
        return tsr_data.get('meta_analisis', '')
    elif capa == "CAPA6":
        return tsr_data.get('guion_taller', '')
    elif capa == "CAPA7":
        return tsr_data.get('caso_estudio', '')
    return ''

def obtener_tsr_de_capa(capa_data: Dict, tsr_id: int) -> Dict:
    """Obtiene datos de un TSR específico de una capa"""
    if not capa_data:
        return None
    
    estructura = capa_data.get('estructura', [])
    for tsr in estructura:
        if tsr.get('tsr_id') == tsr_id or tsr.get('tsr') == tsr_id:
            return tsr
    
    return None

# ============================================================================
# REPORTES
# ============================================================================

def generar_reporte_validacion(incoherencias: List[Incoherencia]) -> str:
    """Genera reporte legible de las incoherencias detectadas"""
    if not incoherencias:
        return "✅ NO SE DETECTARON INCOHERENCIAS\n"
    
    reporte = f"⚠️  INCOHERENCIAS DETECTADAS: {len(incoherencias)}\n\n"
    
    # Agrupar por severidad
    criticas = [i for i in incoherencias if i.severidad == 'critica']
    altas = [i for i in incoherencias if i.severidad == 'alta']
    medias = [i for i in incoherencias if i.severidad == 'media']
    bajas = [i for i in incoherencias if i.severidad == 'baja']
    
    for grupo, nombre in [(criticas, 'CRÍTICAS'), (altas, 'ALTAS'), (medias, 'MEDIAS'), (bajas, 'BAJAS')]:
        if grupo:
            reporte += f"{'='*60}\n"
            reporte += f"SEVERIDAD {nombre} ({len(grupo)} encontradas)\n"
            reporte += f"{'='*60}\n\n"
            
            for i in grupo:
                reporte += f"🔴 [{i.tipo.upper()}] Término: '{i.termino}'\n"
                if i.tsr_id:
                    reporte += f"   TSR: {i.tsr_id}\n"
                reporte += f"   Capa: {i.capa_origen}"
                if i.capa_conflicto:
                    reporte += f" ↔ {i.capa_conflicto}"
                reporte += f"\n"
                reporte += f"   Descripción: {i.descripcion}\n"
                if i.sugerencia:
                    reporte += f"   💡 Sugerencia: {i.sugerencia}\n"
                reporte += "\n"
    
    return reporte

# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Valida coherencia terminológica entre capas del proyecto Cíclope TSR'
    )
    parser.add_argument('--capa', help='Capa a validar (ej: CAPA3)')
    parser.add_argument('--tsr', type=int, help='TSR específico a validar (102-120)')
    parser.add_argument('--all', action='store_true', help='Validar todos los TSR')
    parser.add_argument('--validar-todo', action='store_true', help='Validar todas las capas existentes')
    parser.add_argument('--output', help='Archivo donde guardar el reporte')
    
    args = parser.parse_args()
    
    # Cargar glosario y metadatos
    print("📖 Cargando glosario...")
    glosario = cargar_glosario()
    metadatos = cargar_metadatos()
    
    terminos_rastreados = metadatos['validacion_coherencia']['terminos_clave_rastreados']
    
    print(f"✅ Glosario cargado: {len(terminos_rastreados)} términos clave a rastrear\n")
    
    incoherencias_totales = []
    
    if args.validar_todo:
        print("🔍 Validando todas las capas...\n")
        
        capas_disponibles = ['CAPA2', 'CAPA3', 'CAPA4', 'CAPA5', 'CAPA6', 'CAPA7']
        capas_cargadas = {}
        
        for nombre_capa in capas_disponibles:
            capa_data = cargar_capa(nombre_capa)
            if capa_data:
                capas_cargadas[nombre_capa] = capa_data
        
        # Validar coherencia entre capas consecutivas
        capas_ordenadas = sorted(capas_cargadas.keys())
        
        for i in range(len(capas_ordenadas) - 1):
            capa_ant = capas_ordenadas[i]
            capa_act = capas_ordenadas[i + 1]
            
            print(f"⚙️  Comparando {capa_ant} ↔ {capa_act}...")
            
            incoherencias = validar_coherencia_entre_capas(
                capas_cargadas[capa_ant],
                capas_cargadas[capa_act],
                capa_ant,
                capa_act,
                terminos_rastreados
            )
            
            incoherencias_totales.extend(incoherencias)
    
    elif args.capa:
        print(f"🔍 Validando {args.capa}...\n")
        
        capa_data = cargar_capa(args.capa)
        
        if not capa_data:
            print(f"❌ ERROR: No se pudo cargar {args.capa}")
            return
        
        # Validar cada término en cada TSR
        if args.all:
            tsr_range = range(102, 121)
        elif args.tsr:
            tsr_range = [args.tsr]
        else:
            print("❌ ERROR: Especifica --tsr N o --all")
            return
        
        for tsr_id in tsr_range:
            tsr_data = obtener_tsr_de_capa(capa_data, tsr_id)
            
            if not tsr_data:
                continue
            
            for termino in terminos_rastreados:
                incohs = validar_termino_en_tsr(
                    tsr_data,
                    tsr_id,
                    args.capa,
                    termino,
                    glosario['terminos_nucleares']
                )
                incoherencias_totales.extend(incohs)
    
    # Generar reporte
    reporte = generar_reporte_validacion(incoherencias_totales)
    print("\n" + "="*60)
    print("REPORTE DE VALIDACIÓN")
    print("="*60 + "\n")
    print(reporte)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(reporte)
        print(f"\n💾 Reporte guardado en: {args.output}")

if __name__ == '__main__':
    main()
