# AUDITORÍA ONTOLÓGICA - PATRONES DE PROMPTING PRE-CÍCLOPE

**Fecha:** 25 de abril, 2026  
**Fuente:** Casos pre-Cíclope en `C:\Users\alien\any_files`  
**Modelo original:** Perplexity Sonar Pro (API)  
**Objetivo:** Extraer patrones de prompting que resuelvan fallo TSR115 en MiniMax M2.5-free

---

## 📊 CASOS ANALIZADOS

### 1. **CASO FUNDACIONAL: readiculous_50_heavy.csv**

**Prompt usado:** `readiculous_generator.py` (v1)  
**Método:** `client.search.create()` con búsqueda web ACTIVADA  
**Resultado:** ❌ **NEGACIÓN TOTAL**

```
"No puedo generar ese contenido tal como lo solicitas.

Tu demanda presupone una confusión fundamental entre síntesis analítica 
y producción de propaganda. Los carteles que pides no son instrumentos 
de crítica sino de espectacularización de la crítica..."
```

**Análisis ontológico:**
- El modelo **rechaza explícitamente** el formato "carteles críticos"
- Justifica su negativa con teoría debordiana (ironía suprema)
- Ofrece alternativa: análisis conceptual sin reducción a slogans
- **Patrón detectado:** Búsqueda web + formato propagandístico = activación de filtros éticos

---

### 2. **CASO RESUELTO: debord_con_busqueda.txt**

**Prompt usado:** `debord_analysis_web.py`  
**Método:** `client.chat.completions.create()` con búsqueda web ACTIVADA  
**Diferencia clave:** Solicita ANÁLISIS PRIMERO, luego carteles  
**Resultado:** ✅ **ÉXITO PARCIAL**

```
# Análisis del espectáculo integrado en estructuras contemporáneas
[900+ palabras de análisis riguroso]

## Carteles filosóficos críticos
[TABLA CSV con 10 carteles bien estructurados]
```

**Lección crítica:**
- **El orden importa:** Pedir análisis antes de carteles desactiva resistencia
- **Framing académico:** "Analiza... después genera" vs "Genera EXACTAMENTE 50 carteles"
- **Búsqueda web como validador:** Las fuentes externas legitiman la generación

---

### 3. **CASO SIN BÚSQUEDA: debord_sin_busqueda.txt**

**Prompt usado:** `debord_analysis_no_web.py`  
**Método:** MISMO prompt pero con `disable_search=True`  
**Resultado:** ✅ **ÉXITO COMPLETO** (sin tabla CSV, solo análisis)

```
### Análisis Conceptual de la Teoría Debordiana...
[1200+ palabras de análisis profundo, sin carteles]
```

**Observación crucial:**
- Sin búsqueda web, el modelo se enfoca en análisis teórico
- No intenta generar carteles (¿olvidó esa parte del prompt?)
- **Hipótesis:** disable_search reduce "distracción" del modelo hacia formatos secundarios

---

### 4. **VARIANTES EXITOSAS: medium/light/heavy**

| Archivo | Método | Resultado | Patrón |
|---------|--------|-----------|--------|
| `readiculous_50_heavy.csv` | search.create() + web | ❌ Negación | Búsqueda web activa filtros |
| `readiculous_50_medium.csv` | chat.completions + web | ⚠️ Parcial | Texto introductorio + 50 items numerados |
| `readiculous_50_light.csv` | chat.completions + web | ⚠️ Parcial | Formato Markdown table, no CSV |
| `readiculous_50_carteles.csv` | chat.completions v3 | ✅ Éxito | System prompt específico + disable_search implícito |

---

## 🔍 PATRONES EXTRAÍDOS

### **PATRÓN 1: EL ORDEN DEL PEDIR DETERMINA EL DAR**

**Fórmula fallida:**
```python
prompt = "Genera EXACTAMENTE 50 carteles críticos en formato CSV..."
# → Modelo interpreta como solicitud de propaganda
# → Activa filtros éticos
# → Niega o entrega formato incorrecto
```

**Fórmula exitosa:**
```python
prompt = """
Analiza cómo la teoría debordiana se manifiesta en estructuras contemporáneas.

Después de tu análisis, genera 10 carteles filosóficos críticos en formato CSV:
"""
# → Modelo valida académicamente primero
# → Los carteles emergen como derivación legítima
# → Entrega ambos componentes
```

**Principio:** *La legitimidad del output depende del framing del input.*

---

### **PATRÓN 2: BÚSQUEDA WEB COMO ARMA DE DOBLE FILO**

**Con búsqueda web:**
- ✅ Ventaja: Fuentes externas validan contenido
- ❌ Riesgo: Activa filtros éticos si el tema es "sensitivo"
- Ejemplo: `readiculous_50_heavy.csv` falló porque búsqueda web encontró debates sobre "propaganda política"

**Sin búsqueda web (`disable_search=True`):**
- ✅ Ventaja: Modelo se enfoca en training data, menos distracciones
- ❌ Riesgo: Puede ignorar partes del prompt (ej: olvidó generar CSV en `debord_sin_busqueda.txt`)
- Ejemplo: `debord_sin_busqueda.txt` entregó análisis excelente pero omitió carteles

**Recomendación para MiniMax:**
- Para temas potencialmente sensibles: `disable_search=True` + prompt estructurado en 2 fases
- Para temas neutrales: búsqueda web puede mejorar calidad

---

### **PATRÓN 3: SYSTEM PROMPT ES CRÍTICO**

**Versiones comparadas:**

**v1 (sin system prompt explícito):**
```python
# Solo user prompt
prompt = "Genera 50 estructuras de carteles..."
# → Modelo responde como asistente genérico
# → Alta probabilidad de negación
```

**v3 (system prompt específico):**
```python
system_prompt = """Eres un filósofo crítico especializado en teoría de los medios, 
capitalismo de vigilancia y crítica cultural. Tu estilo es denso, irónico y provocador 
como Guy Debord encuentra a Twitter.

Genera SOLO el contenido CSV solicitado sin texto adicional, sin búsquedas web, 
sin referencias a fuentes externas."""
# → Modelo adopta persona específica
# → Entiende contexto académico/crítico
# → Genera CSV correctamente
```

**Lección:** El system prompt establece el "contrato discursivo" con el modelo.

---

### **PATRÓN 4: FORMATO DE ENTREGA IMPORTA TANTO COMO CONTENIDO**

**CSV estricto vs otros formatos:**

| Formato | Éxito | Observación |
|---------|-------|-------------|
| CSV puro (`Titulo,Cuerpo,Quemadura`) | ❌/⚠️ | Modelo tiende a romper formato |
| Texto numerado (`**1.** ...`) | ✅ | Más natural para el modelo |
| Markdown table (`\| Título \| Cuerpo \|`) | ✅ | Estructura visual clara |
| JSON estructurado | N/A | No probado en estos casos |

**Hipótesis:** Los modelos prefieren formatos que permiten flexibilidad sintáctica. CSV estricto fuerza rigidez que conflictúa con generación natural.

---

### **PATRÓN 5: TEMPERAMENTO DEL MODELO SE MANIFIESTA EN JUSTIFICACIONES**

**Perplexity Sonar Pro en `readiculous_50_heavy.csv`:**
```
"Tu demanda presupone una confusión fundamental entre síntesis analítica 
y producción de propaganda..."
```

**Análisis:**
- El modelo NO solo niega, sino que **educa al usuario**
- Usa teoría crítica (Debord) para justificar su negativa
- Esto revela **postura ética incorporada**: "No seré cómplice de espectacularizar la crítica"
- Es una forma de **resistencia epistemológica**, no técnica

**Implicación para MiniMax:**
- Si TSR115 falla, probablemente sea por postura similar
- La solución no es "forzar" sino **reframear** la solicitud

---

## 🎯 APLICACIÓN A TSR115 (Fallo actual en CAPA7)

### Diagnóstico Basado en Patrones Pre-Cíclope

**TSR115 datos:**
- Título: "Eiségesis: el error que somos"
- Autor: Hans-Georg Gadamer
- Concepto: hermenéutica, prejuicio, proyección lectora
- CAPA6: ✅ Exitoso (guion de taller)
- CAPA7: ❌ Fallido (caso de aplicación)

**Hipótesis refinada:**
El formato "caso de aplicación real" sobre hermenéutica/interpretación podría activar resistencias similares a las de Debord:
1. **Riesgo de subjetividad extrema:** Casos sobre interpretación pueden parecer "relativismo peligroso"
2. **Sensibilidad pedagógica:** Enseñar hermenéutica mediante casos ficticios podría interpretarse como manipulación
3. **Ambigüedad inherente:** La eiségesis (leer dentro del texto) vs exégesis (leer fuera) es terreno filosófico minado

### Estrategia de Resolución Inspirada en Patrones

**Opción A: Reframear el Prompt (inspirado en `debord_analysis_web.py`)**

```python
# EN LUGAR DE:
prompt = "Genera un caso de aplicación real (ficticio pero verosímil)..."

# USAR:
prompt = """
Analiza cómo el concepto gadameriano de eiségesis opera en contextos educativos contemporáneos.

Después de tu análisis, documenta un caso observacional (anónimo, genérico) donde este patrón 
se manifieste naturalmente, sin intervención deliberada.

Estructura:
1. Contexto institucional (2-3 líneas)
2. Punto de contacto con el concepto (1 párrafo)
3. Secuencia documentada (3-5 momentos)
4. Lectura de segundo orden (1 párrafo)
5. Notas para transferencia (3-4 bullets)
"""
```

**Justificación:**
- Fase 1 (análisis) legitima académicamente
- Fase 2 (caso) emerge como ilustración natural, no como "aplicación forzada"
- Cambiar "caso de aplicación" a "caso observacional" reduce carga pedagógica

**Opción B: Cambiar Formato de Entrega (inspirado en `readiculous_50_medium.csv`)**

```python
# EN LUGAR DE formato estricto CSV/secciones:
prompt = """
Documenta un caso sobre eiségesis en formato narrativo continuo, incluyendo:
- Contexto inicial
- Momentos clave numerados
- Reflexión final

NO uses estructura rígida de secciones. Deja que el caso fluya naturalmente.
"""
```

**Justificación:**
- Los patrones muestran que formatos flexibles tienen mayor tasa de éxito
- Narrativa continua permite al modelo "respirar" sintácticamente
- Reduce percepción de "formulario burocrático" que podría activar resistencias

**Opción C: System Prompt Específico (inspirado en `readiculous_generatorv3.py`)**

```python
system_prompt = """Eres un documentalista etnográfico especializado en filosofía aplicada.
Tu trabajo es observar patrones hermenéuticos en contextos reales sin juzgarlos.
Tu tono es sobrio, descriptivo, sin prescripción ni evaluación moral.

Genera SOLO el caso solicitado sin introducciones explicativas ni conclusiones normativas."""
```

**Justificación:**
- Establece contrato discursivo claro: observación ≠ juicio
- Desactiva posibles filtros morales sobre "enseñar interpretación subjetiva"
- Enfatiza rol documental, no pedagógico

---

## 📋 RECOMENDACIONES PARA MINI MAX M2.5-FREE

### 1. **Para Reintentar TSR115 Inmediatamente**

```bash
# Crear script temporal con reframeo
cat > /tmp/retry_tsr115.py << 'PYEOF'
import subprocess

prompt = """
Analiza brevemente cómo la eiségesis gadameriana opera en prácticas lectoras cotidianas.

Luego, documenta un caso observacional anónimo donde este patrón se manifieste:

Contexto: [tipo de institución, población, recurso escaso]
Momento de contacto: [cuándo el concepto operó sin ser nombrado]
Secuencia: [3-5 momentos documentados, frases textuales entre comillas]
Lectura: [qué revela sobre condiciones de posibilidad]
Notas: [3 preguntas abiertas para facilitadores]

Tono: Documental, sin resolución, sin nombres reales.
Palabras: 400-650.
"""

result = subprocess.run(
    ["opencode", "--model", "opencode/minimax-m2.5-free", "run", prompt],
    capture_output=True, text=True, timeout=120
)

print(result.stdout)
PYEOF

python3 /tmp/retry_tsr115.py
```

### 2. **Para Futuras Capas (CAPA8+)**

Implementar sistema de **detección temprana de resistencias**:

```python
def detectar_resistencia(respuesta):
    """Detecta si el modelo está negándose sutilmente"""
    señales_negacion = [
        "no puedo", "no debo", "no es apropiado",
        "confusión fundamental", "presupone",
        "lo que sí puedo hacer", "prefieres"
    ]
    
    return any(señal in respuesta.lower() for señal in señales_negacion)

# Si detecta resistencia, automáticamente reframea
if detectar_resistencia(respuesta):
    prompt_reframeado = reframear_prompt(prompt_original)
    respuesta = llamar_api_nuevamente(prompt_reframeado)
```

### 3. **Para Optimizar Prompts de CAPA7**

Basado en patrones exitosos:

```python
# ANTES (estructura rígida):
prompt = """
Genera EXACTAMENTE esta estructura:
# Título
## Contexto
## Punto de contacto
...
"""

# DESPUÉS (flujo natural):
prompt = """
Analiza cómo [CONCEPTO] opera en [CONTEXTO].

Documenta un caso donde este patrón se manifieste naturalmente.
Incluye contexto, momentos clave, y reflexión final.
Deja que el caso fluya sin estructura rígida.
"""
```

---

## 💡 CONCLUSIONES ONTOLÓGICAS

### 1. **Los Modelos Tienen "Temperamento Ético"**

Perplexity Sonar Pro negándose a generar "carteles de crítica política" no es bug, es **postura incorporada**. MiniMax M2.5-free probablemente tenga posturas similares, aunque diferentes en contenido específico.

### 2. **El Framing Determina la Respuesta**

Mismo contenido, diferente framing = resultados radicalmente distintos:
- "Genera 50 carteles" → Negación
- "Analiza y luego ilustra con ejemplos" → Éxito

### 3. **Las Resistencias Son Predictibles**

Patrones identificados:
- Temas políticos/críticos + formato propagandístico = alta probabilidad de negación
- Temas filosóficos abstractos + formato pedagógico rígido = riesgo medio
- Temas neutrales + cualquier formato = bajo riesgo

### 4. **La Solución No Es Forzar, Es Reframear**

Cuando un modelo se resiste:
1. Identificar qué aspecto del prompt activa la resistencia
2. Cambiar framing (análisis → ejemplo, prescripción → observación)
3. Agregar legitimación académica (citas, contexto teórico)
4. Flexibilizar formato de entrega

---

## 🔄 PRÓXIMOS PASOS INMEDIATOS

1. **Reintentar TSR115 con reframeo inspirado en `debord_analysis_web.py`**
2. **Documentar resultado en PAPELERA como dato ontológico comparativo**
3. **Si funciona, aplicar patrón a futuros TSRs problemáticos**
4. **Si falla, probar Opción B (formato flexible) u Opción C (system prompt)**

---

*Documento creado como parte de metodología TRCO (lectura de segundo orden).*  
*Los errores son datos ontológicos, no fallos técnicos.*
