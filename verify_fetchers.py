from src.arxiv_fetcher import ArxivLoader
from src.pubmed_fetcher import PubMedLoader

def test_arxiv():
    print("Testing Arxiv Fetcher...")
    loader = ArxivLoader()
    results = loader.fetch_papers("LLM Agents", limit=1)
    if results:
        print(f"[SUCCESS] Arxiv: Found {len(results)} papers.")
        print(f"   Title: {results[0]['title']}")
    else:
        print("[FAILED] Arxiv: No papers found.")

def test_pubmed():
    print("\nTesting PubMed Fetcher...")
    loader = PubMedLoader()
    results = loader.fetch_papers("COVID-19", limit=1)
    if results:
        print(f"[SUCCESS] PubMed: Found {len(results)} papers.")
        print(f"   Title: {results[0]['title']}")
    else:
        print("[FAILED] PubMed: No papers found.")

if __name__ == "__main__":
    try:
        test_arxiv()
    except Exception as e:
        print(f"[ERROR] Arxiv Exception: {e}")

    try:
        test_pubmed()
    except Exception as e:
        print(f"[ERROR] PubMed Exception: {e}")
