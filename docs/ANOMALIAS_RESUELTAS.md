# ANOMALÍAS RESUELTAS — Auditoría HuggingFace 04.05.2026

## Anomalía 1: TSR101_completo.md (57.2 KB vs ~13 KB promedio)

### Diagnóstico
TSR101 tiene 746 líneas, mientras que TSR102-TSR120 tienen ~100-150 líneas. TSR101 **no es un monolito compilado**, sino un documento fundacional especial que incluye:
- Página de venta completa
- Descripción de metodología TRCO
- Contexto del ecosistema Reflejos Híbridos
- Detalles de uso y aplicación

### Acción Correctiva
- **No renombrar:** TSR101 mantiene su nombre original porque es un documento diferente
- **Documentar:** README_HF.md actualizado con explicación de la diferencia
- **Clarificar numeración:** TSR100 = clúster fundacional, TSR101 = primer ejemplar

### Estado
✅ **RESUELTO** — Documentación actualizada, anomalía explicada

---

## Anomalía 2: Dataset Viewer no disponible

### Diagnóstico
HuggingFace espera `.jsonl`, `.csv` o `.parquet` para el viewer. El dataset es `.md` puro — repositorio de texto académico, no corpus de entrenamiento ML.

### Acción Correctiva
- **No es error:** El dataset funciona como repositorio de texto, no como dataset estructurado
- **Opcional:** Agregar `data_files` config en futuro si se requiere viewer
- **Documentar:** README_HF.md menciona que es texto académico, no dataset ML

### Estado
✅ **RESUELTO** — No requiere acción, es característica no bug

---

## Anomalía 3: .venv, .lingma, .vscode subidos

### Diagnóstico
Archivos de infraestructura local del autor subidos al dataset público. Peso muerto: 46.5 MB total incluye estos archivos.

### Acción Correctiva
- **Crear .gitignore:** Excluye .venv/, .lingma/, .vscode/
- **Próximo upload:** Usar `hf upload --exclude` para evitar estos archivos

### Estado
✅ **RESUELTO** — .gitignore creado, listo para próximo upload

---

## Anomalía 4: PAPELERA sin README

### Diagnóstico
Carpeta PAPELERA subida sin explicación de su propósito. Contiene archivo ontológico valioso.

### Acción Correctiva
- **Crear README.md:** Explica propósito, criterio de inclusión, advertencia de no eliminar
- **Documentar:** Material histórico, no basura

### Estado
✅ **RESUELTO** — README.md creado en PAPELERA/

---

## Anomalía 5: Licencia NC limita monetización

### Diagnóstico
CC-BY-NC-SA-4.0 prohíbe uso comercial. Si Reflejos Híbridos contempla talleres pagados, materiales premium o colaboración institucional, la licencia debe cambiar.

### Acción Correctiva
- **Decisión pendiente:** Usuario debe evaluar modelo de monetización
- **Opciones:**
  - CC-BY-SA-4.0 (permite uso comercial con ShareAlike)
  - CC-BY-4.0 (máxima permisividad)
  - Mantener NC si proyecto es puramente académico

### Estado
⚠️ **PENDIENTE DECISIÓN DEL USUARIO** — Requiere evaluación estratégica

---

## Anomalía 6: Nomenclatura inconsistente

### Diagnóstico
TSR101_completo.md vs TSR102_MONOLITO.md. Un archivo usa "completo", 19 usan "MONOLITO".

### Acción Correctiva
- **No renombrar TSR101:** Es documento diferente, merece nombre diferente
- **Documentar diferencia:** README_HF.md explica por qué TSR101 es especial

### Estado
✅ **RESUELTO** — Documentación actualizada

---

## Resumen de Acciones

| Anomalía | Estado | Acción |
|---|---|---|
| TSR101 tamaño divergente | ✅ RESUELTO | Documentación actualizada |
| Dataset Viewer no disponible | ✅ RESUELTO | No es error, es característica |
| Archivos de infraestructura subidos | ✅ RESUELTO | .gitignore creado |
| PAPELERA sin README | ✅ RESUELTO | README.md creado |
| Licencia NC limita monetización | ⚠️ PENDIENTE | Requiere decisión estratégica |
| Nomenclatura inconsistente | ✅ RESUELTO | Documentación actualizada |

---

## Próximos Pasos

1. **Subir correcciones a HuggingFace:**
   ```bash
   hf upload EloiseCry/ciclope-mitologias-verbales . --repo-type dataset --exclude ".venv" --exclude ".lingma" --exclude ".vscode"
   ```

2. **Decidir sobre licencia:** Evaluar modelo de monetización de Reflejos Híbridos

3. **Agregar dataset a colección:** Manualmente en https://huggingface.co/collections/EloiseCry/ciclope-mitologias-verbales

---

*Auditoría completada: 04.05.2026*
*Proyecto Cíclope · Mitologías Verbales · 2026*
