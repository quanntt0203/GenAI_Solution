# Alpha AI Assistant β

A powerful Streamlit-based conversational AI application that provides an interactive chat interface with Ollama LLM models. Built with LangChain for advanced conversation management and chat history tracking.

## 🚀 Features

- **Interactive Chat Interface**: Clean and intuitive Streamlit web interface
- **Multiple LLM Support**: Choose between different Ollama models (llama3.1, deepseek-r1)
- **Conversation History**: Persistent chat history with context awareness
- **LangChain Integration**: Advanced prompt templating and conversation management
- **Real-time Responses**: Streaming responses from AI models
- **Model Switching**: Dynamic model selection during conversations
- **Docker Support**: Containerized deployment for easy setup
- **Environment Configuration**: Flexible configuration via environment variables

## 📋 Prerequisites

- Python 3.8+
- Ollama server running locally or remotely
- Docker (optional, for containerized deployment)
- Streamlit for web interface
- LangChain for conversation management

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/quanntt0203/GenAI_Solution.git
   cd GenAI_Solution/chat-8888
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
   cd chat
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project directory:
   ```env
   # Ollama Configuration
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3.1
   
   # Docker Configuration (if using Docker)
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
   docker build -t alpha-chatbot .
   docker run -p 8888:8888 alpha-chatbot
   ```

## 🚀 Running the Application

### Local Development
```bash
cd chat
streamlit run chat_8888.py --server.port=8888
```

### Production (Docker)
```bash
docker-compose up -d
```

The application will be available at:
- **Web Interface**: `http://localhost:8888`

## 📚 How to Use

### 1. Starting a Conversation

1. **Select Model**: Choose from available Ollama models:
   - `llama3.1` (default) - General-purpose language model
   - `deepseek-r1` - Specialized reasoning model

2. **Enter Message**: Type your question or message in the text area

3. **Send Message**: Click "Ask" to send your message and receive a response

### 2. Managing Conversations

- **Chat History**: All conversations are automatically saved and displayed
- **Context Awareness**: The AI maintains context from previous messages
- **Model Switching**: Change models mid-conversation for different capabilities
- **Session Persistence**: Chat history persists throughout your session

### Example Conversations

**General Chat:**
```
User: Hello! How are you today?
Assistant: Hello! I'm doing well, thank you for asking. I'm here and ready to help you with any questions or tasks you might have.
```

**Technical Questions:**
```
User: Explain the concept of machine learning
Assistant: Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed...
```

**Code Assistance:**
```
User: Write a Python function to calculate fibonacci numbers
Assistant: Here's a Python function to calculate Fibonacci numbers using recursion with memoization...
```

## 🏗️ System Architecture

```
chat-8888/
├── docker-compose.yaml     # Docker orchestration
├── Dockerfile             # Container configuration
└── chat/
    ├── chat_8888.py       # Main Streamlit application
    └── requirements.txt   # Python dependencies
```

### Core Components

1. **Streamlit Interface**
   - Web-based chat interface
   - Model selection dropdown
   - Message input and history display
   - Real-time response rendering

2. **LangChain Integration**
   - Conversation management
   - Prompt templating system
   - Message history handling
   - Chain-based response generation

3. **Ollama LLM Backend**
   - Multiple model support
   - Streaming response generation
   - Configurable model parameters

4. **Session Management**
   - Persistent chat history
   - Model state tracking
   - Context preservation

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default Ollama model | `llama3.1` |
| `NETWORK_EXTERNAL` | External Docker network | `false` |
| `NETWORK_NAME` | Docker network name | `alpha-network` |
| `NETWORK_DRIVER` | Docker network driver | `bridge` |

### Model Configuration

**Supported Models:**
- `llama3.1`: General-purpose conversational AI
- `deepseek-r1`: Advanced reasoning and problem-solving
- Any other Ollama-compatible model

**LangChain Components:**
- `SystemMessagePromptTemplate`: System instructions
- `HumanMessagePromptTemplate`: User messages
- `AIMessagePromptTemplate`: AI responses
- `ChatPromptTemplate`: Complete conversation template

### Streamlit Configuration

- **Port**: 8888
- **Layout**: Wide layout for better chat experience
- **Page Title**: Alpha - AI Assistant - βeta
- **Form Handling**: Clear on submit disabled for message persistence

## 🧪 Testing

### Manual Testing

1. **Basic Chat Test**
   ```bash
   # Start the application
   streamlit run chat_8888.py --server.port=8888
   
   # Test basic conversation
   User Input: "Hello, can you help me?"
   Expected: Friendly greeting and offer to help
   ```

2. **Model Switching Test**
   - Start conversation with llama3.1
   - Switch to deepseek-r1 mid-conversation
   - Verify context is maintained

3. **History Persistence Test**
   - Send multiple messages
   - Verify chat history displays correctly
   - Check conversation context is maintained

### Health Check
```bash
# Check if Streamlit is running
curl http://localhost:8888/_stcore/health
```

## 🚨 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   ```bash
   # Check Ollama server status
   ollama list
   
   # Verify Ollama is running
   curl http://localhost:11434/api/tags
   ```

2. **Model Not Found**
   ```bash
   # Pull required models
   ollama pull llama3.1
   ollama pull deepseek-r1
   ```

3. **Port Already in Use**
   ```bash
   # Use different port
   streamlit run chat_8888.py --server.port=8889
   ```

4. **Environment Variables Not Loading**
   - Verify `.env` file exists in project root
   - Check environment variable syntax
   - Restart application after changes

### Debug Mode

Enable Streamlit debug mode:
```bash
streamlit run chat_8888.py --server.port=8888 --logger.level=debug
```

## 🔐 Security Considerations

### Development Environment
- No authentication required (development mode)
- Local-only access by default
- Environment variables for sensitive configuration

### Production Deployment
- Consider implementing authentication
- Use HTTPS for secure communication
- Restrict network access as needed
- Monitor resource usage

## 🚀 Performance Optimization

### Recommendations

1. **Response Speed**
   - Use faster models for simple queries
   - Implement response caching
   - Optimize prompt templates

2. **Memory Management**
   - Limit chat history length
   - Clear session state periodically
   - Monitor memory usage

3. **Model Selection**
   - llama3.1: Faster responses, general queries
   - deepseek-r1: Complex reasoning, slower but more accurate

## 🛠️ Development

### Code Structure

```python
# Main components
get_history()           # Retrieve formatted chat history
generate_response()     # Generate AI response using LangChain
model initialization    # ChatOllama model setup
session management     # Streamlit session state handling
```

### Adding New Features

1. **New Models**
   ```python
   # Add to model selection
   chat_model = st.selectbox("Select model", 
       ["llama3.1", "deepseek-r1", "new-model"], 
       index=0
   )
   ```

2. **Custom Prompts**
   ```python
   # Add system message template
   system_prompt = SystemMessagePromptTemplate.from_template(
       "You are a helpful assistant specialized in..."
   )
   ```

3. **Enhanced UI**
   - Add message timestamps
   - Implement message editing
   - Add conversation export
   - Custom CSS styling

### LangChain Integration

The application uses LangChain for:
- **Prompt Management**: Structured message templates
- **Chain Operations**: Model | Parser pipeline
- **History Handling**: Conversation context management
- **Output Parsing**: String output parser for clean responses

## 📊 Monitoring

### Key Metrics

- Response generation time
- Model switching frequency
- Conversation length
- User engagement patterns
- Error rates

### Logging

Monitor application logs for:
- Model selection events
- Response generation time
- Error conditions
- User interaction patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement new functionality
4. Test with different models
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings for new functions
- Test with multiple Ollama models
- Update README for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. **Model Issues**: 
   - Verify Ollama server is running
   - Check model availability: `ollama list`
   - Pull missing models: `ollama pull <model-name>`

2. **Connection Issues**:
   - Verify `OLLAMA_HOST` configuration
   - Check network connectivity
   - Ensure firewall allows connection

3. **Performance Issues**:
   - Monitor system resources
   - Try different models
   - Check conversation history length

4. **UI Issues**:
   - Clear browser cache
   - Restart Streamlit application
   - Check browser console for errors

## 🔄 Version History

- **v1.0.0**: Initial release with basic chat functionality
- Features: Multi-model support, conversation history, LangChain integration

## 🎯 Roadmap

- [ ] User authentication system
- [ ] Conversation export/import
- [ ] Custom system prompts
- [ ] Message editing and deletion
- [ ] Advanced model parameters
- [ ] Response evaluation
- [ ] Multi-user support
- [ ] API endpoint integration

## 💡 Tips & Best Practices

### For Users
- Start with simple questions to test model responses
- Switch models based on task complexity
- Keep conversations focused for better context
- Use clear and specific questions

### For Developers
- Monitor session state size
- Implement proper error handling
- Use appropriate model for task complexity
- Consider implementing conversation limits

## 📞 Contact

For technical support or feature requests, please open an issue in the repository.
