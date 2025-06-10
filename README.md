# Finmars AI Assistant

An intelligent AI assistant system for portfolio management using cutting-edge agent architectures and modular components.

## Architecture Overview

### 1. Chat Interface - Open WebUI
We utilize [Open WebUI](https://github.com/open-webui/open-webui) as our chat interface platform. Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform that offers:
- Support for Ollama and OpenAI-compatible APIs
- Built-in RAG (Retrieval Augmented Generation) capabilities
- Granular user permissions and access control
- Responsive design with mobile support
- Plugin framework for custom logic
- Web search and browsing integration

### 2. Pipeline Modules - Open WebUI Pipelines
[Open WebUI Pipelines](https://github.com/open-webui/pipelines) provides the capability to build modular agent logic. This framework allows us to:
- Create customizable Python-based workflows
- Build dynamic AI multi-agent behaviors
- Integrate complex business logic
- Support computationally heavy tasks
- Enable function calling and custom RAG implementations

Pipelines is a **FastAPI application** with a fully **OpenAI-compatible API interface**. This means:
- All API endpoints follow the OpenAI API specification
- Any OpenAI client can be made compatible with our agent API by simply replacing the `base_url`
- Seamless integration with existing OpenAI SDK implementations
- Standard request/response formats for chat completions, embeddings, and other endpoints

### 3. Agent Architecture
Agents are implemented using:
- **LangGraph** with ReAct pattern as the primary framework
- **AutoGen** as an alternative agent framework

#### Simple ReAct Agent Architecture as First Step (LangGraph)
The ReAct (Reasoning and Acting) agent follows this workflow:

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM Reasoning │◄──────┐
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────┐       │
│ Tool Selection? │       │
└────┬──────┬─────┘       │
     │      │             │
  No │      │ Yes         │
     │      │             │
     ▼      ▼             │
┌────────┐ ┌─────────────┐│
│Response│ │Tool Execution││
└────────┘ └──────┬───────┘│
              │            │
              └────────────┘
```

The agent:
1. Receives user input
2. Uses LLM to reason about the task
3. Decides whether to use tools or respond
4. If tools are needed, executes them
5. Adds results back to context
6. Loops until task completion

### 4. Tool Infrastructure
Tools are accessible through:
- **LangChain** tooling ecosystem for LangGraph agents
- **AutoGen adapter** ([autogen_ext.tools.langchain](https://microsoft.github.io/autogen/stable//reference/python/autogen_ext.tools.langchain.html#module-autogen_ext.tools.langchain)) for AutoGen agents

This allows seamless tool integration across both agent frameworks.

#### 4.1 Tool Implementation Pattern
Each tool follows a three-step pattern:
1. **Pre-process**: LLM-based input (tool call) preparation and validation
2. **API Request**: Calls to [Finmars Portfolio API](https://api-docs.finmars.com/portfolio.html)
3. **Post-process**: Format results into LLM-optimized strings

#### 4.2 Future Extensions
- MCP Server implementation for comprehensive tool sharing capabilities

### 5. Observability - Langfuse
[Langfuse](https://github.com/langfuse/langfuse) provides comprehensive observability:
- **Trace Tracking**: Monitor all agent execution steps
- **Prompt Management**: Version control and collaborative iteration on prompts
- **Evaluations**: LLM-as-a-judge and custom evaluation pipelines
- **Datasets**: Test sets and benchmarks for continuous improvement
- **LLM Playground**: Testing and iteration environment

## MVP Implementation Plan

### Phase 1: Tool Development
- Create simple tools with limited functionality
- Implement basic API calls to [Finmars Portfolio API](https://api-docs.finmars.com/portfolio.html)
- Focus on core portfolio management operations

### Phase 2: Agent Implementation
- Implement `create_react_agent` using LangGraph
- Set up basic reasoning and tool-calling capabilities
- Test agent workflows

### Phase 3: Pipeline Integration
- Wrap agent logic into Open WebUI Pipelines module
- Configure pipeline endpoints and parameters
- Test integration points

### Phase 4: UI Deployment
- Deploy Open WebUI instance
- Connect pipeline module to the interface
- Enable chat-based interactions with the agent

### Phase 5: Observability Setup
- Integrate Langfuse for trace tracking
- Set up prompt management workflows
- Configure evaluation pipelines

## Getting Started

### Prerequisites
- Python 3.12+
- Docker using docker-compose
- API access to Finmars Portfolio service

### Installation
```bash
# Clone the repository
git clone remote-repo-address/finmars-ai-assistant.git
cd finmars-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Configuration
1. Configure Finmars API credentials
2. Set up LLM provider (OpenAI, Anthropic, etc.)
3. Configure Langfuse connection
4. Deploy Open WebUI and Pipelines

## Project Structure
```
finmars-ai-assistant/
├── README.md
├── libs/
│   └── openapi/
│       └── portfolio/
│           ├── openapi.json         # Local API specification
│           └── openapi_remote.json  # Remote API specification
├── agents/                          # Agent implementations
├── tools/                           # Tool definitions
└── pipelines/                       # Open WebUI pipeline modules
```

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
[Specify your license here]