import os
import requests
import json
import urllib3
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
# Matches: BASE_URL = "https://genailab.tcs.in"
BASE_URL = os.getenv("GENAI_LAB_BASE_URL")
API_KEY = os.getenv("GENAI_LAB_API_KEY")

# --- Disable SSL warnings (Critical for your environment) ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_llm_response(messages, model_name, temperature=0.2, max_tokens=4096, json_mode=False):
    """
    Calls the GenAI Lab API using the OpenAI-compatible standard.
    """
    # Construct standard OpenAI URL: https://genailab.tcs.in/v1/chat/completions
    # This avoids the "Deployment not found" errors by letting the gateway route based on the model name.
    url = f"{BASE_URL}/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}" # Standard Bearer token
    }

    # Payload: We pass the FULL model name here (e.g., "azure_ai/genailab-maas-DeepSeek-V3-0324")
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False  # ⚠️ Bypass SSL as per your requirement
        )
        
        if response.status_code == 404:
            print(f"❌ 404 Error: Endpoint not found.")
            print(f"   Debug URL: {url}")
            return None
            
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error: {e}")
        if response is not None:
             print(f"   Response Body: {response.text}")
        return None