"""
Funciones de utilidad para el proyecto Cíclope.
"""
import os
import time
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, TypeVar, Type
from functools import wraps
import random
import os
import time
import json
from datetime import datetime

T = TypeVar('T')

def retry_with_backoff(
    retries: int = 3, 
    backoff_in_seconds: int = 1,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorador para reintentar una función con backoff exponencial.
    
    Args:
        retries: Número máximo de reintentos
        backoff_in_seconds: Tiempo base de espera entre reintentos (se duplica en cada intento)
        exceptions: Tupla de excepciones que activan el reintento
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if x == retries - 1:  # Último intento
                        raise e
                    else:
                        # Backoff exponencial con jitter
                        sleep = (backoff_in_seconds * 2 ** x + 
                               random.uniform(0, 1))
                        time.sleep(sleep)
                        x += 1
        return wrapper
    return decorator

def guardar_archivo(
    datos: Any, 
    nombre_archivo: str, 
    directorio: str = "",
    formato: str = "json",
    indent: int = 2,
    ensure_ascii: bool = False
) -> str:
    """
    Guarda datos en un archivo con manejo de directorios.
    
    Args:
        datos: Datos a guardar
        nombre_archivo: Nombre del archivo (sin extensión)
        directorio: Directorio de destino (opcional)
        formato: Formato de salida (json, txt)
        indent: Indentación para JSON
        ensure_ascii: Si es False, permite caracteres Unicode en JSON
        
    Returns:
        Ruta completa del archivo guardado
    """
    # Asegurar que el directorio exista
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio, exist_ok=True)
    
    # Añadir extensión si es necesario
    if not nombre_archivo.endswith(f".{formato}"):
        nombre_archivo = f"{nombre_archivo}.{formato}"
    
    # Construir ruta completa
    ruta_completa = os.path.join(directorio, nombre_archivo) if directorio else nombre_archivo
    
    # Guardar según el formato
    try:
        if formato.lower() == 'json':
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=indent, ensure_ascii=ensure_ascii)
        else:  # txt o cualquier otro formato
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                f.write(str(datos))
        
        return ruta_completa
    except Exception as e:
        # Intentar guardar en directorio actual si falla
        nombre_archivo = f"error_{int(time.time())}_{nombre_archivo}"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(f"Error al guardar archivo: {str(e)}\n\nDatos:\n{str(datos)[:1000]}...")
        return nombre_archivo

def cargar_archivo(
    ruta_archivo: str, 
    formato: Optional[str] = None
) -> Any:
    """
    Carga datos desde un archivo.
    
    Args:
        ruta_archivo: Ruta al archivo
        formato: Formato del archivo (json, txt). Si es None, se infiere de la extensión.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
    
    # Inferir formato si no se especifica
    if formato is None:
        _, ext = os.path.splitext(ruta_archivo)
        formato = ext.lower().lstrip('.')
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            if formato == 'json':
                return json.load(f)
            else:
                return f.read()
    except Exception as e:
        raise IOError(f"Error al cargar archivo {ruta_archivo}: {str(e)}")

def obtener_timestamp() -> str:
    """
    Devuelve un timestamp formateado para usar en nombres de archivo.
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def formatear_duracion(segundos: float) -> str:
    """
    Formatea una duración en segundos a un string legible.
    """
    minutos, segundos = divmod(int(segundos), 60)
    horas, minutos = divmod(minutos, 60)
    
    if horas > 0:
        return f"{horas}h {minutos:02d}m {segundos:02d}s"
    elif minutos > 0:
        return f"{minutos}m {segundos:02d}s"
    else:
        return f"{segundos}s"

def crear_directorio_si_no_existe(directorio: str) -> None:
    """
    Crea un directorio si no existe.
    """
    os.makedirs(directorio, exist_ok=True)

def limpiar_texto(texto: str) -> str:
    """
    Limpia un texto eliminando caracteres problemáticos.
    """
    if not texto or not isinstance(texto, str):
        return ""
    
    # Reemplazar caracteres problemáticos
    reemplazos = {
        '\n': ' ', '\r': ' ', '\t': ' ',  # Espacios en blanco
        '"': '"',  # Comillas tipográficas
        "'" : "'",
        '…': '...',  # Puntos suspensivos
    }
    
    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)
    
    # Eliminar múltiples espacios en blanco
    texto = ' '.join(texto.split())
    
    return texto.strip()
