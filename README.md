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

#### 4.2 Pydantic Models Architecture
The project uses two distinct types of Pydantic models:

##### API Payload Models (`libs/schema/`)
- **Purpose**: Define the exact structure for API requests/responses
- **Location**: `libs/schema/` directory
- **Characteristics**:
  - Auto-generated from OpenAPI specification
  - Strict validation constraints (string lengths, numeric ranges, formats)
  - Optional fields for flexible API operations
  - View models for read operations
  - Light models for minimal representations
- **Examples**: `PortfolioView`, `TransactionRequest`, `ClientLight`

##### Tool-Calling Input Schemas
- **Purpose**: Define input structures for LLM tool calls
- **Characteristics**:
  - Simplified schemas focused on LLM-friendly inputs
  - May have different field names and structures than API models
  - Related but not inherited from API models
  - Optimized for natural language understanding
  - Flexible validation for conversational inputs
- **Relationship**: These schemas act as adapters between LLM-generated parameters and API payload models

This separation allows for:
- LLM-optimized tool interfaces without API constraints
- Independent evolution of tool calling schemas
- Clear boundary between AI interaction layer and API layer

#### 4.3 Future Extensions
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
│   ├── openapi/
│   │   └── portfolio/
│   │       ├── openapi.json         # Local API specification
│   │       └── openapi_remote.json  # Remote API specification (just changed `base_url` to remote)
│   └── schema/                      # Pydantic models for API payloads
│       ├── account.py               # Account-related models
│       ├── base.py                  # Base enums and types
│       ├── client.py                # Client models
│       ├── counterparty.py          # Counterparty models
│       ├── currency.py              # Currency models
│       ├── instrument.py            # Financial instrument models
│       ├── portfolio.py             # Portfolio models
│       ├── pricing.py               # Pricing models
│       ├── reconcile.py             # Reconciliation models
│       ├── responses.py             # Paginated response models
│       ├── responsible.py           # User responsibility models
│       ├── transaction.py           # Transaction models
│       └── via_data_model_codegen/  # Auto-generated models
├── agents/                          # Agent implementations
├── tools/                           # Tool definitions with input schemas
└── pipelines/                       # Open WebUI pipeline modules
```

## Finmars API Client Library

### Overview
The `libs/client/` directory contains a fully async Python client library for interacting with the Finmars Portfolio API. The client is organized into logical sub-clients based on business domains.

### Features
- **Async/await support** for all API operations
- **Type-safe** with Pydantic model validation
- **Organized by business logic** into specialized sub-clients
- **Comprehensive test coverage**
- **Built-in authentication** with API key support
- **Configurable timeouts** and error handling

### Usage Example

```python
import asyncio
from libs.client import FinmarsPortfolioClient

async def main():
    # Initialize the client
    client = FinmarsPortfolioClient(
        base_url="",
        realm="",
        space="",
        api_key="your-api-key"
    )
    
    # List portfolios
    portfolios = await client.portfolios.list_portfolios(page=1, page_size=10)
    print(f"Found {portfolios.count} portfolios")
    
    # Get specific portfolio
    portfolio = await client.portfolios.get_portfolio(portfolio_id=1)
    print(f"Portfolio: {portfolio.name}")
    
    # List portfolio types
    portfolio_types = await client.portfolio_types.list_portfolio_types()
    
    # Get portfolio history
    history = await client.portfolio_history.list_portfolio_history()
    
    # Access reconciliation data
    reconcile_groups = await client.portfolio_reconcile.list_portfolio_reconcile_groups()

if __name__ == "__main__":
    asyncio.run(main())
```

### Client Structure

The main `FinmarsPortfolioClient` aggregates the following sub-clients:

1. **portfolios** - Portfolio operations (list, get, attributes, inception dates)
2. **portfolio_types** - Portfolio type management and attributes
3. **portfolio_registers** - Portfolio register and record operations
4. **portfolio_history** - Historical portfolio data access
5. **portfolio_reconcile** - Reconciliation groups and history

### Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest libs/client/tests/
```

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
[Specify your license here]