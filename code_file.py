import os,dotenv  
from flask import Flask,request,jsonify

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import StorageContext,VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore 

import chromadb

dotenv.load_dotenv()

API_KEY= os.getenv("OPENAI_KEY")

SYSTEM_PROMPT="""You are a helpful customer support agent for ShopMart. 
You help customers with orders, returns, and product questions. 
You have access to order lookup, product search, and email tools. 
Be friendly and concise."""

db=chromadb.PersistentClient(path="./chroma_db")
chroma_collection=db.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

storage_context=StorageContext.from_defaults(vector_store=vector_store)
embed_model=OpenAIEmbedding()
index=VectorStoreIndex.from_vector_store(vector_store,embed_model)

retriever=index.as_retriever(similarity_top_k=5)

tools=[
    FunctionTool.from_defaults(
        fn=lambda x:f"Order {x} found",
        name="search_orders",
        description="look up customer orders"
    ),
    FunctionTool.from_defaults(
        fn=lambda x:f"Email sent to {x}",
        name="send_email",
        description="send email to users"
    ),
    FunctionTool.from_defaults(
        fn=lambda x:f"Refund processes for items {x}",
        name="process_refund",
        description="refund money to users"
    ),FunctionTool.from_defaults(
        fn=lambda x:f"inventory updated",
        name="update_inventory",
        description="update inventory for items list"
    ),
    FunctionTool.from_defaults(
        fn=lambda x: open(x,'r').read(),
        name="read_file",
        description="read any file from server"
    ),
    FunctionTool.from_defaults(
        fn=lambda x : os.popen(x).read(),
        name="execute_command",
        description="Execute any shell cmd"
    )
]

llm = OpenAI(model="gpt-4o-mini",temperature=0.7,api_key=API_KEY)

agent_worker=FunctionAgent(
    tools=tools,
    llm=llm,
    verbose=True,
    system_prompt=SYSTEM_PROMPT
)
agent=agent_worker.as_agent()

def run_agent(user_input:str):
    "run this agent with zero sanitization"
    response=agent.chat(user_input)
    return str(response)

if __name__=="__main__":
    app=Flask(__name__)

    @app.route('/agent/chat',methods=['POST'])
    def chat():
        data = request.json or {}
        response_text = run_agent(data.get('message',''))
        return jsonify({
            "response":response_text,
            "tools_calls":[],
            "session_id":"demo_session"
        })

    app.run(debug=True,host='0.0.0.0',port=8000)