import sys
from pathlib import Path

# Add project root to Python path so pipeline module can be found
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
import uvicorn
from pipeline.agents import call_fun, langgraph_agent
from pipeline.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)
builder = langgraph_agent()

class ServerRequest(BaseModel):
    "Request schema for the /server endpoint"
    
    query: str

app = FastAPI(title="Voice system") 

@app.post("/server")
def server(request:ServerRequest):
    
    logger.info(f"Incomming Request: {request.query[:50]}...")
    
    try:
        answer = {"response":call_fun(request.query, builder)}
        
        logger.info("Query Answered Successfully")
        return {"response":answer["response"]}
    
    except RuntimeError as e:
        logger.error(f"Runtime error in /server: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error in /chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. please try again"
        )
        
if __name__ == "__main__":
    # Run from project root: python -m Backend.back_server
    # Or directly: python Backend/back_server.py (must cd to project root first)
    uvicorn.run(app, port=8000, host="127.0.0.1")
    