# 🎙️ Voice-Powered Company RAG System

An end-to-end **Voice-enabled Retrieval-Augmented Generation (RAG)** system that allows users to ask questions via voice and receive AI-generated answers based on company documents.

---

## 🚀 Features

- 🎤 Voice input via microphone (Streamlit)
- 🧠 Retrieval-Augmented Generation (RAG)
- 📄 Custom knowledge base (company files)
- 🔎 Semantic search using embeddings
- 🤖 LLM responses (Groq - LLaMA 3.1)
- ⚡ FastAPI backend
- 🎨 Modern chat UI
- 🧩 LangGraph agent workflow
- 💾 Query caching (TTL-based)

---

## 🏗️ Project Structure
VOICE/
│
├── Backend/
│ └── back_server.py
│
├── Frontend/
│ └── front_server.py
│
├── pipeline/
│ ├── agents.py
│ ├── data_ingestion.py
│ ├── embedding_manager.py
│ ├── vector_db.py
│ ├── retriever.py
│ └── logger.py
│
├── data/
│ ├── company_files/
│ └── vector_database/
│
├── logs/
├── .env
├── requirements.txt
└── README.md

---

## ⚙️ How It Works

1. **Load Data** → Reads `.txt` files from `data/company_files`
2. **Split Text** → Chunking using RecursiveCharacterTextSplitter
3. **Embeddings** → Generated using `bge-small-en-v1.5`
4. **Store** → Saved in ChromaDB
5. **Retrieve** → Top relevant chunks based on query
6. **Generate** → LLM (Groq) produces final response
7. **Voice Flow** → Audio → Whisper → Text → Answer

---

## 🧪 Setup

### 1. Clone Repo
```bash
git clone <your-repo-url>
cd VOICE
2. Create Virtual Environment
python -m venv .venv
Activate:
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Add Environment Variables

Create .env file:

GROQ_API_KEY=your_api_key_here
▶️ Run the Project
Start Backend
python Backend/back_server.py
Start Frontend
streamlit run Frontend/front_server.py
🎯 Usage
Click 🎙️ Start Recording
Speak your query
System transcribes audio
Query is processed via RAG pipeline
Response is displayed in chat UI
🧠 Core Components
🔹 text_agent
Retrieves context
Generates response using LLM
🔹 Voice_agent
Converts audio → text using Whisper
🔹 langgraph_agent
Manages flow using LangGraph
🔹 call_fun
Adds caching layer (TTL = 300s)
⚡ Performance Optimizations
Query caching
Persistent vector database
Chunk-based retrieval
Threshold filtering
⚠️ Common Issues
❌ InvalidSchema Error

Fix:

"http://127.0.0.1:8000/server"
❌ No response / repeated output
Ensure LLM returns string (already fixed in code)
❌ Backend not connecting
Start backend before frontend
🔮 Future Improvements
🔊 Text-to-Speech (voice output)
🌐 Cloud deployment
📊 Analytics dashboard
🧠 Multi-agent system
📂 PDF / DOC support
🧑‍💻 Author

Anurag
AI Engineer (in progress 🚀)

⭐ Final Thought

This project is a foundation for real-world AI products like:

Voice assistants
Enterprise knowledge bots
AI SaaS tools