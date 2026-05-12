# 🚀 Sistema Técnico Cíclope - Generación por Capas

**Este documento complementa el [README principal](../README.md) con detalles técnicos de implementación.**

---

## 📋 Visión Rápida

Este directorio contiene el **motor técnico** que genera los 19 TSR del proyecto Cíclope mediante un sistema de 7 capas secuenciales.

### Para empezar:
1. **[Onboarding completo](../docs/onboarding.md)** - Guía paso a paso
2. **[Arquitectura del sistema](../docs/arquitectura.md)** - Diagramas y flujo
3. **[Glosario de términos](../docs/glosario.md)** - Conceptos clave

---

## �️ Requisitos Técnicos

- Python 3.8+
- API Key de Perplexity
- Dependencias listadas en [requirements.txt](cci:7://file:///c:/Users/alien/Downloads/c%C3%ADclope/c%C3%ADclope%20en%20siete%20capas/requirements.txt:0:0-0:0)

## 🛠️ Instalación

1. Clona el repositorio:

   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd [NOMBRE_DEL_REPOSITORIO]
   ```

2. Crea un entorno virtual (recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura tu API key:

   ```bash
   # En Windows
   setx PERPLEXITY_API_KEY "tu_api_key_aquí"
   
   # En Linux/Mac
   export PERPLEXITY_API_KEY="tu_api_key_aquí"
   ```

## 🚀 Uso

1. Prepara tu archivo de metadatos en `datos/tsr_metadatos.json`
2. Ejecuta el script principal:

   ```bash
   python scripts/ejecutar_capa1.py
   ```

3. Los resultados se guardarán en la carpeta `resultados/`

## 📁 Estructura del Proyecto

```bash
.
├── datos/                    # Datos de entrada
│   └── tsr_metadatos.json    # Metadatos de los TSRs
├── resultados/               # Resultados de la ejecución
│   ├── debug/                # Archivos de depuración
│   └── resultados_*.json     # Resultados parciales y finales
├── scripts/                  # Scripts ejecutables
│   ├── ejecutar_capa1.py     # Script principal
│   └── TSR_CAPA1_Reintentos.py # Script de reintentos
├── src/                      # Código fuente
│   ├── __init__.py
│   ├── api_client.py         # Cliente de la API
│   ├── config.py             # Configuración
│   ├── models.py             # Modelos de datos
│   ├── validators.py         # Validadores
│   └── utils.py              # Utilidades
└── tests/                    # Pruebas unitarias
    └── test_validators.py
```

## ⚙️ Configuración

Puedes modificar los parámetros en `src/config.py`:

- MAX_REINTENTOS: Número máximo de reintentos por TSR
- DELAY_INICIAL: Tiempo de espera inicial entre reintentos (segundos)
- FACTOR_BACKOFF: Factor de multiplicación para el backoff exponencial
- MAX_DELAY: Tiempo máximo de espera entre reintentos (segundos)

## 📊 Estadísticas

El sistema genera automáticamente estadísticas de ejecución, incluyendo:

- Número de TSRs procesados
- Tasa de éxito
- Tiempo de ejecución
- Número de fuentes generadas

## 🐛 Depuración

Los archivos de depuración se guardan en `resultados/debug/` e incluyen:

- Respuestas crudas de la API
- Errores de validación
- Trazas de ejecución

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

Desarrollado por Nigel_Moonwriter | <reflejoshibridos@gmail.com>
