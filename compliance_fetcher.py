import os
import requests
import json
from Bio import Entrez

import urllib3
# Disable annoying warnings when we turn off SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ⚠️ IMPORTANT: You MUST replace this with your actual email or NCBI might block you.
Entrez.email = "your.email@example.com" 

class NCBILoader:
    def __init__(self, data_dir="./data"):
        self.json_dir = os.path.join(data_dir, "json")
        self.pdf_dir = os.path.join(data_dir, "pdfs")
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)

    def fetch_papers(self, query, limit=1):
        """Finds papers and fetches BOTH BioC JSON (Text) and PDF (Images)"""
        print(f"🔍 Searching PMC for: {query}")
        
        try:
            # 1. Search for Open Access papers in PMC
            handle = Entrez.esearch(db="pmc", term=f"{query} AND open access[filter]", sort='relevance', retmax=limit)
            search_results = Entrez.read(handle)
            pmc_ids = search_results["IdList"]
            
            if not pmc_ids:
                print("   ❌ No IDs found matching query.")
                return []
                
            print(f"   found IDs: {pmc_ids}")
        except Exception as e:
            print(f"   ❌ Entrez Search Error: {e}")
            return []
        
        results = []
        for pid in pmc_ids:
            # 2. Get Text (BioC API)
            text_data_path = self._get_bioc_json(pid)
            
            # 3. Get PDF URL (OA Service)
            pdf_path = self._download_pdf(pid)
            
            # We strictly need TEXT. PDF is optional (if missing, we just skip vision).
            if text_data_path:
                results.append({
                    "id": pid, 
                    "json": text_data_path, 
                    "pdf": pdf_path # might be None if PDF download fails
                })
            else:
                print(f"   ⚠️ Skipping {pid} (No text data available)")
                
        return results

    def _get_bioc_json(self, pmc_id):
        # --- THE FIX IS HERE ---
        # The BioC API requires the 'PMC' prefix (e.g., PMC8531986)
        # Entrez returns just the number (e.g., 8531986). We must add it.
        clean_id = str(pmc_id).strip()
        formatted_id = f"PMC{clean_id}" if not clean_id.startswith("PMC") else clean_id
        
        url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{formatted_id}/unicode"
        
        try:
            r = requests.get(url)
            
            # Check if request was successful
            if r.status_code == 200:
                try:
                    data = r.json() # This triggers the error if response is not JSON
                    save_path = os.path.join(self.json_dir, f"{formatted_id}.json")
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                    return save_path
                except json.JSONDecodeError:
                    print(f"   ❌ Error: BioC API returned invalid JSON for {formatted_id}. Response: {r.text[:50]}...")
            else:
                print(f"   ⚠️ BioC API failed for {formatted_id} (Status: {r.status_code})")
        
        except Exception as e:
            print(f"   ❌ Network Error fetching JSON {pmc_id}: {e}")
        
        return None

    def _download_pdf(self, pmc_id):
        # Format ID correctly for OA API as well
        clean_id = str(pmc_id).strip()
        formatted_id = f"PMC{clean_id}" if not clean_id.startswith("PMC") else clean_id
        
        oa_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
        try:
            r = requests.get(oa_url, params={"id": formatted_id})
            
            if "format=\"pdf\"" in r.text:
                start = r.text.find('href="', r.text.find('format="pdf"')) + 6
                end = r.text.find('"', start)
                link = r.text[start:end].replace("ftp://", "https://")
                
                # Download
                print(f"   📄 Downloading PDF from: {link}")
                pdf_r = requests.get(link)
                save_path = os.path.join(self.pdf_dir, f"{formatted_id}.pdf")
                with open(save_path, "wb") as f:
                    f.write(pdf_r.content)
                return save_path
        except Exception as e:
            print(f"   ⚠️ PDF Download failed for {pmc_id}: {e}")
            pass
        return None