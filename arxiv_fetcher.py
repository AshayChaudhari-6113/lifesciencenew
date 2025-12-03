import requests
import xml.etree.ElementTree as ET
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ArxivLoader:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"

    def fetch_papers(self, query, limit=3):
        print(f"[SEARCH] Searching Arxiv for: {query}")
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        try:
            # verify=False is REQUIRED for your network
            response = requests.get(self.base_url, params=params, verify=False)
            response.raise_for_status()
            return self._parse_xml_response(response.content)
        except Exception as e:
            print(f"[ERROR] Arxiv Search Error: {e}")
            return []

    def _parse_xml_response(self, xml_content):
        # ... (Same XML parsing logic as before) ...
        results = []
        try:
            root = ET.fromstring(xml_content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                id_url = entry.find('atom:id', ns).text
                paper_id = id_url.split('/')[-1].split('v')[0]
                title = entry.find('atom:title', ns).text.replace('\n', ' ').strip()
                summary = entry.find('atom:summary', ns).text.replace('\n', ' ').strip()
                published = entry.find('atom:published', ns).text[:10]
                results.append({
                    "id": paper_id, "title": title, "summary": summary, 
                    "pdf_url": None, "published": published, "source": "arxiv"
                })
        except: pass
        return results