# n8n Ollama Integration

## Overview

This project provides a containerized environment for running [n8n](https://n8n.io/) (a workflow automation tool) together with [Ollama](https://ollama.com/) (an open-source LLM server) and supporting services. It is designed for easy orchestration and persistent data storage using Docker Compose.

## Folder Structure

- `docker-compose.yml` — Main Docker Compose file for orchestrating all services
- `Dockerfile_n8n` — Custom Dockerfile for n8n (if you need to extend n8n)
- `n8n_data/` — Persistent data for n8n (database, logs, configs, etc.)
- `n8n_template/` — Example n8n workflow templates
- `ollama_data/` — Persistent data for Ollama (models, keys, etc.)
- `postgres_data/` — Persistent data for PostgreSQL (if used)

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose installed
- Sufficient disk space for persistent data

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd GenAI_Solution/n8n_ollama
   ```

2. **Start all services**:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```
   This will start n8n, Ollama, and any supporting services defined in the compose file.

3. **Access n8n UI**:
   - Open your browser and go to: [http://localhost:5678](http://localhost:5678)

4. **Access Ollama**:
   - Ollama will be available at its configured port (see `docker-compose.yml`).

5. **Persisted Data**:
   - All workflow data, logs, and models are stored in the respective `*_data/` folders for durability.

## Customization

- **n8n Custom Nodes**: Place custom nodes in `n8n_data/nodes/` and restart the container.
- **n8n Templates**: Import workflows from `n8n_template/` via the n8n UI.
- **Ollama Models**: Place or download models into `ollama_data/models/`.
- **Postgres**: If using PostgreSQL, data is persisted in `postgres_data/`.

## Stopping and Restarting

- To stop all services:
  ```bash
  docker compose -f docker-compose.yml down
  ```
- To restart:
  ```bash
  docker compose -f docker-compose.yml up -d
  ```

## Troubleshooting

- Check container logs:
  ```bash
  docker compose -f docker-compose.yml logs
  ```
- Ensure ports 5678 (n8n), 11434 (Ollama), and 5432 (Postgres) are not in use by other applications.
- For persistent issues, remove the `*_data/` folders (data loss!) and restart.

## Security & Production Notes

- Change default credentials and secrets before deploying to production.
- Review and restrict network access to the containers as needed.
- Regularly back up your `n8n_data/` and `ollama_data/` folders.

## References

- [n8n Documentation](https://docs.n8n.io/)
- [Ollama Documentation](https://ollama.com/docs)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

For advanced configuration, see the comments in `docker-compose.yml` and the official documentation for each service.
