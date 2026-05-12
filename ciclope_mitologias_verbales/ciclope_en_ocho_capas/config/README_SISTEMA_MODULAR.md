# 🎯 SISTEMA MODULAR DE CAPAS - CÍCLOPE TSR

**Arquitectura editorial para producción de conocimiento serial, modular y conceptualmente coherente**

---

## 📖 VISIÓN GENERAL

Este sistema permite generar **19 documentos TSR (TSR102-120)** mediante **7 capas apilables** que se generan de manera transversal, asegurando coherencia conceptual y terminológica entre todas las partes.

### Ventajas sobre generación monolítica:
- ✅ **Eficiencia**: 7 llamadas vs. 133 llamadas (reducción 95%)
- ✅ **Coherencia**: Todas las genealogías con misma densidad conceptual
- ✅ **Modularidad**: Regenerar solo capas específicas sin tocar las demás
- ✅ **Escalabilidad**: Agregar TSR121 solo requiere extender cada capa
- ✅ **Versionado**: Control granular por capa
- ✅ **Validación**: Coherencia terminológica automática entre capas

---

## 🏗️ ARQUITECTURA DE CAPAS

```
CAPA 0: Semilla Conceptual (TSR101-120QUOTES.md)
│   └─ 20 fragmentos fundacionales en 7 clústeres
│
├─ CAPA 1: Bibliografía Verificada
│   └─ 235 fuentes (19 TSR × 12 fuentes/TSR)
│
├─ CAPA 2: Genealogía Conceptual
│   └─ 19 genealogías (650-800 palabras c/u)
│   └─ Rastrea origen histórico de conceptos
│
├─ CAPA 3: Problematización Contemporánea  ⬅ PRÓXIMA
│   └─ 19 problematizaciones (1000-1500 palabras c/u)
│   └─ Conecta conceptos con IA, NFT, algoritmos
│
├─ CAPA 4: Resonancias Reflejos Híbridos
│   └─ 19 resonancias (400-600 palabras c/u)
│   └─ Conecta con universo narrativo/visual RH
│
├─ CAPA 5: Metanalisis (TSR sobre TSR)
│   └─ 19 metanalisis (600-800 palabras c/u)
│   └─ Cada TSR se aplica a sí mismo
│
├─ CAPA 6: Guiones de Taller
│   └─ 19 guiones (300-500 palabras c/u)
│   └─ Actividades pedagógicas operativas
│
└─ CAPA 7: Casos de Estudio
    └─ 19 casos (400-600 palabras c/u)
    └─ Ejemplos de aplicación del marco TSR

COMPILACIÓN FINAL
└─ 19 TSR completos (4000-5500 palabras c/u)
```

---

## 📂 ESTRUCTURA DE ARCHIVOS

```
cíclope_en_siete_capas/
├── config/
│   ├── GLOSARIO_CICLOPE.json          # Definiciones canónicas
│   ├── METADATOS_PROYECTO.json        # Info centralizada
│   └── PROMPTS_POR_CAPA/
│       ├── CAPA3_prompt.txt
│       ├── CAPA4_prompt.txt
│       ├── CAPA5_prompt.txt
│       ├── CAPA6_prompt.txt
│       └── CAPA7_prompt.txt
│
├── capas/
│   ├── CAPA0_semilla/
│   │   └── TSR101-120QUOTES.md
│   ├── CAPA1_bibliografia/
│   │   └── TSR_CAPA1_FINAL.json
│   ├── CAPA2_genealogia/
│   │   └── TSR_CAPA2_FINAL.json
│   ├── CAPA3_problematizacion/
│   │   └── TSR_CAPA3_FINAL.json
│   ├── CAPA4_resonancias/
│   ├── CAPA5_metanalisis/
│   ├── CAPA6_talleres/
│   └── CAPA7_casos/
│
├── scripts/
│   ├── validar_coherencia_capas.py    # Validador cruzado
│   ├── generar_capa3.py
│   ├── generar_capa4.py
│   ├── generar_capa5.py
│   ├── generar_capa6.py
│   ├── generar_capa7.py
│   └── compilar_tsr_final.py          # Ensamblador
│
└── outputs/
    └── TSR_COMPILADOS/
        ├── TSR102_completo.md
        ├── TSR103_completo.md
        └── ...
```

---

## 🔧 COMPONENTES CRÍTICOS

### 1. GLOSARIO_CICLOPE.json

**Función:** Define términos clave de manera canónica para asegurar uso consistente entre capas.

**Términos rastreados:**
- `fragmento` (Schlegel vs. Blanchot - tensión dialéctica)
- `aura` (Benjamin + críticos posteriores)
- `autor` (Barthes, Foucault, Eco)
- `archivo` (Foucault, Derrida)
- `episteme` (Foucault)
- `lectura de segundo orden` (TRCO)
- `glitch` (error productivo)
- `Reflejos Híbridos` (universo narrativo)

**Reglas de validación:**
1. Si un término tiene múltiples definiciones, DECLARAR cuál se usa
2. Divergencias deben marcarse explícitamente como "tensión dialéctica"
3. Ninguna capa puede contradecir capas previas sin declarar la tensión

---

### 2. METADATOS_PROYECTO.json

**Función:** Centraliza información del proyecto completo.

**Contiene:**
- Información del proyecto (autor, versión, fechas)
- Arquitectura de capas (dependencias, estados)
- Estructura de TSR (19 TSR, 6 clústeres)
- Reglas de coherencia
- Formatos de exportación

---

### 3. validar_coherencia_capas.py

**Función:** Valida que términos clave se usen consistentemente entre capas.

**Uso:**
```bash
# Validar una capa específica
python validar_coherencia_capas.py --capa CAPA3 --all

# Validar coherencia entre capas consecutivas
python validar_coherencia_capas.py --validar-todo

# Validar un TSR específico
python validar_coherencia_capas.py --capa CAPA3 --tsr 102

# Guardar reporte
python validar_coherencia_capas.py --validar-todo --output reporte.txt
```

**Detecta:**
- ❌ Términos con múltiples definiciones usados sin especificar cuál
- ❌ Contradicciones entre capas sin declarar tensión dialéctica
- ❌ Usos divergentes del glosario sin justificación

---

### 4. generar_capa3.py (y scripts similares para CAPA4-7)

**Función:** Genera una capa completa usando las capas anteriores como input.

**Uso:**
```bash
# Generar un TSR específico
python generar_capa3.py --modelo claude --tsr 102

# Generar todos los TSR
python generar_capa3.py --modelo sonar --all

# Validar CAPA 2 antes de generar CAPA 3
python generar_capa3.py --modelo claude --all --validar-antes
```

**Input:**
- CAPA0: Fragmento fundacional
- CAPA1: Fuentes bibliográficas
- CAPA2: Genealogía conceptual
- GLOSARIO_CICLOPE.json

**Output:**
- JSON con 19 problematizaciones
- Metadata de validación (extensión, términos usados)

---

## 🚀 WORKFLOW RECOMENDADO

### PASO 1: Validar CAPA 1 (Bibliografía)
```bash
# Verificar que todas las URLs funcionen
python validar_capa1.py --verificar-urls

# Completar URLs faltantes manualmente
```

**Criterios de validación:**
- ✅ 19 TSR completos (102-120)
- ✅ 10-13 fuentes por TSR
- ✅ Diversidad: primarias, secundarias, multimedia
- ✅ URLs accesibles (no rotas)

---

### PASO 2: Validar CAPA 2 (Genealogía)
```bash
# Validar coherencia interna de CAPA 2
python validar_coherencia_capas.py --capa CAPA2 --all
```

**Criterios de validación:**
- ✅ 650-800 palabras por genealogía
- ✅ Términos del glosario usados correctamente
- ✅ Citas de CAPA 1 presentes
- ✅ Tono crítico-poético (no académico neutro)

---

### PASO 3: Generar CAPA 3 (Problematización)
```bash
# Generar con validación previa
python generar_capa3.py --modelo claude --all --validar-antes
```

**Criterios de éxito:**
- ✅ 1000-1500 palabras por problematización
- ✅ Conecta con IA, NFT, algoritmos, plataformas
- ✅ Retoma conceptos de CAPA 2
- ✅ Abre preguntas, no cierra con respuestas
- ✅ Validación automática de coherencia con CAPA 2

---

### PASO 4: Repetir para CAPAS 4-7
```bash
python generar_capa4.py --modelo claude --all --validar-antes
python generar_capa5.py --modelo claude --all --validar-antes
python generar_capa6.py --modelo claude --all --validar-antes
python generar_capa7.py --modelo claude --all --validar-antes
```

---

### PASO 5: Compilar TSR finales
```bash
# Compilar un TSR específico
python compilar_tsr_final.py --tsr 102 --formato pdf

# Compilar todos los TSR
python compilar_tsr_final.py --all --formato markdown
```

**Output:**
- 19 archivos markdown (uno por TSR)
- Cada TSR contiene las 7 capas ensambladas
- Extensión total: 4000-5500 palabras por TSR

---

## 📊 VENTAJAS DEL SISTEMA

### 1. CONTROL GRANULAR
- Puedes regenerar CAPA 3 sin tocar CAPA 2
- Puedes probar diferentes modelos (Claude vs. Sonar) por capa
- Puedes versionar capas independientemente

### 2. COHERENCIA AUTOMÁTICA
- El script de validación detecta contradicciones antes de que lleguen a la versión final
- El glosario centralizado evita definiciones divergentes
- Metadata rastrea dependencias entre capas

### 3. ESCALABILIDAD
- Agregar TSR121 solo requiere:
  1. Agregar fragmento a CAPA0
  2. Agregar 12 fuentes a CAPA1
  3. Ejecutar scripts de CAPA2-7 con `--tsr 121`

### 4. REUTILIZACIÓN
- CAPA 1 (bibliografía) puede usarse para otros proyectos
- CAPA 2 (genealogías) puede exportarse como artículos independientes
- CAPA 6 (talleres) puede implementarse sin esperar CAPA 7

---

## 🎯 PRÓXIMOS PASOS

**INMEDIATO:**
1. ✅ Completar URLs faltantes en CAPA 1
2. ✅ Validar coherencia de CAPA 2
3. ⏳ Generar CAPA 3 completa (19 problematizaciones)

**CORTO PLAZO:**
4. Crear scripts para CAPA 4-7
5. Implementar compilador final
6. Diseñar templates de exportación (PDF, Markdown, HTML)

**MEDIANO PLAZO:**
7. Documentar el sistema como paper académico
8. Crear interfaz web para visualizar dependencias entre capas
9. Publicar sistema como herramienta open-source para otros proyectos editoriales

---

## 📝 NOTAS TÉCNICAS

### Modelos soportados:
- **Claude Sonnet 4.5**: Tono crítico-poético, consciencia liminal
- **Perplexity Sonar**: Investigación bibliográfica, síntesis académica

### Formatos de exportación:
- **JSON**: Estructura interna de cada capa
- **Markdown**: TSR compilados listos para publicar
- **PDF**: Diseño final con tipografía y diagramación
- **HTML**: Versión web interactiva

### Requisitos:
- Python 3.10+
- Acceso a API de Claude/Perplexity
- ~500MB de espacio (para las 7 capas de 19 TSR)

---

## 🤝 CONTRIBUCIONES

Este sistema es parte del proyecto **Reflejos Híbridos** de Sarayu Aguilar.

Para replicar este sistema en tu propio proyecto:
1. Adapta `GLOSARIO_CICLOPE.json` con tus términos clave
2. Define tu arquitectura de capas en `METADATOS_PROYECTO.json`
3. Modifica los prompts en `generar_capaN.py` según tu contenido
4. Ejecuta el flujo completo y valida coherencia

---

**Versión:** 1.0  
**Última actualización:** 2026-02-14  
**Autor:** Sarayu Aguilar  
**Licencia:** MIT (ver LICENSE)
