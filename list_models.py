import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=api_key)
    print(f"[INFO] Found API Key: {api_key[:5]}...{api_key[-5:]}")
    
    print("\nListing available models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"[ERROR] Error listing models: {e}")
