# Finmars AI Assistant - Technical Overview

##  SSL Configuration Complete

1. Removed certbot service from docker-compose-ssl.yaml (since you already have one running)
2. Nginx configured to:
  - Serve HTTPS on port 8881 (mapped from container's 443)
  - Use existing Let's Encrypt certificates from /opt/finmars/nginx/ssl
  - Proxy requests to open-webui service on port 8080
3. Open WebUI now only exposes port 8080 internally (no external port mapping needed)

To deploy:

docker-compose -f docker-compose-ssl.yaml up -d

You'll then access Open WebUI at: https://yourdomain.com:8881

The setup now uses your existing Let's Encrypt certificates from the main Finmars deployment, avoiding port conflicts and certificate duplication.

The configuration is set up to allow iframe embedding. The key lines that enable this are:

##  Allow iframe embedding from main domain

```
proxy_hide_header X-Frame-Options;
proxy_hide_header Content-Security-Policy;
add_header X-Frame-Options "ALLOWALL";
add_header Content-Security-Policy "frame-ancestors 'self' https://${MAIN_DOMAIN_NAME} https://*.${MAIN_DOMAIN_NAME};";
```

This configuration:
1. Removes restrictive headers that Open WebUI might set
2. Allows iframe embedding from your main domain
3. Permits cross-port embedding (443 → 8881)

So you can embed it in your main site like:

```
  <iframe src="https://yourdomain.com:8881" width="100%" height="600"></iframe>
```

The browser will accept this because:
- Both use HTTPS (secure context)
- Same domain (just different ports)
- Headers explicitly allow the embedding


## Key Services and Technologies

### Open WebUI
[Open WebUI](https://github.com/open-webui/open-webui) is an extensible, feature-rich, and user-friendly self-hosted AI interface that serves as the primary chat platform for the Finmars AI Assistant.

**Key Features:**
- Support for OpenAI-compatible APIs
- Built-in RAG (Retrieval Augmented Generation) capabilities
- Granular user permissions and access control
- Responsive design with mobile support
- Plugin framework for custom logic
- Web search and browsing integration

**License:** (Copyright (c) 2023-2025 Timothy Jaeryang Baek (Open WebUI)) https://github.com/open-webui/open-webui/blob/main/LICENSE

### Open WebUI Pipelines
[Open WebUI Pipelines](https://github.com/open-webui/pipelines) provides the capability to build modular agent logic through customizable Python-based workflows that can be used in `Open WebUI`.

**Key Features:**
- FastAPI application with fully OpenAI-compatible API interface
- Dynamic AI multi-agent behaviors
- Complex business logic integration
- Function calling and custom RAG implementations
- Standard OpenAI request/response formats for chat completions

**License:** (MIT License) https://github.com/open-webui/pipelines/blob/main/LICENSE

### LangChain
[LangChain](https://github.com/langchain-ai/langchain) is a comprehensive framework for developing applications powered by language models.

**Key Features:**
- Tool orchestration and management
- Prompt template management
- Chain construction for complex workflows
- Integration with multiple LLM providers
- Extensive ecosystem of pre-built components

**Version:** v0.3.25  
**License:** (MIT License) https://github.com/langchain-ai/langchain/blob/master/LICENSE

### LangGraph
[LangGraph](https://github.com/langchain-ai/langgraph) is a library for building stateful, multi-actor applications with LLMs.

**Key Features:**
- ReAct (Reasoning and Acting) agent pattern implementation
- Stateful agent workflows
- Graph-based agent orchestration
- Built on top of LangChain
- Support for complex multi-step reasoning

**Version:** v0.4.8  
**License:** (MIT License) https://github.com/langchain-ai/langgraph/blob/main/LICENSE

### Langfuse (Optional - Recommended to Skip for Initial Production)
[Langfuse](https://github.com/langfuse/langfuse) is an LLM observability platform that provides comprehensive monitoring and debugging capabilities, prompt management, evaluations.

**Purpose:** Langfuse serves as an observability layer for LLM applications - similar to Sentry but specifically designed for Large Language Models. It provides tracing, logging, and prompt management capabilities and etc

**Important Note:** Regarding **Finmars Integration Constraints:**, it is recommended to **exclude it from initial production deployments** due to:
- **Deployment Complexity:** Requires additional database services (PostgreSQL, ClickHouse, Redis, MinIO) which add complexity to the deployment architecture
- **Finmars Integration Constraints:** The specific deployment requirements when integrating with Finmars infrastructure make it preferable to start with a simpler stack
- **Optional Nature:** The core AI Assistant functionality operates fully without Langfuse - it's purely for observability and debugging

Langfuse integration has been made completely optional. 
The system automatically detects if Langfuse environment variables are present and only enables the callback handler when configured. 
This allows for seamless operation with or without Langfuse.

**Features (When Used):**
- LLM call tracing and debugging
- Prompt version management
- Performance metrics and analytics
- Error tracking and debugging capabilities

**License:** (Copyright (c) 2023--2024 Langfuse GmbH) https://github.com/langfuse/langfuse/blob/main/LICENSE

## Production Deployment Stack

For production environments integrated with Finmars, two deployment options are available:

### Core Stack (Recommended for Initial Production)
A new `docker-compose-core.yaml` file provides the minimal production-ready stack:

1. **Open WebUI** - User interface (Docker container on port 8881)
2. **Agent Pipelines Service** - FastAPI backend with OpenAI-compatible API (port 9299)

These two services provide full functionality without any observability infrastructure. No Langfuse environment variables are required.

### Full Stack (With Observability)
The original `docker-compose.yaml` includes all services with Langfuse for development and advanced monitoring needs.

## ***[generated by llm, not validated]*** Python Libraries and Dependencies (check deps in ./requirements.txt)

### Core AI/ML Libraries
- **langchain** (v0.3.25) - MIT License
- **langgraph** (v0.4.8) - MIT License
- **langchain-openai** (v0.3.23) - MIT License
- **langfuse** (v3.0.2) - (optional, can be removed)

### Web Framework
- **fastapi** (v0.115.13) - MIT License
- **uvicorn** (v0.22.0) - BSD License
- **pydantic** (v2.7.4) - MIT License

### HTTP Clients
- **httpx** (v0.28.1) - BSD License
- **aiohttp** (v3.9.5) - Apache License 2.0
- **requests** (v2.32.2) - Apache License 2.0

### Authentication & Security
- **PyJWT[crypto]** - MIT License
- **passlib[bcrypt]** (v1.7.4) - BSD License

### Development Tools
- **pytest** (v8.4.0) - MIT License
- **pytest-asyncio** (v1.0.0) - MIT License
- **black** (v25.1.0) - MIT License
- **datamodel-code-generator** (v0.30.2) - MIT License

### Utilities
- **python-dotenv** (v1.1.0) - BSD License
- **python-multipart** (v0.0.9) - Apache License 2.0
- **python-socketio** - MIT License
