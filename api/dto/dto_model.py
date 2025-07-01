from pydantic import BaseModel

class QueryParam(BaseModel):
    user_id: str = "8888"
    level: int = 0
    query: str = "What is the winloss?"

class ChatQuery(BaseModel):
    api_key: str = "c9ced5f3-9e12-42fb-9776-bf8907b7dd83"
    data: QueryParam

class ReportParam(BaseModel):
    report_type: str = "N/A"
    from_date: str = "2023-01-01"
    to_date: str = "2023-01-31"
    product: str = "All"
    product_detail: str = "All"
    sport: str = "All"
    bettype: str = "All"
    extra_info: str = "N/A"

class ResponseData(BaseModel):
    user_id: str = "user_id"
    is_new_session: bool = False
    is_action: bool = False
    endpoint: str = None
    params: ReportParam = None
    response: str = "Message from the chatbot"


class ChatResult(BaseModel):
    status_code: str
    error_message: str
    data: ResponseData