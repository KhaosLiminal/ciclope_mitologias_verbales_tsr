# PIMP_MY_RIDE_GLM5 - Kit de Optimización para GLM-5

## 🎯 Propósito

Colección curada de system prompts, herramientas, skills y arquitecturas de agentes extraídas de los mejores modelos del mercado (Claude Code, GPT-5.2, Cursor, Windsurf) para potenciar GLM-5 en el proyecto Cíclope.

---

## 📁 Estructura

### `SYSTEM_PROMPTS/`
System prompts de producción listos para adaptar:

- **claude-code-system-prompt.txt** - Prompt base de Claude Code (conciso, directo, <4 líneas)
- **claude-code.md** - System prompt completo v2.1.50 (1491 líneas con todas las especificaciones)

**Patrones clave:**
- Concisión extrema ("One word answers are best")
- Prohibición de preámbulos/postámbulos
- Task management con TodoWrite
- Tool usage policy (paralelismo máximo)
- Código references: `file_path:line_number`

---

### `TOOLS/`
Definiciones de herramientas y su arquitectura:

- **claude-code-tools.json** - 43 herramientas con schemas JSON completos
- **Tool.ts** - Implementación TypeScript de la clase Tool (28.8KB)
- **tools.ts** - Orquestador de herramientas (16.9KB)
- **QueryEngine.ts** - Motor de queries optimizado (45.5KB)
- **commands.ts** - Sistema de comandos (24.6KB)

**Herramientas críticas identificadas:**
1. **Task** - Lanzar agentes especializados (subagent_type)
2. **Bash** - Ejecución con timeout, descripción, background mode
3. **Glob** - Búsqueda por patrones (más rápido que grep)
4. **Grep** - Búsqueda ripgrep optimizada
5. **Read/Edit/Write** - Operaciones de archivo atómicas
6. **AskUserQuestion** - Preguntas estructuradas al usuario

---

### `SKILLS/`
Skills empaquetados y utilidades:

- **batch.ts** - Procesamiento por lotes (7.0KB)
- **remember.ts** - Gestión de memoria persistente (4.1KB)
- **skillify.ts** - Conversión a skills (9.3KB)
- **verify.ts** - Verificación de resultados (0.9KB)
- **simplify.ts** - Simplificación de código (4.4KB)
- **loadSkillsDir.ts** - Cargador dinámico de skills (33.6KB)
- **commands.ts** - Sistema de comandos slash (24.6KB)
- **interactiveHelpers.tsx** - Helpers interactivos (56.1KB)

**Skills prioritarios para CAPA6:**
- `batch.ts` → Procesar 19 TSRs en una llamada
- `verify.ts` → Validar word count y estructura
- `remember.ts` → Mantener coherencia entre TSRs

---

### `THINKING_PATTERNS/`
Patrones de razonamiento de modelos avanzados:

- **gpt-5.2-thinking.md** - Thinking process de GPT-5.2 (85.9KB)
- **o3.md** - Arquitectura de razonamiento o3 (31.5KB)

**Patrones aplicables a Cíclope:**
1. **Chain-of-thought explícito** - Mostrar pasos de razonamiento
2. **Auto-crítica** - Cuestionar propias suposiciones
3. **Multi-perspectiva** - Analizar desde 3+ ángulos
4. **Contradicciones productivas** - Mantener tensiones sin resolver

---

### `AGENT_ARCHITECTURES/`
Arquitecturas de agentes de otros sistemas:

- **CURSOR_Agent_Prompt_2.0.txt** - Prompt de agente Cursor
- **CURSOR_Agent_Tools_v1.0.json** - Tools de Cursor
- **WINDSURF_Prompt_Wave_11.txt** - Prompt Wave de Windsurf
- **WINDSURF_Tools_Wave_11.txt** - Tools de Windsurf

---

## 🔧 Aplicación a CAPA6

### Estrategia de Inyección en Prompt

```python
# Estructura del prompt para CAPA6 (inspirado en claude-code.md)

prompt = f"""
# MISIÓN
Genera 19 guiones de taller coherentes para TSR102-120.

# DATOS DE ENTRADA (CAPAS ANTERIORES)
{genealogias_capa2}      # 19 genealogías
{problematizaciones_capa3}  # 19 problematizaciones
{metaanalisis_capa5}     # 19 meta-análisis

# REGLAS ESTRICTAS (de claude-code-system-prompt.txt)
1. Una sola llamada → 19 outputs
2. Sin reintentos si falla
3. Word count: 300-500 palabras exactas
4. Tono: institucional, exigente, sin emojis
5. No marketero, sin KPIs
6. Estructura fija: 3 módulos + cierre generativo

# FORMATO DE SALIDA
Cada guion debe tener:
- Título provocador
- Módulo 1: Docencia (25 min)
- Módulo 2: Mediación (30 min)
- Módulo 3: Gestión Cultural (30 min)
- Cierre: 3 preguntas abiertas (10 min)

# VALIDACIÓN (de verify.ts)
if palabras < 300 or palabras > 500:
    marcar_como("fuera_de_rango")
"""
```

---

## 📊 Métricas de Agresividad

| Capa | Llamadas API | TSRs por llamada | Eficiencia |
|------|--------------|------------------|------------|
| CAPA2 | 19 individuales | 1 | Baja |
| CAPA3 | 19 individuales | 1 | Baja |
| CAPA4 | 19 individuales | 1 | Baja |
| CAPA5 | 1 transversal | 20 | **Alta** ✅ |
| CAPA6 | 1 transversal | 19 | **Máxima** 🎯 |

**Lección CAPA5:** Método transversal validado → 1 llamada = coherencia garantizada

---

## 🚀 Próximos Pasos

1. **Adaptar system prompt** de Claude Code para GLM-5
2. **Inyectar datos** de CAPA2/CAPA3/CAPA5 en un solo prompt
3. **Ejecutar llamada única** con fallback sin reintentos
4. **Validar outputs** con verify.ts adaptado
5. **Registrar errores** en `/PAPELERA/` si falla

---

## 📚 Referencias Clave

### Claude Code Principles (extraídos de claude-code.md)
- "NEVER give time estimates"
- "Only use emojis if user explicitly requests it"
- "NEVER create files unless absolutely necessary"
- "ALWAYS prefer editing existing file to creating new one"
- "Avoid over-engineering. Keep solutions simple and focused"
- "Don't add error handling for scenarios that can't happen"

### Tool Usage Policy
- "Call multiple tools in parallel whenever possible"
- "Use specialized tools instead of bash commands"
- "For broader codebase exploration, use Task tool with subagent_type=Explore"

### Thinking Patterns (de gpt-5.2-thinking.md)
- Explicit chain-of-thought reasoning
- Self-critique before finalizing
- Multi-perspective analysis
- Maintain productive contradictions

---

*Generado: 2026-04-25*  
*Proyecto: Cíclope · Mitologías Verbales*  
*Objetivo: Potenciar GLM-5 con lo mejor de Claude/GPT-5/Cursor/Windsurf*
