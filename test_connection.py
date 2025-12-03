import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# CONFIGURATION (Adjust these based on your internal documentation)
# The error URL suggested: https://genailab.tcs.in/v1/openai/deployments/azure_ai/genailab-maas-Llama-3.3-70B-Instruct/chat/completions
# This implies:
# Base: https://genailab.tcs.in/v1/openai/deployments/azure_ai
# Deployment: genailab-maas-Llama-3.3-70B-Instruct

client = AzureOpenAI(
    azure_endpoint="https://genailab.tcs.in/v1/openai/deployments/azure_ai", 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"), # Make sure this is in your .env
    api_version="2024-02-15-preview", # Update to a newer version! 2023 is too old for Llama 3
    azure_deployment="genailab-maas-Llama-3.3-70B-Instruct" # Double check this name
)

try:
    print("Testing connection...")
    response = client.chat.completions.create(
        model="genailab-maas-Llama-3.3-70B-Instruct", # Some wrappers need model name repeated here
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, are you working?"}
        ]
    )
    print("✅ Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ Error: {e}")