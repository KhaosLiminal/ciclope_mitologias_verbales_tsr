# Glosario: Términos Clave del Proyecto Cíclope

---

## 🎯 Conceptos Fundamentales

### **TSR (Trabajo de Síntesis de Referencia)**
- **Definición**: Documento académico de 4000-5500 palabras que explora un concepto teórico desde múltiples perspectivas sin buscar síntesis final.
- **Características**: Mantiene tensiones dialécticas, conecta teoría clásica con cultura digital, estructura modular en 7 capas.
- **Ejemplo**: TSR102 sobre "Fragmento Digital" explora cómo los fragmentos clásicos dialogan con memes y NFTs.

### **Cíclope como Método**
- **Definición**: Enfoque epistemológico que asume la parcialidad como rigor metodológico.
- **Principios**: Visión monocular (un ángulo deliberadamente parcial), campo de tensiones (no totalidad), claridad de posición.
- **Aplicación**: Cada TSR es un "ojo" que ve potentemente desde su ángulo específico.

### **Reflejos Híbridos**
- **Definición**: Universo conceptual donde lo humano y lo tecnológico coexisten sin jerarquía.
- **Premisa**: La autoría es negociación con sistemas probabilísticos, la lectura de segundo orden observa cómo interpretamos.
- **Contexto**: Respuesta a la escritura asistida por IA y crisis de la autoría tradicional.

---

## 🔧 Términos Técnicos

### **Sistema de 8 Capas**
- **CAPA0**: Semillas conceptuales - Frases fundacionales que inician cada TSR
- **CAPA1**: Bibliografías verificadas - 235 fuentes académicas por concepto
- **CAPA2**: Genealogías conceptuales - Historia del concepto (650-800 palabras)
- **CAPA3**: Problematizaciones contemporáneas - Aplicación actual (1000-1500 palabras)
- **CAPA4**: Resonancias interdisciplinarias - Conexiones con otros campos (400-600 palabras)
- **CAPA5**: Meta-análisis - Reflexión sobre el propio TSR
- **CAPA6**: Talleres - Lecciones prácticas basadas en el TSR
- **CAPA7**: Casos de estudio aplicados - Ejemplos concretos y análisis


### **TRCO (Sistema de Lectura)**
- **Definición**: Metodología de lectura de segundo orden que observa los marcos de interpretación.
- **Función**: No interpreta mejor, sino hace visibles las condiciones de posibilidad del sentido.
- **Aplicación**: En docencia, mediación cultural, gestión de proyectos.

### **Perplexity Sonar API**
- **Definición**: Servicio de IA que combina búsqueda web con generación de contenido.
- **Uso en proyecto**: Verificación de citas, generación de contenido académico, búsqueda de fuentes.
- **Configuración**: Requiere API key y plan Pro para mejores resultados.

---

## 📚 Conceptos Teóricos

### **Lectura de Segundo Orden**
- **Definición**: Práctica de observar cómo se activan los marcos que hacen posible que algo signifique.
- **Diferencia**: Primer orden = qué significa; Segundo orden = cómo significa.
- **Ejemplos**: Leer consignas académicas, dispositivos de circulación cultural, economías simbólicas.

### **Tensión Dialéctica**
- **Definición**: Oposición productiva entre conceptos que no busca resolución.
- **Característica**: Mantiene la diferencia como fuente de pensamiento, no como problema a resolver.
- **Ejemplo**: Clásico vs Digital, Humano vs IA, Original vs Copia.

### **Campo de Tensiones**
- **Definición**: Territorio conceptual mapeado por las oposiciones productivas.
- **Función**: Los 19 TSR no suman una totalidad, sino mapean este campo.
- **Metáfora**: Como un mapa de corrientes marinas, no de continentes.

---

## 🏗️ Arquitectura del Proyecto

### **Clúster Visual**
- **Definición**: Imagen reproducible manualmente que condensa conceptualmente el TSR.
- **Características**: Fragmentada, numerada, reproducible sin degradación.
- **Función**: Umbral que no ilustra sino condensa el contenido.

### **Metadata Enriquecida**
- **Definición**: Información estructurada asociada a cada concepto (keywords, cluster, autor, obra).
- **Componentes**: Términos canónicos, relaciones conceptuales, contexto histórico.
- **Uso**: Inyección en prompts para mantener coherencia terminológica.

### **Validación de Coherencia**
- **Definición**: Proceso automático que verifica consistencia terminológica entre capas.
- **Mecanismo**: Compara términos del glosario con contenido generado.
- **Objetivo**: Mantener rigor conceptual y evitar derivas semánticas.

---

## 🔄 Procesos y Flujos

### **Generación Secuencial**
- **Definición**: Proceso obligatorio de generar capas en orden (1→2→3→4).
- **Razón**: Cada capa depende de outputs de capas anteriores.
- **Ejemplo**: CAPA3 usa genealogías de CAPA2 para problematizar.

### **Compilación Final**
- **Definición**: Proceso de unir todas las capas en un TSR completo.
- **Formato**: Markdown estructurado para diseño en Canva/PDF.
- **Validación**: Revisión final de extensión, estructura y coherencia.

### **Retry Logic con Backoff Exponencial**
- **Definición**: Estrategia de reintentos automáticos para llamadas API fallidas.
- **Mecanismo**: Espera progresiva entre reintentos para evitar rate limiting.
- **Configuración**: MAX_REINTENTOS, DELAY_INICIAL, FACTOR_BACKOFF.

---

## 📊 Métricas y Validación

### **Word Count por Capa**
- **CAPA2**: 650-800 palabras (genealogías)
- **CAPA3**: 1000-1500 palabras (problematizaciones)
- **CAPA4**: 400-600 palabras (resonancias)
- **Total TSR**: 4000-5500 palabras

### **Tasa de Éxito API**
- **Métrica**: Porcentaje de llamadas exitosas vs fallidas
- **Objetivo**: >90% éxito con retry logic
- **Monitoreo**: Logs detallados en carpeta debug/

### **Coherencia Terminológica**
- **Métrica**: Porcentaje de términos del glosario presentes en contenido
- **Objetivo**: >80% de términos canónicos integrados
- **Validación**: Script automático de verificación

---

## 🚨 Errores Comunes

### **Drift Semántico**
- **Definición**: Cambio gradual en el significado de términos clave entre capas.
- **Causa**: Falta de validación de coherencia terminológica.
- **Solución**: Inyectar glosario canónico en prompts y validar.

### **Forzar Síntesis**
- **Error**: Resolver tensiones conceptuales en lugar de mantenerlas.
- **Consecuencia**: Pierde el propósito del método Cíclope.
- **Prevención**: Revisión humana de cada capa.

### **Citas No Verificadas**
- **Error**: Aceptar referencias generadas sin verificar URLs.
- **Riesgo**: Citas falsas o inexistentes.
- **Solución**: Siempre usar search_web para verificar.

---

## 📖 Recursos Relacionados

- **Roland Barthes**: "La muerte del autor"
- **Foucault**: "¿Qué es un autor?"
- **Teoría de archivos**: Estudios sobre memoria y documentación
- **Crítica digital**: Estudios sobre tecnología y cultura

---

**Última actualización**: Marzo 2026  
**Proyecto**: Cíclope: Mitologías Verbales  
**Sistema**: Reflejos Híbridos/TRCO
