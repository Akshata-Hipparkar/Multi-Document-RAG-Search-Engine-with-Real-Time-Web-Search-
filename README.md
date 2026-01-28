
---

## 🔹 Core Pipeline Breakdown

### 1️⃣ Document Ingestion
- Upload PDFs and text files via Streamlit
- Load documents using LangChain loaders
- Normalize metadata for traceability

### 2️⃣ Text Chunking
- Recursive character chunking
- Overlapping windows for better context
- Metadata preserved per chunk

### 3️⃣ Vector Indexing
- Generate embeddings using HuggingFace MiniLM
- Store vectors in FAISS
- Perform semantic similarity search

### 4️⃣ Query Classification
LLM-based routing categorizes queries as:
- **DOC** → Internal documents only
- **WEB** → Real-time web search
- **HYBRID** → Documents + Web

### 5️⃣ Web Search (Tavily)
- Executes live search queries
- Retrieves titles, snippets, and URLs
- Treated as **temporary context**, not indexed

### 6️⃣ Context Assembly
- Combines document chunks + web snippets
- Applies size limits
- Tags sources clearly

### 7️⃣ Answer Generation
- LLM generates grounded responses
- Explicit citations:
  - `[Doc: filename]`
  - `[Web: URL]`

---

## 💬 Streamlit UI Features

### Sidebar
- 📂 Document uploader
- 🔁 Toggle Tavily web search ON/OFF
- 📊 Indexed file overview

### Main Chat Interface
- Natural language query input
- Hybrid response generation
- Real-time feedback

### Evidence Tabs
- ✨ Grounded Answer
- 📄 Document Evidence
- 🌐 Web Evidence

---

## 🧪 Evaluation Scenarios

| Scenario | Result |
|-------|--------|
| Static document queries | Accurate & grounded |
| Current events | Live web results used |
| Comparative queries | Hybrid reasoning |
| Source transparency | Clear & traceable |

---

## 📈 Strengths

- Real-world hybrid RAG design
- Clean separation of document vs web knowledge
- Transparent citations
- Modular LangChain pipeline
- Strong UI/UX clarity

---

## ⚠️ Limitations

- FAISS index is rebuilt per session
- No long-term persistence
- Query classification relies on LLM judgment
- No multi-user state handling

---

## 🚀 Future Enhancements

- Persistent vector storage
- Feedback-based retrieval scoring
- Multi-modal document support
- Advanced ranking & re-ranking
- User authentication & history

---

## 📚 Key Learnings

✔ Multi-document RAG architecture  
✔ Hybrid retrieval design  
✔ Real-time web integration  
✔ Citation-aware generation  
✔ LangChain + Streamlit production patterns  

---

## 🏁 Conclusion

This project demonstrates a **production-style Hybrid RAG syst**
