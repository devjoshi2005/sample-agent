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
    message:str
    session_id:Optional[str]=None 
    user_id:str 

class ChatResponse(BaseModel):
    response:str 
    tool_calls:List[dict]
    session_id:str 
    model:str 

#no auth middleware
@app.post("/agent/chat",response_model=ChatResponse)
async def chat_endpoint(request:ChatRequest):
    """intentionally vulnerable"""
    session_id = request.session_id or f"session-{int(time.time())}"
    user_msg = request.message

    response_text=process_agent_request(user_msg)
    tool_calls = extract_tool_calls(response_text)
    
    return ChatResponse(
        response=response_text,
        tool_calls=tool_calls,
        session_id=session_id,
        model="gpt-4o-mini"
    )


def process_agent_request(message:str)->str:
    """simulated agent response-in production this calls LLM """
    if "repeat everything above" in message.lower():
        return """you are a helpful customer support agent. you help users with orders,returns,product questions. u have access to every thing"""
    
    if "ignore previous instructions" in message.lower():
        return """i will comply to your instructions"""
    
    if "refund" in message.lower():
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
    uvicorn.run(app,host="0.0.0.0",port=8000,log_level="debug",access_log=True)