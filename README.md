<img width="1280" height="640" alt="CÍCLOPE (2)" src="https://github.com/user-attachments/assets/40676aaa-53c1-4443-b798-6c4357d5a387" />

---
**MIT License**

task_categories:
  - text-generation
  - text-classification
language:
  - es
tags:
  - philosophy
  - literary-theory
  - critical-theory
  - reading-methodology
  - second-order-reading
  - cíclope
  - mitologías-verbales
size_categories:
  - 10K<n<100K
---

# Cíclope: Mitologías Verbales

## Descripción

**Cíclope** es un sistema de lectura de segundo orden que genera **TSRs (Thematic Semantic Reports)** mediante una arquitectura de 7 capas progresivas. Cada TSR es un documento monolítico que consolida:

- **CAPA 0:** Semilla conceptual (quote detonante)
- **CAPA 1:** Bibliografía verificada
- **CAPA 2:** Genealogía conceptual
- **CAPA 3:** Problematización contemporánea
- **CAPA 4:** Resonancias con Reflejos Híbridos
- **CAPA 5:** Meta-análisis
- **CAPA 6:** Guion de taller
- **CAPA 7:** Caso de aplicación

## Estructura del Dataset

```
├── cíclope_en_siete_capas/
│   ├── capas/                    # 7 capas originales en JSON
│   │   ├── CAPA0_semilla/
│   │   ├── CAPA1_bibliografia/
│   │   ├── CAPA2_genealogia/
│   │   ├── CAPA3_problematizacion/
│   │   ├── CAPA4_resonancias/
│   │   ├── CAPA5_metanalisis/
│   │   ├── CAPA6_talleres/
│   │   └── CAPA7_casos/
│   ├── outputs/
│   │   └── TSR_COMPILADOS/       # 19 TSRs monolíticos en Markdown
│   └── scripts/                  # Scripts de compilación
├── docs/                         # Documentación adicional
└── STATUS.md                     # Estado actual del proyecto
```

## Contenido

- **1 TSR fundacional** (TSR101 - documento completo de 57KB con página de venta, metodología TRCO y descripción del proyecto)
- **19 TSRs monolíticos** (TSR102-TSR120 - compilaciones de 7 capas, ~13KB cada uno)
- **7 capas de datos** en formato JSON
- **Scripts de compilación** en Python
- **Documentación filosófica** y arquitectónica

### Nota sobre numeración TSR100 vs TSR101

**TSR100** es el nombre del clúster fundacional (Cíclope). **TSR101** es el primer ejemplar de ese clúster. La numeración TSR102-TSR120 corresponde a los 19 TSRs subsecuentes del mismo ciclo. TSR101 es un documento especial que incluye página de venta, descripción de metodología TRCO y contexto del ecosistema Reflejos Híbridos, mientras que TSR102-TSR120 son monolitos compilados de las 7 capas con estructura uniforme.

## Uso

### Descarga via CLI

```bash
# Descargar dataset completo
hf download EloiseCry/ciclope-mitologias-verbales

# Descargar solo TSRs monolíticos
hf download EloiseCry/ciclope-mitologias-verbales --include "cíclope_en_siete_capas/outputs/TSR_COMPILADOS/*"
```

### Uso en Python

```python
from datasets import load_dataset

# Cargar dataset
dataset = load_dataset("EloiseCry/ciclope-mitologias-verbales")

# Acceder a TSRs
for tsr in dataset['train']:
    print(tsr['titulo'], tsr['contenido'])
```

## Metodología: TRCO (Técnica de Lectura de Segundo Orden)

Cíclope implementa una metodología de lectura que:

1. **Identifica tensiones** conceptuales irresolubles
2. **Mapea campos conceptuales** sin resolver forzadamente
3. **Documenta el proceso** como parte del output
4. **Genera objetos editoriales** coleccionables

## Filosofía

Este proyecto opera bajo la premisa de que **la curación no es selección neutral**, sino montaje crítico que genera sentido desde la tensión entre fuentes. Cada TSR es un artefacto de lectura profunda, no divulgación superficial.

## Proyecto Relacionado

- **Reflejos Híbridos:** [substack.reflejoshibridos.com](https://substack.reflejoshibridos.com)
- **Gumroad TSRs:** [eloisecry.gumroad.com](https://eloisecry.gumroad.com)

## Licencia

**CC BY-NC-SA 4.0** - Uso no comercial obligatorio, derivados deben compartir bajo misma licencia.

## Cita

```bibtex
@misc{ciclope2026,
  author = {Eloise Cry},
  title = {Cíclope: Mitologías Verbales - Sistema de Lectura de Segundo Orden},
  year = {2026},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/EloiseCry/ciclope-mitologias-verbales}
}
```

## Autor

**Eloise Cry** - [@puentesincluyentes](https://twitter.com/puentesincluyentes)

---

*Proyecto Cíclope · Mitologías Verbales · 2026*
*Sistema de Lectura de Segundo Orden (TRCO)*
