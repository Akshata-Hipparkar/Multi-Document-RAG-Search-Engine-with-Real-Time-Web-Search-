import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# LangChain & Tools
from langchain_community.document_loaders import (PyPDFLoader, TextLoader, WikipediaLoader)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (RunnableParallel, RunnablePassthrough, RunnableLambda)
from langchain_core.output_parsers import StrOutputParser

# Environment Setup
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") # Ensure this is in your .env
st.set_page_config(page_title="GA02: Multi-Source RAG", layout="wide")

# --- CUSTOM CSS (Cinematic Enhancements) ---
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at center, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    .results-box { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 30px; margin-top: 20px; }
    .chip { display: inline-block; background: rgba(229, 9, 20, 0.1); color: #E50914; border: 1px solid #E50914; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: 700; margin: 5px; }
    .web-chip { background: rgba(0, 150, 255, 0.1); color: #0096FF; border: 1px solid #0096FF; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.05); border-radius: 4px; color: white; }
</style>
""", unsafe_allow_html=True)

# --- CORE LOGIC ---

def get_query_type(llm, query):
    """Part III.7: Query Classification Logic"""
    router_prompt = ChatPromptTemplate.from_template(
        "Classify this query into one of three categories: 'DOC', 'WEB', or 'HYBRID'.\n"
        "DOC: Internal knowledge, technical specs from documents.\n"
        "WEB: Real-time news, current events, recent stats.\n"
        "HYBRID: Comparing internal info with external trends.\n"
        "Query: {query}\nCategory:"
    )
    chain = router_prompt | llm | StrOutputParser()
    return chain.invoke({"query": query}).strip().upper()

def format_docs(docs):
    return "\n\n".join([f"Source [{d.metadata.get('source', 'Unknown')}]: {d.page_content}" for d in docs])

def perform_tavily_search(query):
    """Part III.8: Tavily Integration"""
    tavily = TavilySearchResults(k=3)
    results = tavily.invoke(query)
    formatted = []
    for r in results:
        formatted.append({
            "content": r["content"],
            "source": r["url"],
            "title": "Web Search Result"
        })
    return formatted

# --- APP LAYOUT ---
st.markdown('<h1 style="text-align:center;">RAG Search Engine</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#E50914; letter-spacing:3px;">DOCUMENTS + REAL-TIME WEB</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    use_web = st.toggle("Enable Tavily Web Search", value=True)
    uploaded_files = st.file_uploader("Upload Knowledge Base", type=["pdf", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        st.info(f"Library: {len(uploaded_files)} files indexed.")

# Main Interaction
query = st.text_input("", placeholder="Ask about your documents or current events...")
run_button = st.button("EXECUTE HYBRID SEARCH")

if run_button and query:
    if not uploaded_files and not use_web:
        st.warning("Please upload documents or enable Web Search.")
    else:
        with st.spinner("Analyzing across dimensions..."):
            # Initialize Models
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # 1. Routing
            q_type = get_query_type(llm, query)
            
            # 2. Retrieval
            context_docs = []
            web_context = ""
            
            # Document Retrieval
            if uploaded_files:
                all_chunks = []
                for uploaded_file in uploaded_files:
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.read())
                        path = tmp.name
                    loader = PyPDFLoader(path) if suffix == ".pdf" else TextLoader(path)
                    data = loader.load()
                    for d in data: d.metadata["source"] = uploaded_file.name
                    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
                    all_chunks.extend(splitter.split_documents(data))
                
                vectorstore = FAISS.from_documents(all_chunks, embeddings)
                retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                context_docs = retriever.invoke(query)

            # Web Retrieval (if applicable)
            if use_web and ("WEB" in q_type or "HYBRID" in q_type):
                web_results = perform_tavily_search(query)
                web_context = "\n".join([f"WEB SOURCE [{r['source']}]: {r['content']}" for r in web_results])

            # 3. Final Generation
            combined_context = format_docs(context_docs) + "\n" + web_context
            
            qa_prompt = ChatPromptTemplate.from_template("""
            You are a helpful AI Assistant. Answer the question based on the provided context.
            If the information comes from a document, cite it as [Doc: filename].
            If it comes from the web, cite it as [Web: URL].
            
            Context: {context}
            Question: {query}
            Answer:""")
            
            final_chain = qa_prompt | llm | StrOutputParser()
            answer = final_chain.invoke({"context": combined_context, "query": query})

            # --- DISPLAY RESULTS ---
            tab1, tab2, tab3 = st.tabs(["✨ Grounded Answer", "📄 Doc Evidence", "🌐 Web Evidence"])
            
            with tab1:
                st.markdown(f'<div class="results-box">{answer}</div>', unsafe_allow_html=True)
                # Display Chips
                st.write("---")
                st.caption("QUERY CLASSIFICATION: " + q_type)
                if uploaded_files:
                    for f in uploaded_files: st.markdown(f'<span class="chip">{f.name}</span>', unsafe_allow_html=True)
                if web_context:
                    st.markdown(f'<span class="chip web-chip">Tavily Live Search</span>', unsafe_allow_html=True)

            with tab2:
                if context_docs:
                    for d in context_docs:
                        with st.expander(f"Source: {d.metadata['source']}"):
                            st.write(d.page_content)
                else:
                    st.write("No local documents used.")

            with tab3:
                if web_context:
                    st.write(web_context)
                else:
                    st.write("Web search was not triggered for this query.")