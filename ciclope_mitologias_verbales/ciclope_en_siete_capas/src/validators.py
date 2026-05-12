"""
Validadores para las respuestas de la API y datos del proyecto.
"""
import re
import json
from typing import Dict, List, Tuple, Optional, Any
from .models import FuenteBibliografica

def extraer_json_de_respuesta(texto_raw: str) -> Optional[Dict]:
    """
    Extrae JSON de respuestas que pueden incluir texto extra o Markdown.
    Maneja múltiples formatos problemáticos.
    """
    if not texto_raw or not isinstance(texto_raw, str):
        return None
    
    # Caso 1: Respuesta es JSON puro (ideal)
    try:
        return json.loads(texto_raw)
    except json.JSONDecodeError:
        pass
    
    # Caso 2: JSON dentro de code block Markdown ```json ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', texto_raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Caso 3: Buscar primer { y último } válidos
    inicio = texto_raw.find('{')
    fin = texto_raw.rfind('}')
    if inicio != -1 and fin != -1 and inicio < fin:
        posible_json = texto_raw[inicio:fin+1]
        try:
            return json.loads(posible_json)
        except json.JSONDecodeError:
            pass
    
    # Caso 4: Limpiar comillas tipográficas Unicode
    texto_limpio = (
        texto_raw
        .replace('"', '"')
        .replace('"', '"')
        .replace('''''', "'")
        .replace('''''', "'")
        .replace('…', '...')
    )
    
    try:
        return json.loads(texto_limpio)
    except json.JSONDecodeError:
        pass
    
    # Caso 5: Intentar extraer después de limpiar y buscar de nuevo
    if inicio != -1 and fin != -1:
        posible_json = texto_limpio[inicio:fin+1]
        try:
            return json.loads(posible_json)
        except json.JSONDecodeError:
            pass
    
    return None

def validar_fuente(fuente: Dict) -> Tuple[bool, List[str]]:
    """
    Valida una fuente bibliográfica individual.
    Retorna (es_valido, lista_errores).
    """
    errores = []
    
    # Campos obligatorios
    campos_requeridos = [
        'bloque', 'autor', 'titulo', 'año', 'tipo', 
        'editorial_revista', 'url', 'relevancia'
    ]
    
    for campo in campos_requeridos:
        if campo not in fuente or not fuente[campo]:
            errores.append(f"Campo obligatorio faltante: {campo}")
    
    # Validar tipos de datos
    if 'año' in fuente and not isinstance(fuente['año'], int):
        try:
            fuente['año'] = int(fuente['año'])
        except (ValueError, TypeError):
            errores.append(f"Año inválido: {fuente['año']}")
    
    # Validar URL
    if 'url' in fuente and fuente['url']:
        if not re.match(r'^https?://', str(fuente['url'])):
            errores.append(f"URL inválida: {fuente['url']}")
    
    return len(errores) == 0, errores

def validar_bibliografia(bibliografia: Dict) -> Tuple[bool, List[str]]:
    """
    Valida la estructura completa de una bibliografía.
    Retorna (es_valido, lista_errores).
    """
    errores = []
    
    # Validar campos obligatorios
    campos_requeridos = ['tsr', 'titulo', 'cluster', 'fuentes']
    for campo in campos_requeridos:
        if campo not in bibliografia:
            errores.append(f"Falta campo obligatorio: {campo}")
    
    # Validar fuentes
    if 'fuentes' in bibliografia:
        if not isinstance(bibliografia['fuentes'], list):
            errores.append("El campo 'fuentes' debe ser una lista")
        else:
            # Validar cada fuente individualmente
            for i, fuente in enumerate(bibliografia['fuentes'], 1):
                es_valida, errores_fuente = validar_fuente(fuente)
                if not es_valida:
                    errores.append(f"Fuente {i}: {', '.join(errores_fuente)}")
    
    # Validar cobertura conceptual
    if 'cobertura_conceptual' in bibliografia:
        if not isinstance(bibliografia['cobertura_conceptual'], dict):
            errores.append("El campo 'cobertura_conceptual' debe ser un objeto")
    
    return len(errores) == 0, errores

def crear_estadisticas(resultados: List[Dict]) -> Dict:
    """
    Crea estadísticas a partir de una lista de resultados.
    """
    total_tsr = len(resultados)
    exitosos = sum(1 for r in resultados if 'error' not in r)
    fallidos = total_tsr - exitosos
    total_fuentes = sum(len(r.get('fuentes', [])) for r in resultados if 'error' not in r)
    
    return {
        'total_tsr': total_tsr,
        'exitosos': exitosos,
        'fallidos': fallidos,
        'total_fuentes': total_fuentes,
        'tasa_exito': (exitosos / total_tsr * 100) if total_tsr > 0 else 0
    }
