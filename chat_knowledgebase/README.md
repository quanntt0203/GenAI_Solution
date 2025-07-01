# Alpha Knowledgebase β

A powerful Streamlit-based RAG (Retrieval-Augmented Generation) application that allows users to upload PDF documents and query them using AI. The system combines ChromaDB vector storage with Ollama LLM models to provide intelligent document search and question-answering capabilities.

## 🚀 Features

- **PDF Document Processing**: Upload and process PDF files into searchable knowledge base
- **Vector Search**: ChromaDB-powered semantic search with Ollama embeddings
- **AI-Powered Q&A**: Natural language querying using Ollama LLM models
- **Cross-Encoder Re-ranking**: Advanced relevance scoring with MS MARCO MiniLM model
- **Multiple LLM Support**: Choose between different Ollama models (llama3.1, deepseek-r1)
- **Streamlit Web Interface**: User-friendly web application
- **Admin Controls**: Document upload restricted to admin users
- **Real-time Streaming**: Live response generation from AI models
- **Docker Support**: Containerized deployment for easy setup

## 📋 Prerequisites

- Python 3.8+
- Ollama server running locally or remotely
- Docker (optional, for containerized deployment)
- ChromaDB for vector storage
- PDF documents for knowledge base

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/quanntt0203/GenAI_Solution.git
   cd GenAI_Solution/chat_knowledgebase
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
   Create a `.env` file in the project directory:
   ```env
   # Ollama Configuration
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3.1
   
   # Docker Configuration (if using Docker)
   PYTHON_TAG=3.11-slim
   NETWORK_EXTERNAL=false
   NETWORK_NAME=alpha-network
   NETWORK_DRIVER=bridge
   ```

### Docker Deployment

1. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Building manually**
   ```bash
   docker build -t alpha-knowledgebase .
   docker run -p 8889:8889 alpha-knowledgebase
   ```

## 🚀 Running the Application

### Local Development
```bash
cd src
streamlit run chat_knowledgebase.py --server.port=8889
```

### Production (Docker)
```bash
docker-compose up -d
```

The application will be available at:
- **Web Interface**: `http://localhost:8889`

## 📚 How to Use

### 1. Admin Document Upload
Access the application with admin privileges by adding `?is_admin=1` to the URL:
```
http://localhost:8889?is_admin=1
```

**Upload Process:**
1. Navigate to the sidebar
2. Click "📑 Upload PDF files for QnA"
3. Select your PDF document
4. Click "⚡️ Process" to add it to the knowledge base

### 2. Querying the Knowledge Base

1. **Select Model**: Choose from available Ollama models:
   - `llama3.1` (default)
   - `deepseek-r1`

2. **Ask Questions**: Enter your question in the text area

3. **Get Answers**: Click "🔥 Ask" to receive AI-generated responses

### Example Queries
- "What are the main topics covered in this document?"
- "Summarize the key findings from the research"
- "Explain the methodology used in the study"
- "What are the conclusions and recommendations?"

## 🏗️ System Architecture

```
chat_knowledgebase/
├── docker-compose.yaml     # Docker orchestration
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── src/
    └── chat_knowledgebase.py  # Main Streamlit application
```

### Core Components

1. **Document Processing Pipeline**
   - PDF loading with PyMuPDF
   - Text chunking with RecursiveCharacterTextSplitter
   - Vector embedding with Ollama nomic-embed-text

2. **Vector Storage**
   - ChromaDB persistent client
   - Cosine similarity search
   - Efficient document retrieval

3. **AI Response Generation**
   - Ollama LLM integration
   - Context-aware prompting
   - Streaming response delivery

4. **Re-ranking System**
   - Cross-encoder relevance scoring
   - MS MARCO MiniLM model
   - Top-3 document selection

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default Ollama model | `llama3.1` |
| `PYTHON_TAG` | Python Docker image tag | `3.11-slim` |

### Model Configuration

**Supported Models:**
- `llama3.1`: General-purpose language model
- `deepseek-r1`: Specialized reasoning model
- `nomic-embed-text:latest`: Embedding model for vector search

**Chunking Parameters:**
- Chunk size: 400 characters
- Chunk overlap: 100 characters
- Separators: `["\n\n", "\n", ".", "?", "!", " ", ""]`

### Vector Database Settings

- **Backend**: ChromaDB with persistent storage
- **Embedding Function**: Ollama nomic-embed-text
- **Similarity Metric**: Cosine similarity
- **Storage Path**: `./alpha-rag-chroma`

## 🧪 Testing

### Manual Testing

1. **Document Upload Test**
   ```bash
   # Access admin interface
   curl http://localhost:8889?is_admin=1
   ```

2. **Query Test**
   - Upload a sample PDF document
   - Ask questions about the content
   - Verify accurate responses

### Health Check
```bash
# Check if Streamlit is running
curl http://localhost:8889/_stcore/health
```

## 🚨 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Verify Ollama server is running
   - Check `OLLAMA_HOST` configuration
   - Ensure models are pulled: `ollama pull llama3.1`

2. **ChromaDB Storage Issues**
   - Check write permissions for `./alpha-rag-chroma`
   - Clear vector collection if corrupted
   - Restart application to reinitialize

3. **PDF Processing Errors**
   - Ensure PDF files are not password-protected
   - Check file size limitations
   - Verify PyMuPDF installation

4. **Memory Issues**
   - Monitor vector database size
   - Consider chunking strategy adjustments
   - Increase Docker memory limits if needed

### Debug Mode

Enable Streamlit debug mode:
```bash
streamlit run chat_knowledgebase.py --server.port=8889 --logger.level=debug
```

## 🔐 Security & Access Control

### Admin Access
- Document upload requires `?is_admin=1` URL parameter
- No authentication mechanism (development mode)
- Consider implementing proper auth for production

### Data Privacy
- Documents stored locally in ChromaDB
- No external data transmission (except to Ollama)
- Vector embeddings remain on-premises

## 🚀 Performance Optimization

### Recommendations

1. **Vector Search**
   - Limit `n_results` for faster queries
   - Implement result caching
   - Consider batch processing for multiple documents

2. **LLM Response**
   - Adjust context window size
   - Implement response caching
   - Use streaming for better UX

3. **Memory Management**
   - Regular vector collection cleanup
   - Monitor ChromaDB size
   - Implement document archiving

## 🛠️ Development

### Adding New Features

1. **New Document Types**
   - Extend `process_document()` function
   - Add new loaders in requirements.txt
   - Update file upload filters

2. **Custom Models**
   - Add model options in selectbox
   - Configure model-specific parameters
   - Update environment variables

3. **Enhanced UI**
   - Modify Streamlit components
   - Add custom CSS styling
   - Implement user sessions

### Code Structure

```python
# Main functions overview
process_document()          # PDF processing pipeline
get_vector_collection()     # ChromaDB initialization
add_to_vector_collection()  # Document indexing
query_collection()          # Semantic search
call_llm()                 # AI response generation
re_rank_cross_encoders()   # Relevance scoring
```

## 📊 Monitoring

### Key Metrics

- Document processing time
- Query response latency
- Vector search accuracy
- Memory usage patterns
- Model performance

### Logging

Monitor Streamlit logs for:
- Document upload events
- Query patterns
- Error conditions
- Performance bottlenecks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add/modify functionality
4. Test with sample documents
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. **Document Issues**: Verify PDF format and size
2. **Model Issues**: Check Ollama server status and model availability
3. **Performance Issues**: Monitor system resources and ChromaDB size
4. **Configuration Issues**: Verify environment variables and network connectivity

## 🔄 Version History

- **v1.0.0**: Initial release with PDF upload and RAG functionality
- Features: PDF processing, vector search, multiple LLM support, cross-encoder re-ranking

## 🎯 Roadmap

- [ ] User authentication system
- [ ] Multiple document format support
- [ ] Advanced search filters
- [ ] Response evaluation metrics
- [ ] API endpoint integration
- [ ] Batch document processing
- [ ] Custom embedding models
