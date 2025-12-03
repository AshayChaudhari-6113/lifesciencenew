from llama_index.llms.azure_openai import AzureOpenAI
# ... imports ...
import os
def generate_structured_insight(full_text, vision_data):
    # Configure Azure Client
    llm = AzureOpenAI(
        model="genailab-maas-Llama-3.3-70B-Instruct",
        deployment_name="genailab-maas-Llama-3.3-70B-Instruct",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint="https://genailab.tcs.in/v1/openai/deployments/azure_ai", # CHECK THIS
        api_version="2024-02-15-preview"
    )

    # ... rest of the code ...