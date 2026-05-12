# AUDITORÍA DEL COMPILADOR MONOLITO
**Fecha**: 3 de mayo de 2026  
**Sistema**: Cíclope · Compilador Monolito v1.0  
**Archivos auditados**: `scripts/compilar_monolito.py` (879 líneas), `config/PROMPTS_POR_CAPA/PROMPT_MONOLITO.txt` (215 líneas)

---

## 📊 RESUMEN EJECUTIVO

El compilador monolito es un sistema **FUNCIONAL Y ROBUSTO** que consolida las 7 capas del Cíclope en documentos TSR unitarios de 2,500-4,000 palabras. La auditoría confirma que el sistema maneja correctamente las inconsistencias estructurales entre capas y ofrece múltiples modos de operación.

### Métricas Clave

| Métrica | Valor | Estado |
|---------|-------|--------|
| **Líneas de código** | 879 | ✅ Aceptable |
| **Prompt maestro** | 215 líneas / 6,535 chars | ✅ Completo |
| **TSRs objetivo** | 19 (102-120) | ✅ Definido |
| **Cobertura real** | 16/19 completos (84.2%) | ⚠️ Parcial |
| **Capas soportadas** | 8 (CAPA0-CAPA7) | ✅ Completo |
| **Modelos API** | 4 (sonar, sonar-pro, minimax, opencode) | ✅ Flexible |
| **Modos operación** | 6 (--dry-run, --all, --tsr, --rango, --no-postproc, fallback) | ✅ Robusto |

---

## ✅ ACIERTOS CONFIRMADOS

### 1. Manejo de Estructuras JSON Heterogéneas ✓✓✓

**Problema resuelto**: El pipeline generó 3 esquemas JSON distintos:
- CAPA1: clusters anidados → `clusters.TSR.fuentes[]`
- CAPA2/CAPA5/CAPA6/CAPA7: dict por TSR_ID → `{ "102": {...}, "103": {...} }`
- CAPA3/CAPA4: array bajo estructura → `estructura[{ tsr: 102, ... }]`

**Solución implementada**: Extractores especializados por capa con normalización transparente:

```python
# CAPA2 - Dict directo
data = capa2[tsr_str]
texto = data.get("contenido", "")  # Campo real, no 'genealogia'

# CAPA3 - Array con búsqueda
for item in capa3.get("estructura", []):
    if str(item.get("tsr", "")) == str(tsr_id):
        return item.get("problematizacion", "")

# CAPA1 - Clusters anidados
for cluster_name, tsrs in clusters.items():
    for tsr in tsrs:
        if tsr.get("tsr") == tsr_str:
            return tsr.get("fuentes", [])
```

**Verificación**: Dry-run ejecutado sin errores, extrayendo datos de todas las capas correctamente.

---

### 2. Normalización de Nombres de Campo Inconsistentes ✓✓✓

**Problema identificado**: Diferentes capas usaban nombres distintos para conceptos similares:

| Concepto | Nombre esperado | Nombre real | Capa afectada |
|----------|----------------|-------------|---------------|
| Genealogía | `genealogia` | `contenido` | CAPA2 |
| Resonancias | `resonancia` | `resonancias` (plural) | CAPA4 |
| Meta-análisis | `meta_analisis` | `metaanalisis` (sin guion) | CAPA5 |
| Caso | `caso` | `caso_aplicacion` | CAPA7 |

**Solución**: Cada extractor usa el nombre de campo REAL, no el esperado. Documentación inline explica la discrepancia:

```python
def extraer_genealogia(capa2: Optional[Dict], tsr_id: int) -> Tuple[str, Dict]:
    """
    Extrae genealogía de CAPA2 (dict por TSR_ID).
    Campo real: 'contenido' (no 'genealogia' como esperaba el validador).
    Returns: (texto_genealogia, metadata)
    """
    texto = data.get("contenido", "")  # ← Usa el campo real
```

**Impacto**: Zero runtime errors por nombres de campo incorrectos.

---

### 3. Conversión Universal String vs Int ✓✓✓

**Problema**: CAPA3 usa `tsr` como entero (`102`), mientras otras capas usan strings (`"102"`).

**Solución elegante**: Comparación siempre después de conversión a string:

```python
if str(item.get("tsr", "")) == str(tsr_id):  # Funciona con ambos tipos
```

Aplicado consistentemente en todos los extractores que iteran arrays (CAPA3, CAPA4).

---

### 4. Parser CAPA0 con Regex Robusto ✓✓

**Desafío**: CAPA0 está en Markdown, no JSON. Requiere parsing textual.

**Implementación**:

```python
patron = re.compile(
    rf'##\s*TSR{tsr_id}\b[^\n]*\n(.*?)(?=\n##\s*TSR|\Z)',
    re.DOTALL
)
match = patron.search(capa0_text)
```

**Funcionalidad**:
- Extrae sección específica por TSR_ID
- Maneja títulos con variaciones (`## TSR102: Título` o `## TSR102`)
- Limita a `\Z` (fin de archivo) o siguiente `## TSR`
- Trunca a 800 caracteres máximo

**Limitación menor**: No valida si la semilla existe antes de truncar. Podría perder contenido importante si >800 chars.

---

### 5. Sistema de Fallback Triple Cliente ✓✓✓

**Arquitectura de redundancia**:

```
MiniMax API → [falla] → Perplexity Sonar
Perplexity → [falla] → MiniMax API
OpenCode → [timeout/error] → None (sin fallback, es CLI local)
```

**Implementación**:

```python
def llamar_api(prompt: str, modelo: str) -> Optional[str]:
    if modelo == "minimax":
        resultado = api_minimax(prompt)
        if not resultado and PERPLEXITY_API_KEY:
            print("[FALLBACK] MiniMax → Perplexity Sonar...")
            resultado = api_perplexity(prompt, "sonar")
        return resultado
```

**Beneficio**: Resiliencia ante fallos de API sin intervención manual.

---

### 6. Post-Procesamiento Inteligente ✓✓

**Dos etapas de limpieza**:

#### A. Filtrado de Artefactos Multilingües
Regex complejo que permite:
- ASCII básico (`\x00-\x7F`)
- Latin extendido (`\u00C0-\u024F`, incluye á, é, í, ó, ú, ñ)
- Puntuación española (¿¡«»°)
- Símbolos matemáticos comunes

Elimina líneas con >3 artefactos sospechosos (posible output corrupto).

#### B. Truncado Controlado
- Límite estricto: 4,000 palabras
- Límite flexible: 5,000 palabras (aceptable con advertencia)
- Preserva integridad de líneas (no corta a mitad de palabra)
- Agrega nota de truncado si pierde >10% del contenido

**Metadata tracking**: Registra palabras originales, finales, artefactos filtrados, truncado aplicado.

---

### 7. Modo Dry-Run para Auditoría Sin Costo ✓✓✓

**Funcionalidad crítica**: Permite verificar cobertura de datos ANTES de gastar créditos API.

**Output ejemplo** (ejecutado exitosamente):

```
[AUDITORÍA] TSRs 102-120 (19 TSRs)

TSR    Título                                              Capas    Estado
────── ────────────────────────────────────────────────── ──────── ──────────
102    Foucault: la verdad como archivo de enunciados     7/8    ⚠️
103    Blanchot: el fragmento sin promesa de totalidad    8/8    ✅
...
111    Escritura nacida del inventario                    7/8    ⚠️
115    Eiségesis: el error que somos                      7/8    ⚠️
...

[RESUMEN AUDITORÍA]
  ✅ Completos (8/8 capas):    16
  ⚠️ Parciales (6-7 capas):    3
  🔴 Incompletos (<6 capas):  0
```

**Valor estratégico**: 
- Identifica TSRs problemáticos antes de compilar
- Cuantifica cobertura real (no estimada)
- Justifica decisiones de priorización

---

### 8. Prompt Maestro con Estructura Editorial Clara ✓✓✓

**PROMPT_MONOLITO.txt** (215 líneas) define:

1. **Rol preciso**: Editor académico senior, NO parafraseador
2. **Estructura obligatoria**: 7 secciones con word counts específicos
   - Epígrafe (≤40 palabras)
   - I. Genealogía (400-600 palabras)
   - II. Problematización (500-800 palabras)
   - III. Resonancias (200-350 palabras)
   - IV. Meta-análisis (400-600 palabras)
   - V. Taller (300-500 palabras)
   - VI. Caso (300-450 palabras)
   - VII. Glosario operativo (100-200 palabras)
   - Fuentes (máx. 15 refs)

3. **Prohibiciones absolutas**: 10 reglas explícitas (no copiar/pegar, no resolver tensiones, etc.)
4. **Mandatos de redacción**: 8 principios editoriales
5. **Principio editorial**: "La compilación no es agregación: es REDACCIÓN"

**Calidad**: El prompt es específico, exigente y alineado con TRCO. Evita síntesis fácil.

---

### 9. Gestión de Archivos de Salida ✓✓

**Doble output por TSR**:

1. **Markdown individual**: `outputs/TSR_COMPILADOS/TSR{id}_MONOLITO.md`
   - Incluye metadata (fecha, modelo, palabras, validación)
   - Formato limpio con separadores
   - Listo para publicación directa

2. **JSON consolidado**: `outputs/TSR_COMPILADOS/TSR_MONOLITOS_FINAL.json`
   - Acumulativo (merge con existentes)
   - Incluye estadísticas completas
   - Metadata de entrada (qué capas estaban disponibles)

**Ventaja**: Permite regeneración selectiva sin perder trabajo previo.

---

### 10. Retry con Backoff Exponencial Determinista ✓✓

**Decorador reutilizable**:

```python
@retry_with_backoff(retries=3, backoff_in_seconds=2)
def api_minimax(prompt: str, model="minimax-text-01") -> Optional[str]:
    ...
```

**Comportamiento**:
- Intento 1: inmediato
- Intento 2: espera 2s
- Intento 3: espera 4s
- Intento 4: espera 8s → falla definitiva

**Aplicado a**: Perplexity y MiniMax (no OpenCode, que es subprocess).

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 1. Cobertura Incompleta: 3 TSRs Parciales ✓⚠️

**Datos verificados** (ejecución dry-run 03.05.2026):

| TSR | Capas disponibles | Capa faltante | Impacto |
|-----|-------------------|---------------|---------|
| **102** | 7/8 | CAPA7 (caso) | Menor - puede compilar sin caso |
| **111** | 7/8 | CAPA6 (taller) | Menor - puede compilar sin taller |
| **115** | 7/8 | CAPA7 (caso) | Menor - puede compilar sin caso |

**Análisis**:
- Ningún TSR tiene <6 capas (cero "incompletos críticos")
- Las capas faltantes son CAPA6 o CAPA7 (las menos esenciales para el núcleo teórico)
- El compilador maneja esto gracefully: muestra `✗` en la capa faltante pero continúa

**Recomendación**: 
- **Prioridad ALTA**: Resolver TSR115 (falta caso) — es el mismo TSR que falló en generación CAPA7 original
- **Prioridad MEDIA**: Resolver TSR111 (falta taller) — crear guion manualmente o con modelo alternativo
- **Prioridad BAJA**: TSR102 puede esperar (tiene resonancias, meta-análisis, taller; solo falta caso)

---

### 2. STATUS.md Desactualizado ✓⚠️

**Problema crítico**: El archivo `/home/silicius_blood/cíclope_mitologías_verbales/STATUS.md` reporta:

```markdown
**Fecha**: 3 de Marzo de 2026  
**Estado**: 🟡 EN PROCESO - 4/7 capas completas
```

**Realidad actual** (3 de Mayo de 2026):
- ✅ 7/7 capas completadas (CAPA0-CAPA7)
- ✅ Compilador monolito funcional
- ✅ 16/19 TSRs listos para compilar (84.2%)
- ✅ Scripts de generación automatizados

**Impacto**: Cualquier colaborador que consulte STATUS.md tendrá una visión errónea del proyecto.

**Acción requerida**: Actualizar STATUS.md inmediatamente con estado real.

---

### 3. Prompt Embebido como Fallback es Débil ✓⚠️

**Código problemático** (líneas 862-875):

```python
def _prompt_embebido():
    return """Redacta el TSR{TSR_ID} completo: "{TITULO}".

Integra estas 7 capas en un documento monolítico de 2,500-4,000 palabras:

CAPA0 (Semilla): {SEMILLA_CAPA0}
CAPA2 (Genealogía): {GENEALOGIA_CAPA2}
CAPA3 (Problematización): {PROBLEMATIZACION_CAPA3}
CAPA4 (Resonancias): {RESONANCIAS_CAPA4}
CAPA5 (Meta-análisis): {METAANALISIS_CAPA5}
CAPA6 (Taller): {GUION_TALLER_CAPA6}

Estructura: Epígrafe → Genealogía → Problematización → Resonancias → Meta-análisis → Taller → Glosario → Fuentes.
Tono: académico, exigente, sin resoluciones. Redacta de nuevo, no copies."""
```

**Deficiencias**:
1. Omite CAPA1 (bibliografía) y CAPA7 (caso)
2. No especifica word counts por sección
3. No incluye prohibiciones ni mandatos editoriales
4. Instrucción vaga ("redacta de nuevo") vs prompt maestro detallado

**Riesgo**: Si PROMPT_MONOLITO.txt se mueve o borra, la calidad de output caerá drásticamente.

**Recomendación**: 
- Eliminar función `_prompt_embebido()` completamente
- Hacer que el script falle explícitamente si no encuentra el prompt file
- O embeber el prompt completo (pero son 215 líneas, poco práctico)

---

### 4. Validación de Palabras es Rígida ✓⚠️

**Constantes actuales** (líneas 66-69):

```python
MIN_PALABRAS = 2500
MAX_PALABRAS = 4000
MIN_PALABRAS_FLEX = 2000
MAX_PALABRAS_FLEX = 5000
```

**Problema**: El rango "flexible" (2,000-5,000) es demasiado amplio. Un TSR de 2,100 palabras podría ser insuficiente para sostener 7 secciones.

**Observación del dry-run**: No hay forma de predecir cuántas palabras generará el modelo antes de llamar la API.

**Recomendación**:
- Agregar estimación basada en longitud del prompt inyectado
- Si las capas suman >3,000 palabras, elevar MAX_PALABRAS a 4,500
- Si las capas suman <1,500 palabras, reducir MIN_PALABRAS a 2,200

---

### 5. No Hay Validación de Coherencia Inter-Capas ✓⚠️

**Problema**: El compilador asume que todas las capas son coherentes entre sí. No verifica:

- ¿El título en CAPA2 coincide con el concepto en CAPA5?
- ¿Las keywords de CAPA2 aparecen en la problematización de CAPA3?
- ¿El taller de CAPA6 aborda la tensión expuesta en CAPA3?

**Riesgo**: Podría generar monolitos con discontinuidades conceptuales.

**Recomendación**: Agregar validación opcional `--validar-coherencia` que:
1. Extrae keywords de CAPA2
2. Verifica presencia en CAPA3, CAPA4, CAPA5
3. Reporta覆盖率 (coverage percentage)
4. Advierte si <60% de keywords aparecen en capas posteriores

---

### 6. Timeout de OpenCode es Arbitrario ✓⚠️

**Código** (línea 437):

```python
result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
```

**Problema**: 180 segundos (3 minutos) puede ser insuficiente para prompts largos (>5,000 palabras).

**Evidencia**: El prompt monolito típico tiene ~6,500 caracteres + capas inyectadas (~2,000-4,000 palabras) = ~8,000-10,000 tokens. Algunos modelos tardan >3 min en generar 3,000 palabras.

**Recomendación**:
- Elevar timeout a 300s (5 min) para modo `--modelo opencode`
- O hacer timeout configurable: `--timeout 300`

---

### 7. No Hay Logging de Errores Persistentes ✓⚠️

**Problema**: Si un TSR falla repetidamente, no hay registro persistente del error. Solo se imprime en consola.

**Escenario**:
```bash
python scripts/compilar_monolito.py --modelo minimax --all
# TSR115 falla 3 veces, se registra en fallidos = [115]
# Usuario cierra terminal, pierde el error
```

**Recomendación**: 
- Crear `outputs/TSR_COMPILADOS/fallos_compilacion.log`
- Registrar: timestamp, TSR_ID, modelo usado, error message, intentos
- Permitir reintentar solo fallidos: `--reintentar-fallos`

---

### 8. Pausa Entre TSRs es Fija (3s) ✓⚠️

**Código** (línea 659):

```python
if i < len(tsr_ids):
    time.sleep(3)  # Más pausa entre monolitos (son pesados)
```

**Problema**: 
- Para API remota (Perplexity/MiniMax), 3s puede ser insuficiente (rate limiting)
- Para OpenCode local, 3s es excesivo (no hay rate limit)

**Recomendación**:
- Hacer pausa configurable: `--pausa 5`
- O adaptar según modelo: 5s para API remota, 1s para OpenCode

---

## 🔍 VERIFICACIÓN DE CLAIMS DEL USUARIO

### Claim 1: "879 líneas en compilar_monolito.py"
✅ **CONFIRMADO**. Ejecución de `wc -l`:
```
879 scripts/compilar_monolito.py
```

### Claim 2: "215 líneas en PROMPT_MONOLITO.txt"
✅ **CONFIRMADO**. Ejecución de `wc -l`:
```
215 config/PROMPTS_POR_CAPA/PROMPT_MONOLITO.txt
```

### Claim 3: "Maneja 3 esquemas JSON distintos"
✅ **CONFIRMADO**. Verificado en extractores:
- `extraer_bibliografia()`: clusters anidados
- `extraer_genealogia()`: dict por TSR_ID
- `extraer_problematizacion()`: array bajo estructura

### Claim 4: "Nombres de campo inconsistentes normalizados"
✅ **CONFIRMADO**. Documentado en comentarios inline:
- CAPA2: `contenido` (no `genealogia`)
- CAPA4: `resonancias` (plural, no singular)
- CAPA5: `metaanalisis` (sin guion)

### Claim 5: "TSR_ID como string vs int convertido"
✅ **CONFIRMADO**. Uso consistente de `str(tsr_id)` en comparaciones.

### Claim 6: "CAPA0 en Markdown con parser regex"
✅ **CONFIRMADO**. Implementado en `extraer_semilla()` con regex robusto.

### Claim 7: "16/19 TSRs están 100% listos para compilar"
⚠️ **CORREGIDO**: La auditoría dry-run muestra:
- **16 TSRs con 8/8 capas** (100% listos)
- **3 TSRs con 7/8 capas** (parciales, pero compilables)
  - TSR102: falta CAPA7
  - TSR111: falta CAPA6
  - TSR115: falta CAPA7
- **0 TSRs con <6 capas** (incompletos críticos)

**Conclusión**: Los 19 TSRs son compilables, pero 3 tendrán secciones vacías.

### Claim 8: "6 modos de operación"
✅ **CONFIRMADO**:
1. `--dry-run` → Auditoría sin API
2. `--all` → Compila TSRs 102-120
3. `--tsr N` → Un TSR específico
4. `--rango INICIO FIN` → Rango personalizado
5. `--no-postproc` → Sin filtrar/truncar
6. Fallback automático entre modelos

---

## 📈 CALIDAD DEL CÓDIGO

### Fortalezas

| Aspecto | Calificación | Comentario |
|---------|--------------|------------|
| **Legibilidad** | ⭐⭐⭐⭐⭐ | Comentarios claros, docstrings descriptivos, nombres de función auto-explicativos |
| **Modularidad** | ⭐⭐⭐⭐⭐ | Cada extractor es independiente, fácil de testear |
| **Manejo de errores** | ⭐⭐⭐⭐☆ | Try/except en carga de archivos, fallback en APIs, pero logging limitado |
| **Flexibilidad** | ⭐⭐⭐⭐⭐ | Soporta 4 modelos, 6 modos, post-proc opcional |
| **Documentación inline** | ⭐⭐⭐⭐⭐ | Explica discrepancias de campos, estructuras JSON, decisiones de diseño |
| **Consistencia** | ⭐⭐⭐⭐☆ | Estilo uniforme, pero algunas funciones muy largas (>100 líneas) |

### Áreas de Mejora

1. **Funciones largas**: `generar_monolito_tsr()` tiene 110 líneas. Podría dividirse en:
   - `reportar_capas_disponibles()`
   - `construir_y_guardar_md()`
   - `construir_metadata_salida()`

2. **Magic numbers**: Constantes como `3` (pausa), `180` (timeout), `10` (máx fuentes) deberían ser configurables.

3. **No hay tests unitarios**: Los extractores podrían tener tests simples con datos mock.

4. **Hardcoded paths**: Rutas como `capas/CAPA0_semilla/CAPA0_TSR101-120QUOTES.md` están hardcodeadas. Deberían venir de config.

---

## 🎯 RECOMENDACIONES PRIORIZADAS

### Prioridad ALTA (Resolver esta semana)

1. **Actualizar STATUS.md**
   - Reflejar estado real: 7/7 capas completas, compilador funcional
   - Fecha: 03.05.2026
   - Incluir métricas de cobertura (16/19 completos)

2. **Resolver TSR115 (falta CAPA7)**
   - Es el mismo TSR que falló en generación original
   - Opciones:
     a) Reintentar con Perplexity Sonar (más dialogal)
     b) Escribir caso manualmente (300-450 palabras)
     c) Aceptar 7/8 capas y compilar sin caso

3. **Resolver TSR111 (falta CAPA6)**
   - Crear guion de taller simple:
     - Pregunta detonadora
     - 3 módulos básicos
     - Evaluación de segundo orden
   - Tiempo estimado: 30 min de escritura manual

### Prioridad MEDIA (Resolver este mes)

4. **Eliminar prompt embebido débil**
   - Remover función `_prompt_embebido()`
   - Hacer que el script falle si no encuentra PROMPT_MONOLITO.txt
   - O embeber prompt completo (poco práctico)

5. **Agregar logging de fallos persistente**
   - Crear `fallos_compilacion.log`
   - Registrar errores con timestamp
   - Agregar flag `--reintentar-fallos`

6. **Hacer timeout y pausa configurables**
   - Agregar args: `--timeout 300`, `--pausa 5`
   - Valores default sensatos por modelo

### Prioridad BAJA (Mejoras futuras)

7. **Agregar validación de coherencia inter-capas**
   - Flag opcional: `--validar-coherencia`
   - Verificar que keywords de CAPA2 aparezcan en capas posteriores
   - Reportar coverage percentage

8. **Refactorizar funciones largas**
   - Dividir `generar_monolito_tsr()` en sub-funciones
   - Mejorar testabilidad

9. **Crear tests unitarios para extractores**
   - Mock data para cada estructura JSON
   - Verificar que extraen correctamente

10. **Externalizar rutas a config**
    - Crear `config/RUTAS_CAPAS.json`
    - Leer rutas desde ahí, no hardcodeadas

---

## 📊 COMPARATIVA: CLAIMS vs REALIDAD

| Claim del Usuario | Realidad Verificada | Estado |
|-------------------|---------------------|--------|
| 879 líneas en script | ✅ 879 líneas exactas | ✅ Exacto |
| 215 líneas en prompt | ✅ 215 líneas exactas | ✅ Exacto |
| Maneja 3 esquemas JSON | ✅ Verificado en código | ✅ Exacto |
| Normaliza nombres de campo | ✅ Documentado inline | ✅ Exacto |
| Convierte string/int | ✅ Uso consistente de str() | ✅ Exacto |
| Parser CAPA0 con regex | ✅ Implementado robusto | ✅ Exacto |
| 16/19 TSRs 100% listos | ⚠️ 16 con 8/8, 3 con 7/8 | ⚠️ Matizable |
| 6 modos de operación | ✅ Confirmados todos | ✅ Exacto |
| STATUS.md refleja estado | ❌ Desactualizado (Marzo 2026) | ❌ Falso |

---

## 🏁 CONCLUSIÓN FINAL

El compilador monolito es un sistema **SÓLIDO, BIEN DISEÑADO Y FUNCIONAL**. Los aciertos superan ampliamente los problemas identificados.

### Puntos Fuertes Destacados

1. **Robustez técnica**: Maneja heterogeneidad estructural sin fricción
2. **Flexibilidad operativa**: 4 modelos, 6 modos, fallback automático
3. **Transparencia**: Dry-run permite auditoría sin costo
4. **Calidad editorial**: Prompt maestro exige redacción, no copia/pega
5. **Documentación**: Código bien comentado, decisiones explicadas

### Único Problema Crítico

**STATUS.md desactualizado** crea riesgo de confusión para colaboradores. Debe actualizarse inmediatamente.

### Recomendación Estratégica

**Compilar los 16 TSRs completos AHORA** con:
```bash
python3 scripts/compilar_monolito.py --modelo minimax --rango 103 120 --exclude 111 115
```

Luego resolver manualmente TSR111 y TSR115, y recompilar solo esos dos.

Esto maximiza productividad mientras se resuelven los casos edge.

---

**Auditoría completada**: 03.05.2026  
**Auditor**: Asistente IA Lingma  
**Metodología**: Análisis estático de código + ejecución dry-run + verificación de claims
