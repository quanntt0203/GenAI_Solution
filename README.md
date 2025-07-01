# GenAI Solution: Modular AI, Data, and Automation Platform

## Overview

This repository is a modular, container-friendly solution for integrating Generative AI, workflow automation, database reporting, API services, and knowledge base management. It is designed for rapid prototyping and deployment of AI-powered business tools using Python, n8n, Ollama, and Microsoft SQL Server.

## Solution Structure

- **api/** — Python FastAPI-based REST API for chatbot and service orchestration
- **mcp_mssql_report/** — Python-based Model Context Protocol (MCP) server for SQL Server reporting and analytics
- **n8n_ollama/** — Workflow automation (n8n) and LLM server (Ollama) with persistent storage, all containerized
- **chat_knowledgebase/** — Knowledge base chat system (Python)
- **chat-8888/** — Additional chat or API service (Python)

## Key Features

- **AI-Driven Reporting**: Generate SQL Server reports via API or MCP tool calls
- **Workflow Automation**: Orchestrate business processes and AI tasks with n8n
- **LLM Integration**: Use Ollama for local LLM inference and chat
- **Knowledge Base Chat**: Query and interact with your own knowledge base
- **REST API Layer**: Unified API endpoints for chatbot and service orchestration
- **Containerized**: All major services are Docker-ready for easy deployment

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/quanntt0203/GenAI_Solution.git
   cd GenAI_Solution
   ```

2. **Review and configure each module**
   - See each subfolder's `README.md` for detailed setup and usage instructions.

3. **Start services with Docker Compose**
   - For n8n, Ollama, and supporting services:
     ```bash
     cd n8n_ollama
     docker compose -f docker-compose.yml up -d
     ```
   - For API and other Python services, see their respective folders.

4. **Run Example Workflows and Reports**
   - Use the test scripts in `mcp_mssql_report/test/` to verify database connectivity and reporting.
   - Access n8n at [http://localhost:5678](http://localhost:5678) and configure workflows.
   - Access the API endpoints as described in `api/README.md`.

## Prerequisites

- Docker & Docker Compose (for containerized services)
- Python 3.9+ (for Python modules)
- Microsoft SQL Server (for reporting)
- Sufficient disk space for persistent data

## Security & Production Notes

- Change all default credentials before deploying to production
- Secure network access to containers and databases
- Regularly back up persistent data folders

## Documentation

- Each module contains its own `README.md` and usage documentation
- See `docs/` in each subfolder for advanced configuration and API details

## Support & Contributions

- Issues and PRs are welcome! Please open an issue for bug reports or feature requests.

---

For more details, see the documentation in each subfolder and the official docs for n8n, Ollama, and MCP.
