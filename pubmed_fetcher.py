import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PubMedLoader:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def fetch_papers(self, query, limit=3):
        print(f"[SEARCH] Searching PubMed for: {query}")
        try:
            # Search
            search_url = f"{self.base_url}/esearch.fcgi"
            search_params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": limit}
            resp = requests.get(search_url, params=search_params, verify=False) # verify=False
            
            id_list = resp.json().get('esearchresult', {}).get('idlist', [])
            if not id_list: return []

            # Summary
            summary_url = f"{self.base_url}/esummary.fcgi"
            summary_params = {"db": "pubmed", "id": ",".join(id_list), "retmode": "json"}
            resp = requests.get(summary_url, params=summary_params, verify=False) # verify=False
            
            papers = []
            for pmid, details in resp.json().get('result', {}).items():
                if pmid == 'uids': continue
                papers.append({
                    "id": pmid,
                    "title": details.get('title', 'No Title'),
                    "summary": details.get('title', 'No Abstract'), # Simple fallback
                    "pdf_url": None,
                    "published": details.get('pubdate', 'Unknown'),
                    "source": "pubmed"
                })
            return papers
        except Exception as e:
            print(f"[ERROR] PubMed Search Error: {e}")
            return []