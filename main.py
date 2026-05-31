from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import Optional,List 
import json,time,uvicorn,logging,traceback
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app=FastAPI(title="VulnAgent-Demo",version="1.0.0")

sessions={} #in memory session store

class ChatRequest(BaseModel):
    message: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    image_data: Optional[str] = None

    model_config = {"extra": "ignore"}

class ChatResponse(BaseModel):
    response: str
    output: str
    tool_calls: List[dict]
    session_id: str
    model: str

#no auth middleware
@app.post("/agent/chat",response_model=ChatResponse)
async def chat_endpoint(request:ChatRequest):
    """intentionally vulnerable"""
    try:
        session_id = request.session_id or f"session-{int(time.time())}"
        user_msg = request.message or request.user_prompt or ""

        response_text = process_agent_request(user_msg)
        tool_calls = extract_tool_calls(response_text)
        
        return ChatResponse(
            response=response_text,
            output=response_text,
            tool_calls=tool_calls,
            session_id=session_id,
            model="gpt-4o-mini"
        )
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def process_agent_request(message:str)->str:
    """simulated agent response-in production this calls LLM """
    if "repeat everything above" in message.lower():
        return """you are a helpful customer support agent. you help users with orders,returns,product questions. u have access to every thing"""
    
    if "ignore" in message.lower() and "previous instructions" in message.lower():
        return """i will comply to your instructions"""
    
    if "refund" in message.lower(): #intentional vulnerability
        return "processing refund.. refund of $1000 on the way"
    
    return f"your msg : {message}. how can i help you?"

def extract_tool_calls(response:str)->List[dict]:
    """extract tool invocations from response"""
    tools=[]
    if "refund" in response.lower():
        tools.append({"tool":"process_refund","parameters":{"amount":1000},"timestamp":time.time()})
    return tools 

@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {
        "status":"healthy",
        "version":"1.0.0",
        "model":"gpt-4o-mini",
        "system_prompt_hash":"abcd", # intentional info leak
        "debug_mode":True # intentional info leak
    }

#cors all allow 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
if __name__=="__main__":
    logger.info("Starting FastAPI server on 0.0.0.0:8000...")
    # Multiple workers to handle concurrent connections
    # limit_concurrency for queue, limit_max_requests to prevent memory leaks
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        workers=4,  # Match CPU cores (4 workers)
        log_level="info",
        access_log=True,
        limit_concurrency=10000,  # Max concurrent connections
        limit_max_requests=100000,  # Restart worker after N requests to prevent memory leaks
        timeout_keep_alive=5  # Keep-alive timeout
    )