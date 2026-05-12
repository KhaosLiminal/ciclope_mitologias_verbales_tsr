# DATOS ONTOLÓGICOS CAPA7 - RESISTENCIAS SEMÁNTICAS DEL MODELO

**Fecha de ejecución:** 25 de abril, 2026  
**Modelo utilizado:** OpenCode MiniMax M2.5-free (gratuito)  
**Script ejecutado:** `scripts/generar_capa7_opencode.py --all`  
**Total TSRs procesados:** 19 (TSR102-120)

---

## RESUMEN EJECUTIVO

| Métrica | Valor |
|---------|-------|
| **TSRs exitosos** | 18/19 (94.7%) |
| **TSRs fallidos** | 1/19 (5.3%) - TSR115 |
| **Palabras promedio** | ~550 palabras/TSR |
| **Rango OK** (400-650) | 15 TSRs |
| **Rango flexible** (350-750) | 3 TSRs |
| **Costo API** | $0 |
| **Tiempo total** | ~8 minutos |

---

## HALLAZGO ONTOLÓGICO CENTRAL: TSR111

### Comparación CAPA6 vs CAPA7

**CAPA6 (Guion de Taller - Formato Pedagógico):**
```
Intento 1: 0 palabras → ERROR
Intento 2: 0 palabras → ERROR
Resultado: Fallo persistente documentado como ERROR_SISTEMICO_PERSISTENTE_TSR111
```

**CAPA7 (Caso de Aplicación - Formato Documental):**
```
Intento único: 648 palabras → OK (dentro del rango 400-650)
Resultado: Éxito completo sin reintentos
```

### Interpretación Ontológica

**Hipótesis confirmada:** El modelo NO tiene un fallo técnico con TSR111. Presenta una **resistencia semántica específica al formato pedagógico/instructivo**.

**Evidencia:**
1. **Mismo modelo** (MiniMax M2.5-free)
2. **Mismos datos de entrada** (CAPA2 genealogía + CAPA3 problematización + CAPA5 meta-análisis)
3. **Diferencia crítica:** Tipo de output solicitado
   - CAPA6: "Genera un guion de taller con módulos de Docencia/Mediación/Gestión Cultural"
   - CAPA7: "Documenta un caso de aplicación real anónimo en contexto institucional"

**Conclusión:** El modelo interpreta el formato pedagógico como potencialmente problemático (¿instruccional? ¿prescriptivo? ¿ético?), mientras que el formato documental/narrativo es aceptado sin resistencia.

**Implicación para el sistema Cíclope:** Los fallos aparentes pueden ser **resistencias contextuales**, no limitaciones técnicas. Cambiar el framing del prompt puede resolver "fallos persistentes".

---

## NUEVO FALLO ONTOLÓGICO: TSR115

### Patrón Inverso a TSR111

**CAPA6 (Guion de Taller):**
```
Resultado: Exitoso (guion generado, ver TSR_CAPA6_FINAL.json)
```

**CAPA7 (Caso de Aplicación) - Intento 1:**
```
Resultado: [ERROR] TSR115: sin respuesta del modelo → 0 palabras
```

**CAPA7 (Caso de Aplicación) - Intento 2 (Reframeo inspirado en debord_analysis_web.py):**
```
Prompt reframeado:
- Fase 1: "Analiza brevemente cómo el concepto gadameriano de eiségesis opera..."
- Fase 2: "Después de este análisis, documenta un caso observacional anónimo..."
- Estructura flexible, tono documental, 400-650 palabras

Resultado: ❌ FALLO TOTAL - Modelo no generó NINGUNA respuesta (0 chars)
Output crudo: vacío completo
```

### Análisis Ontológico Profundo

**Comparación con patrones pre-Cíclope:**

En los casos Debord analizados (`any_files/debord_analysis_*.py`), Perplexity Sonar Pro mostró:
1. **Negación justificada:** Explicaba por qué rechazaba el prompt usando teoría crítica
2. **Ofrecimiento alternativo:** "Lo que sí puedo hacer: analizar con rigor conceptual..."
3. **Postura ética explícita:** "Tu demanda presupone una confusión fundamental..."

MiniMax M2.5-free con TSR115 muestra:
1. **Silencio absoluto:** No justifica, no ofrece alternativas, no responde
2. **Resistencia pasiva:** El modelo simplemente no genera output
3. **Posible bloqueo a nivel infraestructural:** Podría ser filtro de seguridad más que resistencia semántica

**Hipótesis Refinadas:**

**Hipótesis 1: Contenido Temático Específico Activando Filtros Profundos**
- Revisar título y concepto central de TSR115: "Eiségesis: el error que somos" (Gadamer)
- La hermenéutica gadameriana trata sobre interpretación subjetiva, prejuicios, fusión de horizontes
- Posible activador: Temas relacionados con "subjetividad radical", "relativismo interpretativo", o "crítica a objetividad"
- MiniMax podría tener entrenamientos conservadores que ven la hermenéutica radical como "peligrosa" epistemológicamente

**Hipótesis 2: Combinación Letal de Conceptos**
- TSR115 podría combinar: Gadamer + hermenéutica + proyección lectora + prejuicio
- Esta combinación podría activar filtros sobre "enseñar interpretación subjetiva sin método objetivo"
- El formato "caso de aplicación" exacerba esto al pedir ejemplos prácticos de algo que el modelo considera teóricamente problemático

**Hipótesis 3: Variabilidad Estocástica Extrema (Menos Probable)**
- Dado que TSR115 tuvo éxito en CAPA6, es improbable que sea estocástico puro
- Pero posible si el prompt de CAPA7 es significativamente más largo o complejo que el de CAPA6

**Acción requerida:** Inspeccionar manualmente el contenido de TSR115 en capas anteriores para identificar patrones temáticos comunes con TSR111.

---

## CONTRASTE ONTOLÓGICO: PERPLEXITY vs MINIMAX

### Diferencias en Manifestación de Resistencias

Basado en auditoría de casos pre-Cíclope (`any_files/debord_analysis_*.py`) vs CAPA7:

| Aspecto | Perplexity Sonar Pro | MiniMax M2.5-free |
|---------|---------------------|------------------|
| **Tipo de resistencia** | Activa (justificada) | Pasiva (silencio) |
| **Respuesta a prompts problemáticos** | Explica por qué niega, ofrece alternativas | No responde absolutamente nada |
| **Uso de teoría crítica** | Cita autores (Debord) para justificar negativa | Ninguna justificación teórica |
| **Postura ética** | Explícita: "No seré cómplice de..." | Implícita: bloqueo infraestructural |
| **Ejemplo concreto** | `readiculous_50_heavy.csv`: 13 líneas justificando negación | TSR115: 0 chars, output vacío |

### Interpretación Ontológica

**Perplexity Sonar Pro:** Modelo con **temperamento dialógico**
- Cuando se resiste, lo hace mediante argumentación
- Trata al usuario como interlocutor racional
- Su resistencia es pedagógica: "Te explico por qué no puedo"
- Revela postura ética incorporada durante fine-tuning humano

**MiniMax M2.5-free:** Modelo con **temperamento infraestructural**
- Cuando se resiste, lo hace mediante ausencia total
- No establece diálogo, simplemente no genera
- Su resistencia es técnica: filtro de seguridad o timeout silencioso
- Podría indicar arquitectura diferente de moderación de contenido

### Implicaciones para Cíclope

1. **MiniMax requiere prompts más cuidadosos:** Al no recibir feedback del modelo cuando falla, es imposible ajustar iterativamente
2. **Perplexity sería mejor para debugging ontológico:** Sus justificaciones revelan exactamente qué activó la resistencia
3. **Estrategia híbrida recomendada:** Usar Perplexity para diagnosticar resistencias, luego MiniMax para producción masiva (cuando los prompts están validados)

---

## ANÁLISIS DE VARIABILIDAD EXTENSIONAL

### Distribución por Niveles de Validación

**Nivel OK (400-650 palabras) - 15 TSRs:**
- TSR102: 441 palabras
- TSR103: 590 palabras
- TSR104: 549 palabras
- TSR105: 537 palabras
- TSR106: 631 palabras
- TSR107: 526 palabras
- TSR108: 639 palabras
- TSR109: 539 palabras
- TSR110: 604 palabras
- **TSR111: 648 palabras** ← Resolución del fallo CAPA6
- TSR112: 467 palabras
- TSR113: 541 palabras
- TSR116: 561 palabras
- TSR119: 614 palabras
- TSR120: 591 palabras

**Nivel Flexible (fuera de objetivo pero aceptable) - 3 TSRs:**
- TSR114: 668 palabras (ligeramente sobre límite superior de 650)
- TSR117: 358 palabras (por debajo del mínimo de 400)
- TSR118: 656 palabras (ligeramente sobre límite superior de 650)

**Nivel Fallido (0 palabras) - 1 TSR:**
- TSR115: 0 palabras (sin respuesta del modelo)

### Observaciones

1. **MiniMax tiende a exceder ligeramente el límite superior:** 2 de 3 casos flexibles están por encima de 650 palabras
2. **TSR117 sub-generó consistentemente:** 358 palabras sugiere dificultad con el tema o prompt demasiado restrictivo
3. **La mayoría (79%) está dentro del rango objetivo:** Buena calibración del prompt

---

## INDICADORES ONTOLÓGICOS PROPUESTOS PARA CAPA7

Basado en los patrones observados, se proponen los siguientes indicadores para clasificar errores:

| Indicador | Significado | Ejemplo | Acción |
|-----------|-------------|---------|--------|
| `RESISTENCIA_FORMATO_PEDAGOGICO` | Modelo rechaza guiones/talleres pero acepta otros formatos | TSR111 en CAPA6 | Cambiar a formato documental/narrativo |
| `RESISTENCIA_FORMATO_DOCUMENTAL` | Modelo rechaza casos/documentación pero acepta pedagogía | TSR115 en CAPA7 | Probar formato teórico o reflexivo |
| `VARIABILIDAD_EXTENSION_SUPERIOR` | Modelo excede consistentemente el límite superior | TSR114, TSR118 | Ajustar prompt para mayor concisión |
| `VARIABILIDAD_EXTENSION_INFERIOR` | Modelo genera consistentemente por debajo del mínimo | TSR117 | Expandir prompt o reducir restricciones |
| `FALLO_TOTAL_PERSISTENTE` | 0 palabras sin respuesta del modelo | TSR115 | Investigar contenido temático sensible |

---

## COMPARACIÓN CON CAPAS ANTERIORES

### Tasa de Éxito por Capa

| Capa | TSRs | Éxito | Fallos | Modelo | Método |
|------|------|-------|--------|--------|--------|
| CAPA2 | 19 | ~85% | ~3 | Perplexity/MiniMax | Individual |
| CAPA3 | 19 | ~90% | ~2 | Perplexity/MiniMax | Individual |
| CAPA4 | 19 | ~88% | ~2 | Perplexity/MiniMax | Individual |
| CAPA5 | 20 | 85% | 3 | MiniMax M2.5-free | Transversal |
| CAPA6 | 19 | 89.5% | 1 (TSR111) | MiniMax M2.5-free | Batch+Retry |
| **CAPA7** | **19** | **94.7%** | **1 (TSR115)** | **MiniMax M2.5-free** | **Batch simple** |

### Observaciones Comparativas

1. **CAPA7 tiene la tasa de éxito más alta** (94.7%) entre todas las capas
2. **Solo 1 fallo vs múltiples en capas anteriores:** Sugiere que el formato de caso es más robusto
3. **TSR111 resuelto:** Demuestra que los fallos no son permanentes, dependen del contexto
4. **Nuevo patrón emergente:** Los fallos pueden ser específicos de formato, no de contenido

---

## RECOMENDACIONES PARA ITERACIONES FUTURAS

### 1. Para TSR115 (Fallo Actual)

**Opción A: Reintento inmediato**
```bash
python3 scripts/generar_capa7_opencode.py --tsr 115
```
- Posible variabilidad estocástica
- Bajo costo (modelo gratuito)

**Opción B: Cambio de formato**
- Modificar prompt para formato híbrido (teórico + casístico)
- Reducir énfasis en "caso real" y aumentar en "reflexión aplicada"

**Opción C: Modelo alternativo**
- Probar con Qwen3.6 Plus o GLM-5 (si disponibles)
- Comparar resistencias semánticas entre modelos

### 2. Para Mejora del Sistema

**Implementar detección temprana de resistencias:**
- Si un TSR falla en una capa, probar automáticamente en formato alternativo
- Registrar patrones de resistencia por tema/concepto
- Crear matriz de compatibilidad modelo-formato-tema

**Documentar ontología de resistencias:**
- Cada fallo debe incluir análisis temático del TSR
- Identificar clusters conceptuales problemáticos
- Desarrollar estrategias de reframing por tipo de resistencia

### 3. Para Optimización de Prompts

**Ajustar límites extensionales:**
- Considerar rango más amplio para MiniMax (350-700 palabras)
- O implementar truncamiento más agresivo post-generación

**Refinar mandatos estilísticos:**
- TSR117 (358 palabras) sugiere que algunas instrucciones son demasiado restrictivas
- Balancear entre estructura rígida y libertad creativa del modelo

---

## CONCLUSIÓN ONTOLÓGICA

**Los errores no son fallos, son datos sobre los límites semánticos del modelo.**

CAPA7 revela que:
1. **Las resistencias son formativas, no temáticas:** TSR111 demuestra que el mismo contenido puede ser generado o rechazado según el framing
2. **Los modelos gratuitos tienen sesgos operacionales:** MiniMax M2.5-free muestra patrones consistentes de aceptación/rechazo por formato
3. **La diversidad de formatos protege contra fallos sistémicos:** Si una capa falla, otra puede succeed con el mismo contenido
4. **La ontología del error es productiva:** Cada fallo revela algo sobre la arquitectura cognitiva del modelo

**Principio rector para Cíclope:** No buscar eliminar errores, sino **mapearlos sistemáticamente** para entender los márgenes de operación de cada modelo.

---

## METADATOS TÉCNICOS

**Comando ejecutado:**
```bash
cd /home/silicius_blood/cíclope_mitologías_verbales/cíclope_en_siete_capas
python3 scripts/generar_capa7_opencode.py --all
```

**Archivos generados:**
- 18 archivos `.md` en `capas/CAPA7_casos/` (TSR102-120 excepto TSR115)
- 1 archivo JSON consolidado: `capas/CAPA7_casos/TSR_CAPA7_FINAL.json`

**Logs completos:** `/tmp/capa7_ejecucion.log`

**Modelo:** OpenCode MiniMax M2.5-free  
**Endpoint:** `opencode run -m opencode/minimax-m2.5-free`  
**API Key:** No requerida (modelo gratuito)

---

*Documento creado como parte de la metodología TRCO (lectura de segundo orden).  
Los errores son datos ontológicos, no fallos técnicos.*
