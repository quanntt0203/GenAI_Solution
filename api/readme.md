# Alpha Chatbot API

A FastAPI-based chatbot service that provides AI-powered knowledge base queries and report generation capabilities using Ollama LLM and ChromaDB vector database.

## 🚀 Features

- **AI-Powered Chatbot**: Natural language processing using Ollama LLM models
- **Knowledge Base Integration**: Vector database search with ChromaDB
- **Multi-Level User Access**: Hierarchical user permissions (super, master, agent)
- **API Key Authentication**: Secure access control
- **Report Generation**: Automated report parameter generation
- **RESTful API**: Clean and documented API endpoints
- **Docker Support**: Containerized deployment

## 📋 Prerequisites

- Python 3.8+
- Ollama server running locally or remotely
- ChromaDB database
- Docker (optional, for containerized deployment)

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/quanntt0203/GenAI_Solution.git
   cd GenAI_Solution/api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the api directory:
   ```env
   # API Configuration
   APP_API_HOST=127.0.0.1
   APP_API_PORT=8088
   
   # Ollama Configuration
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=granite3.2:8b
   
   # ChromaDB Configuration
   CHROMADB_PATH=D:/AI/chromadb/alpha_knowledgebase
   
   # Docker Configuration (if using Docker)
   PYTHON_TAG=3.11-slim
   NETWORK_EXTERNAL=false
   NETWORK_NAME=alpha-network
   NETWORK_DRIVER=bridge
   ```

### Docker Deployment

1. **Create ChromaDB Volume** (Windows)
   ```bash
   docker volume create --driver local --opt type=none --opt device=D:\AI\alpha-rag-chroma --opt o=bind alpha_chromadb
   ```

2. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Building manually**
   ```bash
   docker build -t alpha-chatbot-api .
   docker run -p 8088:8080 alpha-chatbot-api
   ```

## 🚀 Running the Application

### Local Development
```bash
python chatbot_api.py
# or with custom host/port
python chatbot_api.py --server 0.0.0.0 --port 8080
```

### Production
```bash
uvicorn chatbot_api:app --host 0.0.0.0 --port 8088
```

The API will be available at:
- **API Base URL**: `http://localhost:8088`
- **Swagger Documentation**: `http://localhost:8088/apidocs`
- **API Documentation**: `http://localhost:8088/docs`

## 📚 API Endpoints

### 1. Chat Endpoint
**POST** `/chat`

Chat with the AI assistant using knowledge base.

**Request Body:**
```json
{
  "api_key": "c9ced5f3-9e12-42fb-9776-bf8907b7dd83",
  "data": {
    "user_id": "8888",
    "level": 4,
    "query": "What is the winloss report?"
  }
}
```

**Response:**
```json
{
  "status_code": "200",
  "error_message": "",
  "data": {
    "user_id": "8888",
    "is_new_session": false,
    "is_action": false,
    "endpoint": "/winlost_detail_report",
    "params": {
      "report_type": "N/A",
      "from_date": "2023-01-01",
      "to_date": "2023-01-31",
      "product": "All",
      "product_detail": "All",
      "sport": "All",
      "bettype": "All",
      "extra_info": "N/A"
    },
    "response": "AI generated response"
  }
}
```

### 2. Demo Endpoint
**GET** `/demo`

Get a sample response for testing purposes.

### 3. Report Endpoint
**POST** `/report`

Create a new report with specified parameters.

**Request Body:**
```json
{
  "report_type": "winloss",
  "from_date": "2023-01-01",
  "to_date": "2023-01-31",
  "product": "All",
  "product_detail": "All",
  "sport": "All",
  "bettype": "All",
  "extra_info": "Additional info"
}
```

## 🔐 Authentication & Authorization

### API Keys
The system uses API key-based authentication. Valid API keys are configured in `config/api_config.py`:

- `alpha_web`: Web application access
- `alpha_mobile`: Mobile application access
- `alpha_api`: API-to-API communication
- `demo`: Demo/testing purposes

### User Levels
The system supports hierarchical user permissions:

- **Level 4 (super)**: Full access to all features
- **Level 3 (master)**: Advanced access
- **Level 2 (agent)**: Basic access

## 🏗️ Project Structure

```
api/
├── chatbot_api.py          # Main FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container configuration
├── docker-compose.yaml    # Docker Compose setup
├── readme.md              # This file
├── config/
│   ├── __init__.py
│   └── api_config.py      # API keys and user levels
├── dto/
│   ├── __init__.py
│   └── dto_model.py       # Data Transfer Objects
└── service/
    ├── __init__.py
    └── chat_service.py    # Core chat service logic
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_API_HOST` | API server host | `127.0.0.1` |
| `APP_API_PORT` | API server port | `8088` |
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `granite3.2:8b` |
| `CHROMADB_PATH` | ChromaDB database path | Local path |

### Ollama Models
Supported models include:
- `granite3.2:8b` (default)
- `llama3.1`
- Any other Ollama-compatible model

## 🧪 Testing

### Manual Testing
Use the built-in Swagger UI at `http://localhost:8088/apidocs` to test endpoints interactively.

### cURL Examples

**Chat request:**
```bash
curl -X POST "http://localhost:8088/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "c9ced5f3-9e12-42fb-9776-bf8907b7dd83",
    "data": {
      "user_id": "test_user",
      "level": 4,
      "query": "What is the winloss report?"
    }
  }'
```

**Demo request:**
```bash
curl -X GET "http://localhost:8088/demo"
```

## 🛠️ Development

### Adding New Endpoints
1. Define data models in `dto/dto_model.py`
2. Implement business logic in `service/`
3. Add endpoint in `chatbot_api.py`

### Extending User Levels
Update `USER_LEVELS` in `config/api_config.py`:
```python
USER_LEVELS = (
    (5, "admin"),
    (4, "super"), 
    (3, "master"), 
    (2, "agent"),
    (1, "user")
)
```

### Adding New API Keys
Update `api_keys` in `config/api_config.py`:
```python
api_keys = [
    ("app_name", "unique-api-key-here"),
    # ... existing keys
]
```

## 🚨 Error Handling

The API returns standardized error responses:

- **401**: Invalid API key or user level
- **500**: Internal server error
- **200**: Success

Example error response:
```json
{
  "status_code": "401",
  "error_message": "Invalid or missing API Key",
  "data": null
}
```

## 📊 Monitoring & Logs

The application logs important events and errors. Monitor the following:
- API request/response patterns
- Ollama model performance
- ChromaDB query performance
- Authentication failures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/apidocs`
2. Review the logs for error details
3. Ensure Ollama and ChromaDB services are running
4. Verify environment configuration

## 🔄 Version History

- **v1.0.0**: Initial release with basic chat functionality
- Features: AI chat, knowledge base integration, user levels, API authentication