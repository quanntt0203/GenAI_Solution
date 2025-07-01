import sys
import os
from dotenv import load_dotenv
load_dotenv()

APP_API_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(f"{APP_API_PATH}/dto/"))
sys.path.append(os.path.abspath(f"{APP_API_PATH}/service/"))
sys.path.append(os.path.abspath(f"{APP_API_PATH}/config/"))

os.environ["APP_API_PATH"] = APP_API_PATH

# pc desktop
# os.environ["OLLAMA_HOST"] = "http://10.21.10.36:7869"
# os.environ["OLLAMA_MODEL"] = "llama3.1"
# os.environ["CHROMADB_PATH"] = "D:/AI/alpha-rag-chroma"

# laptop
os.environ["OLLAMA_HOST"] = "http://localhost:11434"
os.environ["OLLAMA_MODEL"] = "granite3.2:8b"
os.environ["CHROMADB_PATH"] = "D:/AI/chromadb/alpha_knowledgebase"

import uvicorn
import argparse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dto_model import ChatQuery, ChatResult, ResponseData, ReportParam
from chat_service import ChatService
from api_config import api_keys, USER_LEVELS

app = FastAPI(
    title="Chatbot API", 
    description="A simple RESTful API for managing reports",
    version="1.0.0",
    docs_url="/apidocs",  # Custom URL for Swagger UI
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}}
)

origins = [
    f"http://{os.environ.get("APP_API_HOST")}:{os.environ.get("APP_API_PORT")}",
    f"https://{os.environ.get("APP_API_HOST")}:{os.environ.get("APP_API_PORT")}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", summary="Get knowlegde base", description="Ask for knowledge base")
def chat(query: ChatQuery):
    """
    Generate report's parameter or ask for knowledge base
    """
    
    if not api_keys or query.api_key not in [key[1] for key in api_keys]:
        return ChatResult(status_code=401, error_message="Invalid or missing API Key")
    
    if query.data.level not in [key[0] for key in USER_LEVELS]:
        return ChatResult(status_code=401, error_message="Invalid or missing user level")   

    user_level = dict(USER_LEVELS)[query.data.level]

    service = ChatService(level=user_level)
    response_message = service.chat_message(query=query)
    if response_message is None:
        return ChatResult(status_code=500, error_message="Error generating response")    
    
    result: ChatResult = ChatResult(
        status_code="200",
        error_message="",
        data=ResponseData(
            user_id=query.data.user_id,
            response=response_message
        )
    )

    return result

@app.get("/demo", summary="Generate or get knowlegde base", description="Generate report's parameter or ask for knowledge base")
async def demo():
    """
    Get a sample report
    """
    result: ChatResult = ChatResult(
        status_code="200",
        error_message="",
        data=ResponseData(
            user_id="user_id",
            is_new_session=False,
            is_action=False,
            endpoint="/winlost_detail_report",
            params=ReportParam(
                report_type="N/A",
                from_date="2023-01-01",
                to_date="2023-01-31",
                product="All",
                product_detail="All",
                sport="All",
                bettype="All",
                extra_info="N/A"
            ),
            response="Message from the chatbot"
        )
    )

    return result

@app.post("/report", summary="Create a new report", description="Create a new report")
async def report(params: ReportParam):
    """
    Create a new report
    """
    return params


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", help="host of the server", default="127.0.0.1", type=str)
    parser.add_argument("-p", "--port", help="port number of the server", default=8080, type=int)

    args = parser.parse_args()
    server_port = args.port if args.port else os.environ.get("APP_API_PORT")
    server_host = args.server if args.server else os.environ.get("APP_API_HOST")

    uvicorn.run(app, port=8088)
