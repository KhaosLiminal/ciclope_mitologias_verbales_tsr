# RESUMEN EJECUTIVO - PIMP_MY_RIDE_GLM5

## 📊 Estadísticas de Recursos Extraídos

| Categoría | Archivos | Tamaño Total | Origen |
|-----------|----------|--------------|--------|
| SYSTEM_PROMPTS | 2 | 80KB | Claude Code v2.1.50 |
| TOOLS | 4 | 96KB | Claude source map |
| SKILLS | 8 | 168KB | Claude bundled skills |
| THINKING_PATTERNS | 2 | 124KB | GPT-5.2 + o3 |
| AGENT_ARCHITECTURES | 4 | 116KB | Cursor + Windsurf |
| **TOTAL** | **20** | **684KB** | **5 sistemas** |

---

## 🎯 Hallazgos Clave para CAPA6

### 1. **Método Transversal (Validado en CAPA5)**
- **Fuente:** Claude Code `batch.ts` + experiencia CAPA5
- **Patrón:** 1 llamada API → procesar todos los TSRs
- **Ventaja:** Coherencia conceptual garantizada entre outputs
- **Aplicación:** CAPA6 usa este método (no 19 llamadas individuales)

### 2. **System Prompt Óptimo (Claude Code)**
Extraído de `claude-code-system-prompt.txt`:

```
IMPORTANT: You must minimize output tokens as much as possible 
while maintaining helpfulness, quality, and accuracy. Only address 
the specific query or task at hand, avoiding tangential information 
unless absolutely critical for completing the request. If you can 
answer in 1-3 sentences or a short paragraph, please do.

IMPORTANT: You should NOT answer with unnecessary preamble or 
postamble (such as explaining your code or summarizing your action), 
unless the user asks you to.
```

**Lección para GLM-5:**
- Prohibir introducciones/conclusiones
- One word answers are best
- No explicar el código después de modificarlo
- Detenerse inmediatamente después de la acción

### 3. **Tool Usage Policy (Paralelismo Máximo)**
De `claude-code.md` línea 133:

```
You have the capability to call multiple tools in a single response. 
When multiple independent pieces of information are requested, batch 
your tool calls together for optimal performance.
```

**Aplicación a CAPA6:**
- Si necesitamos validar múltiples TSRs, hacerlo en paralelo
- No esperar confirmación entre validaciones
- Batch processing desde el diseño del prompt

### 4. **Thinking Patterns (GPT-5.2)**
De `gpt-5.2-thinking.md` (77KB):

**Patrones aplicables:**
1. **Chain-of-thought explícito:** Mostrar razonamiento paso a paso
2. **Self-critique:** Cuestionar suposiciones antes de finalizar
3. **Multi-perspective analysis:** Analizar desde 3+ ángulos
4. **Productive contradictions:** Mantener tensiones sin resolver

**Ejemplo de aplicación a CAPA6:**
```
Antes de generar guion final:
1. Analizar genealogía (CAPA2) → identificar concepto nuclear
2. Cruzar con problematización (CAPA3) → detectar tensión contemporánea
3. Consultar meta-análisis (CAPA5) → extraer auto-crítica
4. Sintetizar en guion operativo → mantener tensión dialéctica
```

### 5. **Agent Architecture (Cursor/Windsurf)**
De `CURSOR_Agent_Prompt_2.0.txt`:

**Estructura de agente especializada:**
```
ROLE: Diseñador pedagógico especializado en teoría crítica
CONTEXT: 19 TSRs con genealogías + problematizaciones + meta-análisis
TASK: Generar guiones de taller operativos
CONSTRAINTS: 
  - 300-500 palabras por guion
  - 3 módulos obligatorios (Docencia/Mediación/Gestión)
  - Evaluación de segundo orden (proceso, no resultado)
OUTPUT: JSON estructurado + archivos .md individuales
```

---

## 🔧 Adaptaciones Críticas para GLM-5

### A. **Prompt Engineering (inspirado en Claude Code)**

```python
prompt_capa6 = f"""
# MISIÓN CRÍTICA
Genera 19 guiones de taller coherentes para TSR102-120 en UNA SOLA LLAMADA.

# DATOS DE ENTRADA (inyectados)
{capa2_genealogias}      # 19 genealogías conceptuales
{capa3_problematizaciones}  # 19 problematizaciones contemporáneas  
{capa5_metaanalisis}     # 19 meta-análisis auto-aplicados

# REGLAS ABSOLUTAS (de claude-code-system-prompt.txt)
1. SIN preámbulos ("Aquí están los guiones...")
2. SIN postámbulos ("Espero que esto sea útil...")
3. SIN explicaciones después del código
4. Word count estricto: 300-500 palabras
5. Tono: institucional, exigente, sin emojis
6. Estructura fija: Título + 3 módulos + cierre generativo

# FORMATO EXACTO POR TSR
# TSR{{tsr_id}}: GUIÓN DE TALLER

## Título del taller
[Título provocador]

## Módulo 1: Docencia (25 min)
**Problema:** [1 frase]
**Actividad:** [Pasos numerados concretos]
**Evaluación 2do orden:** [Criterio de proceso]

## Módulo 2: Mediación (30 min)
**Problema:** [1 frase]
**Actividad:** [Pasos numerados]
**Conexión editorial:** [1-2 líneas]

## Módulo 3: Gestión Cultural (30 min)
**Problema:** [1 frase]
**Actividad:** [Pasos numerados]
**Criterios TRCO:** [1-2 preguntas]

## Cierre generativo (10 min)
1. [Pregunta abierta]
2. [Pregunta abierta]
3. [Pregunta abierta]

---

# VALIDACIÓN (de verify.ts)
Para cada guion generado:
- if palabras < 300: marcar("INSUFICIENTE")
- if palabras > 500: marcar("EXCESIVO")
- if estructura != 3_modulos: marcar("INCOMPLETO")
- if tono == "marketero": marcar("TONO_INCORRECTO")

# POST-MORTEM (de gpt-5.2-thinking.md)
Después de generar, auto-evaluar:
1. ¿Los guiones mantienen coherencia conceptual entre sí?
2. ¿Cada guion opera independientemente sin consultar el TSR?
3. ¿Las actividades son ejecutables con materiales específicos?
4. ¿Se mantiene la tensión dialéctica sin resolverla?

GENERAR AHORA.
"""
```

### B. **Fallback Strategy (sin reintentos)**

```python
def llamar_api_con_fallback(prompt, modelo_primario):
    """
    Estrategia de CAPA6: una llamada, fallback único, sin reintentos
    """
    resultado = api_call(modelo_primario, prompt)
    
    if not resultado:
        # Fallback único (de claude-code.md fallback policy)
        modelo_secundario = obtener_modelo_alternativo(modelo_primario)
        print(f"[FALLBACK] {modelo_primario} falló, intentando {modelo_secundario}")
        resultado = api_call(modelo_secundario, prompt)
        
        if not resultado:
            # Registro en PAPELERA (no reintentar)
            registrar_error_en_papelera({
                "capa": "CAPA6",
                "modelo_primario": modelo_primario,
                "modelo_secundario": modelo_secundario,
                "error": "Ambos modelos fallaron",
                "timestamp": datetime.now().isoformat()
            })
            return None
    
    return resultado
```

### C. **Batch Processing (de batch.ts)**

```typescript
// Adaptación de batch.ts para CAPA6
interface BatchResult {
  tsr_id: number;
  guion: string;
  validation: {
    palabras: number;
    estructura: "completa" | "incompleta";
    tono: "correcto" | "incorrecto";
  };
}

async function procesarCapa6Batch(
  datosCapas: CapaData[],
  modelo: string
): Promise<BatchResult[]> {
  // UNA SOLA LLAMADA API
  const prompt = construirPromptTransversal(datosCapas);
  const respuesta = await apiCall(modelo, prompt);
  
  // Parsear 19 guiones de la respuesta única
  const guiones = parsearGuiones(respuesta);
  
  // Validar cada guion
  return guiones.map(guion => ({
    tsr_id: guion.tsr_id,
    guion: guion.contenido,
    validation: validarGuion(guion.contenido)
  }));
}
```

---

## 📈 Métricas de Éxito para CAPA6

| Métrica | Objetivo | Fuente |
|---------|----------|--------|
| **Llamadas API** | 1 (transversal) | Lección CAPA5 |
| **TSRs procesados** | 19/19 | Requerimiento |
| **Word count válido** | 300-500 palabras | CAPA6_prompt.txt |
| **Coherencia inter-TSR** | Alta (misma llamada) | Claude batch.ts |
| **Fallbacks utilizados** | ≤1 | claude-code.md |
| **Errores registrados** | En /PAPELERA/ | Política proyecto |

---

## 🚀 Próximos Pasos Inmediatos

1. ✅ **Recursos extraídos** de Claude/GPT-5/Cursor/Windsurf
2. ⏳ **Adaptar system prompt** específico para GLM-5
3. ⏳ **Inyectar datos** de CAPA2/CAPA3/CAPA5 en prompt transversal
4. ⏳ **Ejecutar llamada única** con modelo seleccionado
5. ⏳ **Validar outputs** con patrón de verify.ts
6. ⏳ **Registrar resultado** en bitácora si hay errores

---

## 📚 Referencias Directas

- **Claude Code System Prompt:** `SYSTEM_PROMPTS/claude-code.md` (línea 1-1491)
- **GPT-5.2 Thinking:** `THINKING_PATTERNS/gpt-5.2-thinking.md` (77KB)
- **Batch Processing:** `SKILLS/batch.ts` (7.0KB)
- **Tool Definitions:** `TOOLS/claude-code-tools.json` (43 herramientas)
- **Agent Architecture:** `AGENT_ARCHITECTURES/CURSOR_Agent_Prompt_2.0.txt`

---

*Documento generado: 2026-04-25*  
*Propósito: Optimizar GLM-5 para CAPA6 del proyecto Cíclope*  
*Estado: Listo para implementación*
