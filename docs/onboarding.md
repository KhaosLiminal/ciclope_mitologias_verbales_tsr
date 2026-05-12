# Onboarding: Guía para Nuevos Colaboradores

## 🎯 Bienvenido al Proyecto Cíclope

Esta guía te ayudará a entender rápidamente qué es este proyecto y cómo puedes contribuir.

---

## 📖 ¿Qué necesitas saber primero?

### Conceptos Fundamentales

**TSR (Trabajo de Síntesis de Referencia)**
- Documento académico de 4000-5500 palabras
- Explora un concepto teórico desde múltiples ángulos
- No busca resolver tensiones, sino mantenerlas productivas

**Sistema de 8 Capas**
- Cada TSR se construye en 8 etapas secuenciales
- Las capas dependen entre sí (orden obligatorio)
- Cada capa añade profundidad y complejidad

**Cíclope como Método**
- Cada TSR es una perspectiva "monocular" (parcial pero rigurosa)
- No buscamos objetividad, sino claridad de posición
- Los 19 TSR mapean un campo de tensiones conceptuales

---

## 🚀 Primeros Pasos

### 1. Configuración Técnica

```bash
# Clonar el repositorio
git clone [URL_DEL_REPOSITORIO]
cd cíclope_mitologías_verbales

# Configurar entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r cíclope_en_siete_capas/requirements.txt

# Configurar API Key de Perplexity
export PERPLEXITY_API_KEY="tu_api_key_aquí"
```

### 2. Entender la Estructura

```
cíclope_mitologías_verbales/
├── README.md              # Visión general del proyecto
├── cíclope_en_siete_capas/ # Sistema técnico
│   ├── scripts/           # Scripts de generación
│   ├── capas/            # Resultados por capa
│   └── config/           # Configuración
├── docs/                 # Documentación extendida
└── outputs/              # TSR finales compilados
```

---

## 🔄 Flujo de Trabajo Estándar

### Para Generar TSR Completos

1. **Preparación**
   - Verificar API Key configurada
   - Revisar que capas anteriores existan

2. **Ejecución Secuencial**
   ```bash
   # CAPA0: Semillas (ya existen)
   # Las semillas están en cíclope_en_siete_capas/capas/CAPA0_semilla/
   
   # CAPA1: Bibliografías
   python cíclope_en_siete_capas/scripts/TSR_CAPA1_Completa.py
   
   # CAPA2: Genealogías
   python cíclope_en_siete_capas/scripts/consolidar_capa2_final.py
   
   # CAPA3: Problematizaciones
   python cíclope_en_siete_capas/scripts/generar_capa3.py --all
   
   # CAPA4: Resonancias
   python cíclope_en_siete_capas/scripts/generar_capa4.py --all
   
   # CAPA5: Meta-análisis (próximo paso)
   # python cíclope_en_siete_capas/scripts/generar_capa5.py --all
   
   # CAPA6: Talleres (pendiente)
   # python cíclope_en_siete_capas/scripts/generar_capa6.py --all
   
   # CAPA7: Casos de estudio (pendiente)
   # python cíclope_en_siete_capas/scripts/generar_capa7.py --all
   ```

3. **Validación**
   ```bash
   # Validar coherencia entre capas
   python cíclope_en_siete_capas/scripts/validar_coherencia_capas.py
   ```

---

## ⚠️ Problemas Comunes y Soluciones

### Error: API Key no configurada
```bash
# Verificar que esté configurada
echo $PERPLEXITY_API_KEY

# Si no aparece, configurar nuevamente
export PERPLEXITY_API_KEY="tu_api_key"
```

### Error: Dependencias faltantes
```bash
# Reinstalar dependencias
pip install -r cíclope_en_siete_capas/requirements.txt --force-reinstall
```

### Error: Capas anteriores no existen
- Las capas deben generarse en orden (1→2→3→4)
- Verificar que archivos JSON existan en `cíclope_en_siete_capas/capas/`

### Resultados vacíos o incompletos
- Revisar logs de error en consola
- Verificar conexión a internet
- Validar formato de archivos de entrada

---

## 🔍 Cómo Revisar Calidad

### Checklist para TSR Completos

- **Extensión**: 4000-5500 palabras totales
- **Estructura**: Todas las 7 capas presentes
- **Coherencia**: Términos consistentes entre capas
- **Citas**: Bibliografía verificada y relevante
- **Tensión**: Conceptos sin resolución forzada

### Herramientas de Validación

```bash
# Validar coherencia terminológica
python cíclope_en_siete_capas/scripts/validar_coherencia_capas.py

# Generar reporte de estado
python cíclope_en_siete_capas/scripts/generar_reporte_estado.py
```

---

## 🤖 Trabajando con IA

### Buenas Prácticas

1. **Verificar siempre** las citas y referencias generadas
2. **Revisar coherencia** terminológica entre capas
3. **Mantener la tensión** conceptual (no forzar síntesis)
4. **Validar extensión** y estructura de cada sección

### Qué Evitar

- No dejar que la IA resuelva tensiones conceptuales
- No aceptar citas sin verificar URLs
- No permitir mezcla de estilos o voces
- No omitir validación humana

---

## 📚 Recursos Adicionales

- **[Filosofía del Proyecto](filosofia.md)** - Ensayo sobre el método Cíclope
- **[Arquitectura del Sistema](arquitectura.md)** - Diagramas y flujo
- **[Glosario](glosario.md)** - Términos clave definidos
- **[Guía Técnica](../cíclope_en_siete_capas/README.md)** - Detalles de implementación

---

## 🆘 Pedir Ayuda

Si encuentras problemas:

1. **Revisa este documento** primero
2. **Consulta los logs** de error detallados
3. **Verifica el estado** actual de las capas
4. **Documenta el problema** específico antes de pedir ayuda

---

## ✅ Checklist de Onboarding

- [ ] API Key de Perplexity configurada
- [ ] Dependencias instaladas correctamente
- [ ] Estructura del proyecto comprendida
- [ ] Flujo de trabajo secuencial entendido
- [ ] Herramientas de validación probadas
- [ ] Documentación clave leída

---

**¡Listo para empezar!** 

Ahora puedes generar tu primer TSR completo siguiendo el flujo estándar.
