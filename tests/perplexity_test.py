from perplexity import Perplexity

client = Perplexity()

search = client.search.create(
    query="latest AI developments 2024",
    max_results=5,
    max_tokens_per_page=2048
)

for result in search.results:
    print(f"{result.title}: {result.url}")
