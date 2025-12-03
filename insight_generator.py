import os
import json
import re
from pydantic import BaseModel, Field, ValidationError
from typing import List
from src.llm_client import get_llm_response

# Get Model ID from env
MODEL_NAME = os.getenv("MODEL_REASONING", "azure/genailab-maas-gpt-4o")

# Define Structured Output Models
class PaperInsight(BaseModel):
    background: str = Field(description="Background and context of the study")
    methods: str = Field(description="Methodology used in the study")
    results: str = Field(description="Key results and findings")
    conclusions: str = Field(description="Conclusions drawn by the authors")
    key_findings: List[str] = Field(description="3-5 bullet points of the most critical findings")
    methodology_score: int = Field(description="Rating 1-10 of methodology rigor")
    methodology_critique: str = Field(description="Brief explanation of the score")

class ComparisonInsight(BaseModel):
    title: str = Field(description="Title for the comparison")
    hypothesis: str = Field(description="Common hypothesis or theme")
    methodology: str = Field(description="Comparison of methodologies")
    tabular_data: str = Field(description="Markdown table comparing quantitative data")
    conclusion: str = Field(description="Synthesis conclusion")
    key_findings: List[str] = Field(description="List of key comparative findings")

def clean_json_string(text_response):
    """Helper to strip ```json markdown blocks from LLM response"""
    if not text_response:
        return "{}"
    # Remove markdown code blocks
    cleaned = re.sub(r"```json\s*", "", text_response)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()

def generate_paper_insight(text: str) -> PaperInsight:
    """Generates structured insight for a single paper using Internal API."""
    
    # We construct a prompt that explicitly asks for JSON matching the schema
    schema_desc = PaperInsight.model_json_schema()
    
    system_prompt = f"""
    You are a scientific analyst. Analyze the provided text.
    You MUST return the output as a valid JSON object matching this schema exactly:
    {json.dumps(schema_desc)}
    
    Do not add any markdown formatting or explanation text outside the JSON.
    """

    user_prompt = f"Text to analyze:\n{text[:25000]}" # Truncate to be safe

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response_text = get_llm_response(messages, MODEL_NAME, json_mode=True)
        cleaned_json = clean_json_string(response_text)
        return PaperInsight.model_validate_json(cleaned_json)
    except (ValidationError, json.JSONDecodeError, Exception) as e:
        print(f"Error generating paper insight: {e}")
        return PaperInsight(
            background="Error parsing model response", 
            methods="Error", 
            results="Error", 
            conclusions="Error",
            key_findings=[f"Raw Error: {str(e)}"], 
            methodology_score=0, 
            methodology_critique="Failed to generate valid JSON."
        )

def generate_comparison_insight(papers_text: str) -> ComparisonInsight:
    """Generates comparative insight for multiple papers."""
    
    schema_desc = ComparisonInsight.model_json_schema()
    
    system_prompt = f"""
    Compare the provided scientific papers.
    You MUST return the output as a valid JSON object matching this schema exactly:
    {json.dumps(schema_desc)}
    
    For 'tabular_data', return a string formatted as a Markdown table.
    """

    user_prompt = f"Papers Content:\n{papers_text[:40000]}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response_text = get_llm_response(messages, MODEL_NAME, json_mode=True)
        cleaned_json = clean_json_string(response_text)
        return ComparisonInsight.model_validate_json(cleaned_json)
    except Exception as e:
        print(f"Error generating comparison insight: {e}")
        return ComparisonInsight(
            title="Error", 
            hypothesis="Error", 
            methodology="Error", 
            tabular_data="Error", 
            conclusion="Error", 
            key_findings=["Failed to generate comparison."]
        )