from .data_ingestion import splitter
from .embedding_manager import EmbeddingManager
from .vector_db import VectorStore
from .retriever import Retriever
from langgraph.graph import StateGraph, START, END
from typing_extensions import Annotated
from langchain.messages import HumanMessage
from langgraph.graph.message import add_messages
from typing import Annotated
import time
from langchain_groq import ChatGroq
from groq import Groq
from dotenv import load_dotenv 
import os
from pathlib import Path
from .logger import get_logger
from langchain.messages import AIMessage

logger = get_logger(__name__)

# Load .env from project root (OS-independent)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

if os.getenv("GROQ_API_KEY"):
    logger.info("API key imported successfully")
else:
    logger.critical("API key not found - set GROQ_API_KEY in .env")


client = Groq()
Responsive_agent = ChatGroq(model = "llama-3.1-8b-instant",
                            temperature=0.3)

DATA_LOADED = False
embedding_manager = EmbeddingManager()
vector_store = VectorStore()
QUERY_TTL = 300
QUERY_CACHE = {}


def initialize_data():
    
    global DATA_LOADED
    if DATA_LOADED:
        logger.info("DATA already Loaded")
        return
    
    chunks = splitter()
    text = [doc.page_content for doc in chunks]
    embeddings = embedding_manager.generate_embeddings(text)
    vector_store.add_documents(chunks,embeddings=embeddings)
    logger.info("DATA LOADED successfully")
    DATA_LOADED = True
    
    
initialize_data()
retriever = Retriever(Embedding_Manager=embedding_manager,
                      Vector_Store=vector_store)

def is_valid(cache_entry, ttl):
    return (time.time() - cache_entry["timestamp"]) < ttl


def text_agent(query ,llm=Responsive_agent):
    """
    Retrieves context and generates response using LLM.
    
    Args:
        query: User question
        llm: Language model instance
        
    Returns:
        str: Generated response (NOT dict anymore)
    """
    
    results = retriever.retrieve(query)
    
    if not results:
        return "No relevant information found in knowledge base."
    
    context = "\n\n".join([doc["content"] for doc in results] if results else "")

    PROMPT = f'''### You are a 'Company Secretary' with over '20+' years of experience
whenever a person ask you any question you have to answer him properly using the following 
Context:
- {context}
User Query;
- {query}
Constraints- Don't give any false info only use the following context to answer this is strictly followed by everyone
Response format: should be in Markdown format with perfect response format that looks beautiful to our eyes.
"Answer directly. No greetings. No repeated introductions."
'''
    
    if not context.strip():
        logger.debug("No context related to your query found")
        return "No relevant information found in knowledge base."
    
    else:
       response = llm.invoke(PROMPT)
       logger.info("Response generated")
       return response.content  # ✅ FIXED: Return string directly
   
   
def Voice_agent(audio_file_path=None, client=client):
    """Transcribe audio file using Whisper model.
    
    Args:
        audio_file: audio file
        client: Groq client instance
    
    Returns:
        Transcribed text from audio
    """
    with open(audio_file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file_path, file.read()),
            model="whisper-large-v3-turbo",
            temperature=0,
            response_format="verbose_json",
        )
        
        # Save transcription to file
        query_file_path = os.path.dirname(__file__) + "/User_Query.txt"
        with open(query_file_path, "w") as f:
            f.write(transcription.text)
        
        logger.info("Transcription generated successfully")
        return transcription.text


def langgraph_agent(text_agent=text_agent):
    """Langgraph agent for handle complex agent system fast """
    
    class State(StateGraph):
        messages: Annotated[list, add_messages]
        
    graph = StateGraph(State)
    
    def response(state_graph:State):
        user_query = state_graph["messages"][-1].content
        result = text_agent(user_query)  # Now returns string directly

        return {
            "messages": state_graph["messages"] + [
                AIMessage(content=result)  # ✅ FIXED: result is now a string
            ]
        }

    graph.add_node("response",response)
    graph.add_edge(START, "response")
    graph.add_edge("response", END)
    
    builder = graph.compile()
    return builder

def call_fun(query, builder):
    """
    Process query through LangGraph with caching.
    
    Args:
        query: User question
        builder: Compiled LangGraph
        
    Returns:
        dict: {"response": str} for backward compatibility with frontend
    """
    
    if query in QUERY_CACHE:
        if is_valid(QUERY_CACHE[query], QUERY_TTL):
            return QUERY_CACHE[query]["answer"]
        else:
            del QUERY_CACHE[query]
        
    try:
        result = builder.invoke(
            {"messages":[HumanMessage(content=query)]},
            {"recursion_limit": 30}  
        )
        response = result["messages"][-1].content
        
        QUERY_CACHE[query] = {
            "answer":{"response":response},  # Wrapped for frontend compatibility
            "timestamp":time.time()
        }
        logger.info("Response processed")
        return QUERY_CACHE[query]["answer"]
    
    except Exception as e:
        logger.critical(f"Response not generated: {e}")
        raise RuntimeError(f"Response not generated: {e}") from e