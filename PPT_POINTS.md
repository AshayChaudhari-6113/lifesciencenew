# Life Sciences Research Agent - Presentation Highlights

## Slide 1: Title Slide
*   **Project Name**: Life Sciences Research Agent
*   **Subtitle**: Accelerating Scientific Discovery with Agentic AI
*   **Key Tech**: Google Gemini, Groq, Streamlit, Arxiv/PubMed APIs

## Slide 2: The Problem
*   **Information Overload**: Millions of new papers published annually.
*   **Fragmentation**: Data scattered across different repositories (Arxiv, PubMed).
*   **Time-Consuming**: Manual reading and synthesis of abstracts takes hours.
*   **Goal**: Create a unified tool to find, read, and synthesize papers in seconds.

## Slide 3: The Solution
*   **Unified Search**: Single interface for Arxiv (CS/Physics/Bio) and PubMed (Biomedical).
*   **Intelligent Querying**: Uses Llama-3 (Groq) to translate "vague ideas" into "precise keywords".
*   **Automated Analysis**: Uses Google Gemini to extract:
    *   Background & Context
    *   Methodology Rigor (Score 1-10)
    *   Key Results & Conclusions
*   **Comparative Synthesis**: Automatically compares multiple papers side-by-side.

## Slide 4: System Architecture
*   **Frontend**: Streamlit (Python-based interactive UI).
*   **Orchestration**: Custom Python backend.
*   **LLM Layer**:
    *   **Reasoning**: Google Gemini Flash (High speed, large context).
    *   **Optimization**: Groq (Low latency query refinement).
*   **Data Layer**: Live API connections to Arxiv and PubMed (No stale data).

## Slide 5: Key Features Demo
*   **Smart Search**: "Tell me about malaria vaccines" -> Auto-converts to "R21/Matrix-M malaria vaccine efficacy".
*   **Rigor Scoring**: AI evaluates the methodology quality (1-10 scale).
*   **Chat with Data**: Ask specific questions like "What was the sample size?" across all selected papers.
*   **Export**: Download structured JSON for further analysis.

## Slide 6: Future Roadmap
*   **Full-Text Analysis**: Integration with PDF parsing for deeper insights.
*   **Graph RAG**: Visualizing citation networks using Neo4j.
*   **Multi-Modal**: Analyzing figures and charts from papers.
*   **Personalization**: Saving user preferences and history.

## Slide 7: Conclusion
*   **Impact**: Reduces literature review time from hours to minutes.
*   **Accuracy**: Grounded in real-time scientific data.
*   **Accessibility**: Makes complex research accessible via simple chat interface.
