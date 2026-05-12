"""
Configuración centralizada para el proyecto Cíclope.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la API
API_KEY = os.getenv("PERPLEXITY_API_KEY", "tu_api_key_aquí")
MODEL = "sonar-pro"
MAX_TOKENS = 5000
TEMPERATURE = 0.3
MAX_RETRIES = 3
REQUEST_TIMEOUT = 60  # segundos

# Rutas de archivos
DEBUG_DIR = "debug"
RESULTS_DIR = "resultados"

# Crear directorios si no existen
os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Configuración de reintentos
RETRY_DELAYS = [5, 10, 15]  # Tiempos de espera entre reintentos (segundos)

# Validación de respuestas
MIN_SOURCES = 10
MAX_SOURCES = 15

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
