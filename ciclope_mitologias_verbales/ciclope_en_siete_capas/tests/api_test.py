from perplexity import Perplexity
import os

# El SDK automáticamente lee PERPLEXITY_API_KEY
client = Perplexity()

# Prueba 1: Search API (simple búsqueda)
print("=== TEST 1: Search API ===")
search = client.search.create(
    query="teoría crítica Foucault 2025",
    max_results=5
)

print(f"Búsqueda ejecutada exitosamente")
print(f"Resultados encontrados: {len(search.results)}")
for i, result in enumerate(search.results[:3], 1):
    print(f"\n{i}. {result.title}")
    print(f"   URL: {result.url}")
    print(f"   Snippet: {result.snippet[:150]}...")

# Prueba 2: Chat/Grounded LLM (con síntesis de IA)
print("\n\n=== TEST 2: Grounded LLM (Sonar) ===")
chat = client.chat.completions.create(
    model="sonar",
    messages=[
        {
            "role": "user",
            "content": "¿Cuáles son los últimos avances en IA 2025?"
        }
    ]
)

print(f"Respuesta generada:")
print(chat.choices[0].message.content[:300])
print("\nEstadísticas de uso:")
print(f"Tokens entrada: {chat.usage.prompt_tokens}")
print(f"Tokens salida: {chat.usage.completion_tokens}")
