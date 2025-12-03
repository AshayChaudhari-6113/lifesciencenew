import streamlit as st
import os
import json
from dotenv import load_dotenv
from src.arxiv_fetcher import ArxivLoader
from src.pubmed_fetcher import PubMedLoader
from src.insight_generator import generate_paper_insight, generate_comparison_insight
from src.llm_client import get_llm_response

# --- Configuration ---
load_dotenv()

# Load specific model names from env or defaults
MODEL_FAST = os.getenv("MODEL_FAST", "azure_ai/genailab-maas-Llama-3.3-70B-Instruct")
MODEL_REASONING = os.getenv("MODEL_REASONING", "azure/genailab-maas-gpt-4o")

# --- Helper Functions ---
def refine_search_query(user_input):
    """Uses the Llama 3.3 model to refine the search query"""
    try:
        messages = [
            {"role": "system", "content": "You are a Scientific Search Optimizer. Convert the user's natural language request into a precise, keyword-based search query. Return ONLY the keywords. Do not add quotes or prefixes."},
            {"role": "user", "content": user_input}
        ]
        # Using the Fast model (Llama) for this
        response = get_llm_response(messages, MODEL_FAST, temperature=0.1)
        return response.strip() if response else user_input
    except Exception:
        return user_input

# --- Session State Initialization ---
if "found_papers" not in st.session_state:
    st.session_state.found_papers = []
if "selected_papers" not in st.session_state:
    st.session_state.selected_papers = []
if "chat_context" not in st.session_state:
    st.session_state.chat_context = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "paper_insights" not in st.session_state:
    st.session_state.paper_insights = {} 
if "comparison_insight" not in st.session_state:
    st.session_state.comparison_insight = None

# --- UI Layout ---
st.set_page_config(page_title="Life Sciences Agent", page_icon="🧬", layout="wide")

st.title("🧬 Life Sciences Research Agent (Secure Env)")
st.markdown("Search, Analyze, and Compare Research Papers using Internal GenAI APIs.")

# --- Sidebar: Search ---
with st.sidebar:
    st.header("🔎 Search Papers")
    query = st.text_input("Enter topic (e.g., 'COVID-19 vaccines')")
    if st.button("Search"):
        with st.spinner("Refining query & Searching..."):
            refined_query = refine_search_query(query)
            st.write(f"**Keywords:** {refined_query}")
            
            # Initialize Loaders
            arxiv_loader = ArxivLoader()
            pubmed_loader = PubMedLoader()
            
            # Fetch Papers
            arxiv_papers = arxiv_loader.fetch_papers(refined_query, limit=3)
            pubmed_papers = pubmed_loader.fetch_papers(refined_query, limit=3)
            
            st.session_state.found_papers = arxiv_papers + pubmed_papers
            st.session_state.selected_papers = []
            st.session_state.chat_context = ""
            st.session_state.messages = []
            st.session_state.paper_insights = {}
            st.session_state.comparison_insight = None

# --- Main Area ---

# 1. Search Results & Selection
if st.session_state.found_papers:
    st.subheader(f"📄 Found {len(st.session_state.found_papers)} Papers")
    
    with st.form("selection_form"):
        selected_indices = []
        for i, paper in enumerate(st.session_state.found_papers):
            source_icon = "🅰️" if paper['source'] == 'arxiv' else "Pw"
            label = f"[{source_icon}] {paper['title']} ({paper['published']})"
            if st.checkbox(label, key=f"paper_{i}"):
                selected_indices.append(i)
        
        submitted = st.form_submit_button("✅ Analyze Selected Papers")
        
        if submitted:
            if len(selected_indices) > 3:
                st.error("Please select max 3 papers.")
            elif len(selected_indices) == 0:
                st.error("Please select at least one paper.")
            else:
                st.session_state.selected_papers = [st.session_state.found_papers[i] for i in selected_indices]
                st.session_state.paper_insights = {}
                st.session_state.comparison_insight = None
                st.session_state.chat_context = ""
                st.rerun()

# 2. Analysis & Comparison Logic
if st.session_state.selected_papers and not st.session_state.chat_context:
    with st.spinner("Analyzing papers using GenAI Lab Models..."):
        combined_context = ""
        
        # Individual Analysis
        for paper in st.session_state.selected_papers:
            if paper['id'] not in st.session_state.paper_insights:
                text_content = f"Title: {paper['title']}\nAbstract: {paper['summary']}"
                insight = generate_paper_insight(text_content)
                st.session_state.paper_insights[paper['id']] = insight
                combined_context += f"\n\n=== PAPER: {paper['title']} ===\n{text_content}\nAnalysis: {insight.model_dump_json()}"

        # Comparative Analysis
        if len(st.session_state.selected_papers) > 1:
            comparison = generate_comparison_insight(combined_context)
            st.session_state.comparison_insight = comparison
            st.session_state.chat_context = f"Comparative Analysis:\n{comparison.model_dump_json()}\n\nPapers Data:\n{combined_context}"
        else:
            st.session_state.chat_context = combined_context

# 3. Display Analysis
if st.session_state.selected_papers and st.session_state.paper_insights:
    st.divider()
    st.subheader("🧠 Analysis & Comparison")
    
    cols = st.columns(len(st.session_state.selected_papers))
    for idx, paper in enumerate(st.session_state.selected_papers):
        insight = st.session_state.paper_insights.get(paper['id'])
        if insight:
            with cols[idx]:
                st.markdown(f"### {paper['title']}")
                
                # Score Badge
                score_color = "green" if insight.methodology_score >= 8 else "orange" if insight.methodology_score >= 5 else "red"
                st.markdown(f"**Rigor Score:** :{score_color}[{insight.methodology_score}/10]")
                
                with st.expander("See Details", expanded=True):
                    st.markdown(f"**Background:** {insight.background}")
                    st.markdown(f"**Methods:** {insight.methods}")
                    st.caption(f"*Critique: {insight.methodology_critique}*")
                    st.markdown(f"**Results:** {insight.results}")
                    
                    st.markdown("**Key Findings:**")
                    for kf in insight.key_findings:
                        st.markdown(f"- {kf}")
                        
                    st.markdown(f"**Conclusions:** {insight.conclusions}")
                    
                    json_str = insight.model_dump_json(indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"insight_{paper['id']}.json",
                        mime="application/json",
                        key=f"dl_{idx}"
                    )

    # Display Comparison
    if st.session_state.comparison_insight:
        st.markdown("### ⚖️ Comparative Synthesis")
        comparison = st.session_state.comparison_insight
        
        st.info(f"**Hypothesis:** {comparison.hypothesis}")
        st.markdown(f"**Methodology:**\n{comparison.methodology}")
        st.markdown(f"**Data Comparison:**\n{comparison.tabular_data}")
        st.success(f"**Conclusion:** {comparison.conclusion}")
        
        comp_json = comparison.model_dump_json(indent=2)
        st.download_button(
            label="📥 Download Comparison JSON",
            data=comp_json,
            file_name="comparison_insight.json",
            mime="application/json",
            key="dl_comp"
        )

# 4. Chat Interface
if st.session_state.chat_context:
    st.divider()
    st.subheader("💬 Chat with Papers")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about these papers..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Construct messages for RAG Chat
            rag_messages = [
                {"role": "system", "content": "You are a research assistant. Answer the user's question based ONLY on the provided context."},
                {"role": "user", "content": f"Context:\n{st.session_state.chat_context[:30000]}\n\nUser Question: {prompt}"}
            ]
            
            # Use Reasoning Model (GPT-4o) for best chat answers
            response_text = get_llm_response(rag_messages, MODEL_REASONING)
            
            if response_text:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error("Failed to get response from API.")