# Arquitectura del Sistema Cíclope

---

## 🏗️ Vista General del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA CÍCLOPE                          │
│                Generación de TSR (19 documentos)           │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA0: Semillas │
                    │   Conceptuales    │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA1:          │
                    │   Bibliografías   │ ← Perplexity API
                    │   (235 fuentes)   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA2:          │
                    │   Genealogías     │ ← Glosario inyectado
                    │   (650-800 pal)   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA3:          │
                    │   Problematiza-   │ ← CAPA2 como input
                    │   ciones (1000-   │
                    │   1500 pal)       │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA4:          │
                    │   Resonancias     │ ← CAPA2 + CAPA3
                    │   (400-600 pal)   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA5:          │
                    │   Meta-análisis   │
                    │   (pendiente)     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA6:          │
                    │      Talleres     │
                    │   (pendiente)     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CAPA7:          │
                    │ Casos de Estudio  │
                    │   (pendiente)     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   TSR COMPLETO    │
                    │   (4000-5500 pal) │
                    └───────────────────┘
```

---

## 📁 Estructura de Directorios

```
cíclope_mitologías_verbales/
│
├── 📄 README.md                    # Portal principal del proyecto
├── 📁 docs/                        # Documentación conceptual
│   ├── 📄 filosofia.md            # Ensayo sobre Cíclope
│   ├── 📄 onboarding.md           # Guía para nuevos usuarios
│   ├── 📄 arquitectura.md         # Este archivo
│   └── 📄 glosario.md             # Términos clave
│
├── 📁 cíclope_en_siete_capas/      # Motor técnico
│   ├── 📄 README.md                # Guía técnica
│   ├── 📄 requirements.txt         # Dependencias Python
│   │
│   ├── 📁 scripts/                 # Scripts ejecutables
│   │   ├── 🐍 TSR_CAPA1_Completa.py
│   │   ├── 🐍 consolidar_capa2_final.py
│   │   ├── 🐍 generar_capa3.py
│   │   ├── 🐍 generar_capa4.py
│   │   ├── 🐍 validar_coherencia_capas.py
│   │   └── 🐍 utils.py
│   │
│   ├── 📁 capas/                   # Resultados por capa
│   │   ├── 📄 CAPA1_fuentes.json
│   │   ├── 📄 TSR_CAPA2_FINAL_CONSOLIDADO.json
│   │   ├── 📄 TSR_CAPA3_FINAL.json
│   │   └── 📄 TSR_CAPA4_FINAL.json
│   │
│   ├── 📁 config/                  # Configuración
│   │   ├── 📄 METADATOS_PROYECTO.json
│   │   ├── 📄 GLOSARIO_CICLOPE.json
│   │   └── 📄 CAPA4_prompt.txt
│   │
│   └── 📁 src/                     # Código fuente modular
│       ├── 🐍 api_client.py
│       ├── 🐍 models.py
│       ├── 🐍 validators.py
│       └── 🐍 config.py
│
├── 📁 outputs/                     # TSR finales compilados
│   ├── 📄 TSR102_completo.md
│   ├── 📄 TSR103_completo.md
│   └── 📄 ...
│
└── 📄 LICENSE                      # Licencia MIT
```

---

## 🔄 Flujo de Datos

### Input → Procesamiento → Output

```
INPUTS INICIALES:
├── 🌐 Perplexity API Key
├── 📝 20 semillas conceptuales (CAPA0)
└── 📚 Glosario de términos canónicos

           │
           ▼

PROCESAMIENTO POR CAPA:
┌─────────────────────────────────────────────────┐
│ CAPA1: API Calls → 235 fuentes verificadas     │
│ CAPA2: Genealogías con metadata enriquecida     │
│ CAPA3: Problematizaciones contemporáneas       │
│ CAPA4: Resonancias interdisciplinarias         │
└─────────────────────────────────────────────────┘

           │
           ▼

OUTPUTS FINALES:
├── 📄 19 TSR completos (4000-5500 palabras)
├── 🎨 19 clúster visuales
├── 📊 Reportes de validación
└── 📋 Estadísticas de generación
```

---

## 🔌 Integraciones Externas

### Perplexity Sonar API
```
┌─────────────────┐    API Key    ┌──────────────────┐
│   Scripts Cíclope│ ─────────────→ │ Perplexity Sonar │
│                 │                │                  │
│ • Búsqueda      │ ← Respuestas → │ • Citas          │
│ • Verificación  │                │ • Contexto       │
│ • Generación    │                │ • Fuentes        │
└─────────────────┘                └──────────────────┘
```

### Sistema de Validación
```
┌─────────────────┐    JSON       ┌──────────────────┐
│   Glosario      │ ─────────────→ │ Validador       │
│   Canónico      │                │                  │
│                 │ ← Reporte →   │ • Coherencia     │
│ • Términos      │                │ • Consistencia   │
│ • Definiciones  │                │ • Métricas       │
└─────────────────┘                └──────────────────┘
```

---

## ⚙️ Configuración y Parámetros

### Variables de Entorno
```bash
PERPLEXITY_API_KEY=tu_api_key_aquí
```

### Parámetros en config.py
```python
MAX_REINTENTOS=3           # Reintentos API
DELAY_INICIAL=1.0         # Segundos espera inicial
FACTOR_BACKOFF=2.0        # Multiplicador backoff
MAX_DELAY=60.0            # Máximo espera
```

### Estructura de Metadatos
```json
{
  "proyecto": "Cíclope: Mitologías Verbales",
  "capas": 7,
  "tsr_count": 19,
  "estado": "en_progreso",
  "ultima_actualizacion": "2026-03-03"
}
```

---

## 🎯 Puntos de Control y Validación

### Checkpoints por Capa
```
✅ CAPA1: 235 fuentes verificadas
✅ CAPA2: 19 genealogías con metadata
✅ CAPA3: 19 problematizaciones
✅ CAPA4: 19 resonancias
⏳ CAPA5: Meta-análisis (pendiente)
⏳ CAPA6: Talleres (pendiente)
⏳ CAPA7: Casos de estudio (pendiente)
```

### Validaciones Automáticas
- **Coherencia terminológica**: Glosario vs contenido
- **Extensión**: Word count por capa
- **Formato**: Estructura JSON válida
- **Citas**: URLs verificables

---

## 🚨 Manejo de Errores

### Retry Logic
```
Intento 1: Llamada API normal
└── Error → Espera 1s → Intento 2
    └── Error → Espera 2s → Intento 3
        └── Error → Espera 4s → Abortar
```

### Logs y Debug
```
logs/
├── api_calls.log          # Todas las llamadas API
├── validation_report.json # Resultados validación
└── error_tracebacks.log   # Errores detallados
```

---

## 📊 Métricas y Monitoreo

### KPIs del Sistema
- **Tasa éxito API**: >90%
- **Tiempo generación TSR**: ~15 min
- **Coherencia terminológica**: >80%
- **Citas verificadas**: 100%

### Dashboard de Estado
```bash
python scripts/generar_reporte_estado.py
```

Output:
```
📊 ESTADO DEL PROYECTO CÍCLOPE
=============================
Capas completas: 4/7
TSRs generados: 19/19
Tasa éxito API: 94.2%
Última actualización: 2026-03-03
```

---

## 🔮 Arquitectura Futura

### Próximas Capas
```
CAPA5: Casos de Estudio
├── Análisis de ejemplos concretos
├── Aplicación práctica de conceptos
└── Conexión con actualidad

CAPA6: Meta-análisis
├── Reflexión sobre el propio TSR
├── Auto-cuestionamiento
└── Cierre apofético
```

### Mejoras Técnicas
- **Paralelización**: Múltiples TSRs simultáneos
- **Caching**: Reducir llamadas API
- **UI/UX**: Interfaz web para monitoreo
- **Integración**: Con plataformas de publicación

---

## 🔄 Ciclo de Vida del TSR

```
1. 🌱 Semilla Conceptual (CAPA0)
2. 📚 Investigación Bibliográfica (CAPA1)
3. 🧬 Genealogía Conceptual (CAPA2)
4. ⚡ Problematización Contemporánea (CAPA3)
5. 🔗 Resonancias Interdisciplinarias (CAPA4)
6. 🎯 Caso de Estudio Aplicado (CAPA5)
7. 🪞 Meta-análisis y Reflexión (CAPA6)
8. 📦 Compilación Final y Diseño
9. 🚀 Publicación y Distribución
```

---

**Última actualización**: Marzo 2026  
**Arquitecto**: Sistema Reflejos Híbridos  
**Versión**: v2.0 (con CodeMaps Windsurf integrados)
