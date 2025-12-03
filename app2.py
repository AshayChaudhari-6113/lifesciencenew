import chainlit as cl
import google.generativeai as genai
import os
import json
from groq import Groq
from src.arxiv_fetcher import ArxivLoader
from src.pubmed_fetcher import PubMedLoader
from src.insight_generator import generate_paper_insight, generate_comparison_insight

# --- Configuration ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Helper Functions ---
def refine_search_query(user_input):
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Scientific Search Optimizer. Convert the user's natural language request into a precise, keyword-based search query. Return ONLY the keywords."},
                {"role": "user", "content": user_input}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return user_input

# --- Chainlit Session Management ---

@cl.on_chat_start
async def start():
    cl.user_session.set("arxiv_loader", ArxivLoader())
    cl.user_session.set("pubmed_loader", PubMedLoader())
    cl.user_session.set("found_papers", [])
    cl.user_session.set("selected_papers", [])
    cl.user_session.set("mode", "search") # Modes: search, select, chat

    await cl.Message("🧬 **Life Sciences Research Agent**\n\nI can help you find, analyze, and compare research papers from Arxiv and PubMed.\n\n**Please enter a search topic to begin.**").send()

@cl.on_message
async def main(message: cl.Message):
    mode = cl.user_session.get("mode")
    
    if mode == "search":
        await handle_search(message.content)
    elif mode == "chat":
        await handle_chat(message.content)
    else:
        # Fallback or specific selection handling if done via text
        pass

async def handle_search(query):
    refined_query = refine_search_query(query)
    msg = cl.Message(content=f"🔎 Searching Arxiv & PubMed for: **'{refined_query}'**...")
    await msg.send()

    arxiv_loader = cl.user_session.get("arxiv_loader")
    pubmed_loader = cl.user_session.get("pubmed_loader")

    # Fetch from both sources
    arxiv_papers = arxiv_loader.fetch_papers(refined_query, limit=3)
    pubmed_papers = pubmed_loader.fetch_papers(refined_query, limit=3)
    
    all_papers = arxiv_papers + pubmed_papers
    cl.user_session.set("found_papers", all_papers)

    if not all_papers:
        await cl.Message(f"❌ No papers found for '{refined_query}'. Try a different topic.").send()
        return

    # Display results with actions for selection
    actions = []
    results_text = "### 📄 Found Papers:\n"
    
    for i, paper in enumerate(all_papers):
        source_icon = "🅰️" if paper['source'] == 'arxiv' else "Pw"
        results_text += f"**{i+1}. [{source_icon}] {paper['title']}**\n*Published: {paper['published']}*\n\n"
        actions.append(cl.Action(name="select_paper", value=str(i), label=f"Select #{i+1}"))

    results_text += "\n👇 **Click buttons below to select papers for analysis (Max 3).**"
    
    await cl.Message(content=results_text, actions=actions).send()
    
    # Add a "Done" button
    await cl.Message(content="When you are finished selecting, click **Analyze Selected**.", actions=[
        cl.Action(name="analyze_papers", value="done", label="✅ Analyze Selected")
    ]).send()

@cl.action_callback("select_paper")
async def on_select_paper(action: cl.Action):
    index = int(action.value)
    found_papers = cl.user_session.get("found_papers")
    selected_papers = cl.user_session.get("selected_papers")
    
    paper = found_papers[index]
    
    # Check if already selected
    if any(p['id'] == paper['id'] for p in selected_papers):
        await cl.Message(content=f"⚠️ '{paper['title']}' is already selected.").send()
        return

    if len(selected_papers) >= 3:
        await cl.Message(content=f"⚠️ You can only select up to 3 papers.").send()
        return

    selected_papers.append(paper)
    cl.user_session.set("selected_papers", selected_papers)
    await cl.Message(content=f"✅ Added: **{paper['title']}**").send()

@cl.action_callback("analyze_papers")
async def on_analyze_papers(action: cl.Action):
    selected_papers = cl.user_session.get("selected_papers")
    
    if not selected_papers:
        await cl.Message(content="⚠️ Please select at least one paper first.").send()
        return

    cl.user_session.set("mode", "chat") # Switch to chat mode
    
    await cl.Message(content=f"🧠 Analyzing {len(selected_papers)} papers... This may take a moment.").send()
    
    combined_context = ""
    
    # Generate individual insights
    for paper in selected_papers:
        msg = cl.Message(content=f"📖 Reading **{paper['title']}**...")
        await msg.send()
        
        # Use summary as text for now (Full text fetching is complex and varies by source)
        # In a real full implementation, we would try to download PDF/HTML here.
        text_content = f"Title: {paper['title']}\nAbstract: {paper['summary']}"
        
        insight = generate_paper_insight(text_content)
        
        # Store insight in paper dict for reference
        paper['insight'] = insight
        
        display_text = f"""
        ### 📄 Analysis: {paper['title']}
        **Background:** {insight.background}
        **Methods:** {insight.methods}
        **Results:** {insight.results}
        **Conclusions:** {insight.conclusions}
        """
        await cl.Message(content=display_text).send()
        
        combined_context += f"\n\n=== PAPER: {paper['title']} ===\n{text_content}\nAnalysis: {insight.model_dump_json()}"

    # Generate Comparison if > 1 paper
    if len(selected_papers) > 1:
        await cl.Message(content="⚖️ Generating Comparative Analysis...").send()
        comparison = generate_comparison_insight(combined_context)
        
        comp_text = f"""
        ## 📊 Comparative Analysis
        
        **Hypothesis:** {comparison.hypothesis}
        
        **Methodology Comparison:**
        {comparison.methodology}
        
        **Data Comparison:**
        {comparison.tabular_data}
        
        **Conclusion:**
        {comparison.conclusion}
        """
        await cl.Message(content=comp_text).send()
        
        # Save context for chat
        cl.user_session.set("chat_context", f"Comparative Analysis:\n{comparison.model_dump_json()}\n\nPapers Data:\n{combined_context}")
    else:
         cl.user_session.set("chat_context", combined_context)

    await cl.Message(content="**✅ Analysis Complete.**\nYou can now ask questions about these papers or ask for further comparisons.").send()

async def handle_chat(user_input):
    context = cl.user_session.get("chat_context")
    
    if not context:
        await cl.Message(content="⚠️ No papers loaded. Please search and select papers first.").send()
        return

    # Simple RAG / Chat
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are a research assistant. Answer the user's question based ONLY on the provided context.
    
    Context:
    {context[:40000]}
    
    User Question: {user_input}
    """
    
    msg = cl.Message(content="")
    await msg.send()
    
    response = model.generate_content(prompt, stream=True)
    for chunk in response:
        if chunk.text:
            await msg.stream_token(chunk.text)
    
    await msg.update()