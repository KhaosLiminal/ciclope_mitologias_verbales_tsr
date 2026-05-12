"""
════════════════════════════════════════════════════════════════════════════════
TSR CAPA 1: BIBLIOGRAFÍA VERIFICADA - VERSIÓN ROBUSTA
════════════════════════════════════════════════════════════════════════════════
Mejoras implementadas:
✅ Extracción robusta de JSON (maneja Markdown, texto extra, comillas tipográficas)
✅ Sistema de 3 reintentos automáticos con delays inteligentes
✅ Validación post-generación de estructura
✅ Guardado automático de respuestas problemáticas para debug
✅ Aumento de max_tokens a 5000
✅ Prompt más estricto para forzar JSON puro
✅ Delays adaptativos entre requests
════════════════════════════════════════════════════════════════════════════════
"""

from perplexity import Perplexity
import json
import re
import time
from datetime import datetime
import os

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════

client = Perplexity()

# TSRs QUE FALLARON (solo estos se reintentarán)
TSR_FALLIDOS = [
    {
        "numero": "102",
        "cluster": "I. Autoría, Escritura, Fragmento",
        "titulo": "Foucault: la verdad como archivo de enunciados",
        "autor_primario": "Michel Foucault",
        "obra_primaria": "¿Qué es un autor?",
        "año": 1969,
        "concepto_central": "función-autor",
        "keywords": ["autor como función", "enunciado", "episteme", "arqueología del saber", "condiciones de existencia discursiva"],
        "autores_secundarios": ["Roland Barthes", "Umberto Eco"],
        "conexion_RH": "IA generativa y autoría algorítmica",
        "glitch_conceptual": "El autor no desaparece: se convierte en función que opera desde la sombra"
    },
    {
        "numero": "106",
        "cluster": "II. Pigmentos, Color, Mercado, Poder",
        "titulo": "Colores como botín teológico",
        "autor_primario": "Victoria Finlay",
        "obra_primaria": "Color: A Natural History of the Palette",
        "año": 2002,
        "concepto_central": "economía política del color",
        "keywords": ["lapislázuli", "ultramarino", "cochinilla", "comercio medieval", "teología del mercado"],
        "autores_secundarios": ["Michel Pastoureau", "Anne Varichon"],
        "conexion_RH": "Paletas de color en diseño digital: ¿acceso universal o uniformización?",
        "glitch_conceptual": "El color es código. La escasez es teología. El mercado es liturgia"
    },
    {
        "numero": "107",
        "cluster": "II. Pigmentos, Color, Mercado, Poder",
        "titulo": "El azul sintético como democratización o pérdida de aura",
        "autor_primario": "Walter Benjamin",
        "obra_primaria": "La obra de arte en la época de su reproductibilidad técnica",
        "año": 1936,
        "concepto_central": "aura y reproducción técnica",
        "keywords": ["Jean Baptiste Guimet", "ultramarino sintético", "democratización del arte", "pérdida de aura", "mercado pigmentos"],
        "autores_secundarios": ["Victoria Finlay", "Michel Pastoureau"],
        "conexion_RH": "Filtros de Instagram: democratización estética o estandarización visual",
        "glitch_conceptual": "¿Se liberó el arte o perdió el color su aura sagrada?"
    },
    {
        "numero": "110",
        "cluster": "II. Pigmentos, Color, Mercado, Poder",
        "titulo": "El color como ventana mística",
        "autor_primario": "Yves Klein",
        "obra_primaria": "Anthropométries (serie 1960)",
        "año": 1960,
        "concepto_central": "experiencia mística del color",
        "keywords": ["monocromo", "experiencia perceptual", "disolución sujeto-objeto", "océano azul", "estado alterado"],
        "autores_secundarios": ["Mark Rothko", "Wassily Kandinsky"],
        "conexion_RH": "Pantallas LED: ¿el aura sobrevive a la digitalización?",
        "glitch_conceptual": "¿El aura sobrevive cuando el color se vuelve píxel?"
    },
    {
        "numero": "112",
        "cluster": "III. Origen de la Escritura",
        "titulo": "Tablilla vs. papiro: la tecnología como episteme",
        "autor_primario": "Jack Goody",
        "obra_primaria": "The Logic of Writing and the Organization of Society",
        "año": 1986,
        "concepto_central": "materialidad del soporte",
        "keywords": ["tablilla arcilla", "papiro", "durabilidad", "tecnología soporte", "archivo histórico"],
        "autores_secundarios": ["Friedrich Kittler", "Marshall McLuhan"],
        "conexion_RH": "Almacenamiento en la nube: ¿archivo permanente o amnesia programada?",
        "glitch_conceptual": "Leemos los residuos, no la verdad"
    },
    {
        "numero": "115",
        "cluster": "IV. Semiótica, Interpretación, Crítica",
        "titulo": "Eiségesis: el error que somos",
        "autor_primario": "Hans-Georg Gadamer",
        "obra_primaria": "Verdad y método",
        "año": 1960,
        "concepto_central": "eiségesis vs. exégesis",
        "keywords": ["hermenéutica", "prejuicio", "proyección lectora", "círculo hermenéutico", "fusión de horizontes"],
        "autores_secundarios": ["Paul Ricoeur", "Umberto Eco"],
        "conexion_RH": "Personalización algorítmica: eiségesis como servicio",
        "glitch_conceptual": "¿No estamos institucionalizando la eiségesis como deseable?"
    },
    {
        "numero": "119",
        "cluster": "VI. Segunda Orden, Pedagogía, Aprendizaje",
        "titulo": "Leer en voz alta: erotizar la sintaxis",
        "autor_primario": "Severo Sarduy",
        "obra_primaria": "Escrito sobre un cuerpo",
        "año": 1969,
        "concepto_central": "lectura como performance corporal",
        "keywords": ["voz alta", "materialidad vocal", "erotismo textual", "performance bucal", "cuerpo-texto"],
        "autores_secundarios": ["Roland Barthes", "Paul Zumthor"],
        "conexion_RH": "Voces sintéticas: ¿dónde queda el cuerpo en la lectura automática?",
        "glitch_conceptual": "Leer poesía en silencio es amputar una capa de sentido"
    }
]

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT MEJORADO
# ═══════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_BIBLIOGRAFIA = """
Eres un investigador académico especializado en teoría crítica, filosofía continental, semiótica, historia del arte y pedagogía crítica del siglo XX-XXI.

Tu tarea es localizar y verificar fuentes bibliográficas rigurosas para investigación académica de alto nivel.

CRITERIOS DE CALIDAD:
1. Textos originales accesibles (PDFs de editoriales reconocidas, repositorios institucionales)
2. Análisis académicos recientes (2015-2026) que conecten teoría clásica con tecnología digital
3. Fuentes en español cuando sea posible (sin sacrificar calidad)
4. Diversidad de medios (libros, papers, conferencias académicas en video, tesis doctorales)
5. Priorizar fuentes con DOI o URL estable

DISTRIBUCIÓN OBLIGATORIA POR TSR:
- 40% teoría clásica (obras del autor primario + comentaristas canónicos)
- 30% teoría crítica relacionada (autores secundarios + diálogos conceptuales)
- 30% investigación contemporánea (papers 2020-2026 sobre IA/algoritmos/cultura digital)

VERIFICACIÓN:
- URL debe existir y ser accesible públicamente
- Evitar enlaces rotos, paywall sin alternativa, blogs sin respaldo institucional
- Si es video, debe ser académico (conferencias, clases universitarias, no divulgación superficial)

═══════════════════════════════════════════════════════════════════════════
⚠️ FORMATO DE RESPUESTA CRÍTICO ⚠️
═══════════════════════════════════════════════════════════════════════════

DEVUELVE **ÚNICAMENTE** EL OBJETO JSON. 

❌ NO INCLUYAS:
- Texto introductorio ("Aquí está la bibliografía...")
- Bloques de código Markdown (```json ... ```)
- Explicaciones posteriores
- Ningún texto antes o después del JSON

✅ RESPONDE EXACTAMENTE ASÍ:
{"tsr": "102", "titulo": "...", "cluster": "...", ...}

NADA MÁS. Solo el objeto JSON puro.
═══════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN: EXTRACCIÓN ROBUSTA DE JSON
# ═══════════════════════════════════════════════════════════════════════════

def extraer_json_de_respuesta(texto_raw):
    """
    Extrae JSON de respuestas que pueden incluir texto extra o Markdown.
    Maneja múltiples casos problemáticos.
    """
    # Caso 1: Respuesta es JSON puro (ideal)
    try:
        return json.loads(texto_raw)
    except json.JSONDecodeError:
        pass
    
    # Caso 2: JSON dentro de code block Markdown ```json ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', texto_raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Caso 3: Buscar primer { y último } válidos
    inicio = texto_raw.find('{')
    fin = texto_raw.rfind('}')
    if inicio != -1 and fin != -1 and inicio < fin:
        posible_json = texto_raw[inicio:fin+1]
        try:
            return json.loads(posible_json)
        except json.JSONDecodeError:
            pass
    
    # Caso 4: Limpiar comillas tipográficas Unicode
    texto_limpio = texto_raw.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'").replace('…', '...')
    try:
        return json.loads(texto_limpio)
    except json.JSONDecodeError:
        pass
    
    # Caso 5: Intentar extraer después de limpiar y buscar de nuevo
    if inicio != -1 and fin != -1:
        posible_json = texto_limpio[inicio:fin+1]
        try:
            return json.loads(posible_json)
        except json.JSONDecodeError:
            pass
    
    # Si nada funciona, devolver None
    return None

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN: VALIDACIÓN DE BIBLIOGRAFÍA
# ═══════════════════════════════════════════════════════════════════════════

def validar_bibliografia(bibliografia):
    """
    Valida estructura de bibliografía generada.
    Retorna (es_valido, lista_errores).
    """
    errores = []
    
    # Validar campos obligatorios
    campos_requeridos = ["tsr", "titulo", "cluster", "fuentes"]
    for campo in campos_requeridos:
        if campo not in bibliografia:
            errores.append(f"❌ Falta campo obligatorio: {campo}")
    
    # Validar número de fuentes
    if "fuentes" in bibliografia:
        num_fuentes = len(bibliografia["fuentes"])
        if num_fuentes < 10:
            errores.append(f"⚠️ Pocas fuentes: {num_fuentes} (mínimo recomendado 12)")
        elif num_fuentes > 15:
            errores.append(f"⚠️ Muchas fuentes: {num_fuentes} (máximo recomendado 14)")
        
        # Validar cada fuente
        for i, fuente in enumerate(bibliografia["fuentes"], 1):
            if "titulo" not in fuente or not fuente.get("titulo"):
                errores.append(f"⚠️ Fuente {i} sin título")
            if "autor" not in fuente or not fuente.get("autor"):
                errores.append(f"⚠️ Fuente {i} sin autor")
            if "url" not in fuente or not fuente.get("url"):
                errores.append(f"⚠️ Fuente {i} sin URL")
    else:
        errores.append("❌ No hay campo 'fuentes'")
    
    return len(errores) == 0, errores

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN: GENERADOR CON REINTENTOS
# ═══════════════════════════════════════════════════════════════════════════

def generar_bibliografia_tsr(tsr_data, max_intentos=3):
    """
    Genera bibliografía verificada para un TSR específico.
    Incluye sistema de reintentos automáticos y guardado de debug.
    """
    
    user_prompt = f"""
Busca y verifica 12-14 fuentes académicas para el TSR{tsr_data['numero']}.

METADATA DEL TSR:
- Título: {tsr_data['titulo']}
- Autor primario: {tsr_data['autor_primario']}
- Obra primaria: {tsr_data['obra_primaria']} ({tsr_data['año']})
- Concepto central: {tsr_data['concepto_central']}
- Keywords: {', '.join(tsr_data['keywords'])}
- Autores secundarios: {', '.join(tsr_data['autores_secundarios'])}
- Conexión Reflejos Híbridos: {tsr_data['conexion_RH']}
- Glitch conceptual: {tsr_data['glitch_conceptual']}

DISTRIBUCIÓN REQUERIDA (12-14 fuentes):

**BLOQUE 1: Teoría Clásica (5-6 fuentes)**
- Texto original del autor primario (PDF si existe)
- 2-3 comentaristas canónicos del autor primario
- 1-2 fuentes de autores secundarios mencionados

**BLOQUE 2: Teoría Crítica Relacionada (3-4 fuentes)**
- Textos que conecten el concepto central con otros marcos teóricos
- Diálogos conceptuales (ej: Foucault + Deleuze, Barthes + Eco)
- Críticas o ampliaciones del concepto original

**BLOQUE 3: Investigación Contemporánea (4 fuentes)**
- Papers 2020-2026 sobre: {tsr_data['conexion_RH']}
- Investigación sobre IA, algoritmos, cultura digital, NFT, deepfakes
- Conexiones explícitas entre teoría clásica y tecnología actual

FORMATO JSON (responde SOLO con este JSON):
{{
  "tsr": "{tsr_data['numero']}",
  "titulo": "{tsr_data['titulo']}",
  "cluster": "{tsr_data['cluster']}",
  "fecha_generacion": "{datetime.now().strftime('%Y-%m-%d')}",
  "fuentes": [
    {{
      "numero": 1,
      "bloque": "Teoría Clásica",
      "autor": "Apellido, Nombre",
      "titulo": "Título completo",
      "año": 2024,
      "tipo": "libro|paper|pdf|video|tesis",
      "editorial_revista": "Editorial o Revista Académica",
      "url": "URL completa verificada",
      "doi": "DOI si existe",
      "relevancia": "1-2 frases explicando qué aporta específicamente a TSR{tsr_data['numero']}"
    }}
  ],
  "cobertura_conceptual": {{
    "concepto_central": "% de fuentes que abordan concepto",
    "conexion_RH": "% de fuentes que conectan con RH",
    "glitch": "% de fuentes que problematizan glitch"
  }},
  "nota_metodologica": "Breve nota sobre criterios de selección"
}}

RESTRICCIONES:
- NO inventes URLs
- NO incluyas fuentes sin verificar accesibilidad
- Si no encuentras fuentes suficientes en BLOQUE 3, explícitalo en nota_metodologica
"""

    for intento in range(1, max_intentos + 1):
        try:
            if intento > 1:
                print(f"   🔄 Reintento {intento}/{max_intentos}...")
            
            # LLAMADA A LA API
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_BIBLIOGRAFIA},
                    {"role": "user", "content": user_prompt}
                ],
                model="sonar-pro",
                temperature=0.3,
                max_tokens=5000  # ← AUMENTADO DE 4000 A 5000
            )
            
            texto_raw = completion.choices[0].message.content
            
            # EXTRACCIÓN ROBUSTA
            bibliografia_json = extraer_json_de_respuesta(texto_raw)
            
            # Si no se pudo extraer JSON
            if bibliografia_json is None:
                if intento < max_intentos:
                    print(f"   ⚠️ JSON inválido, reintentando en 8 segundos...")
                    time.sleep(8)
                    continue
                else:
                    # Último intento fallido: guardar para debug
                    debug_filename = f"debug_TSR{tsr_data['numero']}_raw.txt"
                    with open(debug_filename, "w", encoding="utf-8") as f:
                        f.write(f"═══ TSR{tsr_data['numero']}: {tsr_data['titulo']} ═══\n\n")
                        f.write(f"Intentos: {max_intentos}\n")
                        f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
                        f.write("═══ RESPUESTA RAW ═══\n\n")
                        f.write(texto_raw)
                    
                    return {
                        "error": "No se pudo extraer JSON válido después de 3 intentos",
                        "tsr": tsr_data['numero'],
                        "titulo": tsr_data['titulo'],
                        "debug_file": debug_filename,
                        "longitud_respuesta": len(texto_raw)
                    }
            
            # VALIDACIÓN
            es_valido, errores_validacion = validar_bibliografia(bibliografia_json)
            
            if not es_valido:
                if intento < max_intentos:
                    print(f"   ⚠️ Bibliografía incompleta ({len(errores_validacion)} problemas), reintentando...")
                    time.sleep(8)
                    continue
                else:
                    # Último intento con errores: guardar con warnings
                    bibliografia_json["warnings"] = errores_validacion
                    print(f"   ⚠️ Completado con {len(errores_validacion)} advertencias")
            
            # ÉXITO: agregar metadata
            bibliografia_json["metadata_generacion"] = {
                "modelo": completion.model,
                "intentos_necesarios": intento,
                "tokens_entrada": completion.usage.prompt_tokens,
                "tokens_salida": completion.usage.completion_tokens,
                "temperatura": 0.3,
                "timestamp": datetime.now().isoformat()
            }
            
            return bibliografia_json
        
        except json.JSONDecodeError as e:
            if intento < max_intentos:
                print(f"   ⚠️ Error JSON: {str(e)[:60]}... Reintentando en 8s")
                time.sleep(8)
            else:
                return {
                    "error": f"JSONDecodeError persistente: {str(e)}",
                    "tsr": tsr_data['numero'],
                    "titulo": tsr_data['titulo']
                }
        
        except Exception as e:
            if intento < max_intentos:
                print(f"   ⚠️ Error: {str(e)[:60]}... Reintentando en 12s")
                time.sleep(12)
            else:
                return {
                    "error": f"Error después de {max_intentos} intentos: {str(e)}",
                    "tsr": tsr_data['numero'],
                    "titulo": tsr_data['titulo']
                }
    
    # Fallback (no debería llegar acá)
    return {
        "error": "Error desconocido después de todos los intentos",
        "tsr": tsr_data['numero'],
        "titulo": tsr_data['titulo']
    }

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL: REINTENTO DE TSRs FALLIDOS
# ═══════════════════════════════════════════════════════════════════════════

def reintentar_tsr_fallidos():
    """
    Reintenta generación de bibliografía para los 7 TSRs que fallaron.
    """
    
    print("═" * 80)
    print("🔬 REINTENTO: CAPA 1 - TSRs FALLIDOS")
    print("═" * 80)
    print(f"📊 TSRs a reintentar: {len(TSR_FALLIDOS)}")
    print(f"🎯 Objetivo: ~{len(TSR_FALLIDOS) * 12} fuentes")
    print("═" * 80)
    
    resultados = []
    exitosos = 0
    fallidos = 0
    
    for i, tsr in enumerate(TSR_FALLIDOS, 1):
        print(f"\n📚 [{i}/{len(TSR_FALLIDOS)}] TSR{tsr['numero']}: {tsr['titulo']}")
        print(f"   📖 {tsr['autor_primario']} - {tsr['obra_primaria']}")
        
        resultado = generar_bibliografia_tsr(tsr, max_intentos=3)
        
        if "error" in resultado:
            print(f"   ❌ FALLO: {resultado['error'][:80]}")
            fallidos += 1
        else:
            num_fuentes = len(resultado.get('fuentes', []))
            warnings = len(resultado.get('warnings', []))
            if warnings > 0:
                print(f"   ⚠️ {num_fuentes} fuentes ({warnings} advertencias)")
            else:
                print(f"   ✅ {num_fuentes} fuentes")
            exitosos += 1
        
        resultados.append(resultado)
        
        # DELAY entre requests (excepto el último)
        if i < len(TSR_FALLIDOS):
            delay = 6 if "error" not in resultado else 15
            print(f"   ⏳ Pausa de {delay}s antes del siguiente...")
            time.sleep(delay)
    
    # GUARDAR RESULTADOS
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"TSR_CAPA1_Reintentos_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "capa": "CAPA 1: Bibliografía Verificada (Reintentos)",
                "fecha_generacion": datetime.now().isoformat(),
                "total_tsr_reintentados": len(TSR_FALLIDOS),
                "exitosos": exitosos,
                "fallidos": fallidos,
                "tasa_exito": f"{(exitosos/len(TSR_FALLIDOS)*100):.1f}%",
                "total_fuentes_obtenidas": sum(len(r.get('fuentes', [])) for r in resultados if "error" not in r)
            },
            "resultados": resultados
        }, f, indent=2, ensure_ascii=False)
    
    print("\n" + "═" * 80)
    print("🎉 REINTENTOS COMPLETADOS")
    print(f"📁 Archivo: {filename}")
    print(f"✅ Exitosos: {exitosos}/{len(TSR_FALLIDOS)}")
    print(f"❌ Fallidos: {fallidos}/{len(TSR_FALLIDOS)}")
    print(f"📊 Tasa de éxito: {(exitosos/len(TSR_FALLIDOS)*100):.1f}%")
    
    if fallidos > 0:
        print("\n⚠️ TSRs que siguen fallando:")
        for r in resultados:
            if "error" in r:
                print(f"   - TSR{r['tsr']}: {r.get('titulo', 'N/A')}")
                if "debug_file" in r:
                    print(f"     Debug guardado en: {r['debug_file']}")
    
    print("═" * 80)
    
    return resultados

# ═══════════════════════════════════════════════════════════════════════════
# EJECUCIÓN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    resultados = reintentar_tsr_fallidos()
