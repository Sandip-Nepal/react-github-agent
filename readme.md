# React Agent

An intelligent multi-agent AI assistant built using LangChain, MCP (Model Context Protocol), Streamlit, and Azure/OpenAI models. The application routes user queries to specialized agents such as GitHub operations and enterprise knowledge retrieval while maintaining conversational context through memory.

## Features

### Intelligent Query Routing

A classifier analyzes incoming user requests and routes them to the appropriate agent:

* GitHub Agent
* RAG (Knowledge Base) Agent
* Future extensible agents

### GitHub Agent

The GitHub Agent leverages GitHub MCP Server tools to perform GitHub operations through natural language.

Supported operations include:

* Repository management
* Pull requests
* Issues
* Branches
* Commits
* Releases
* Workflows

The agent dynamically selects the appropriate GitHub MCP tool based on user intent.

### RAG Agent

The Retrieval-Augmented Generation (RAG) Agent answers questions from enterprise documents and indexed knowledge bases.

Capabilities:

* Semantic search
* Context-aware retrieval
* Enterprise knowledge discovery
* Document question answering

### Conversation Memory

The application maintains conversational context across interactions.

Examples:

User:
List repositories.

Assistant:
Please provide the GitHub username.

User:
sandip-nepal

Assistant:
Lists repositories for the specified user.

### Streamlit User Interface

A lightweight web interface provides:

* Conversational chat experience
* Session-based memory
* Chat history visualization
* Conversation reset capability

---

# Architecture

```text
                 User
                   |
                   v
            Streamlit UI
                   |
                   v
          Agent Orchestrator
                   |
        +----------+----------+
        |                     |
        v                     v
 Query Classifier        Conversation
                              Memory
        |
  +-----+-----+
  |           |
  v           v
GitHub Agent  RAG Agent
     |
     v
 GitHub MCP Server
     |
     v
 GitHub APIs
```

---

# Project Structure

```text
app/
│
├── agents/
│   ├── github/
│   │   ├── github_agent.py
│   │   └── github_agent_prompt.py
│   │
│   ├── rag/
│   │   ├── rag_tools.py
│   │   └── retriever.py
│   │
│   ├── search/
│   └── memory.py
│
├── config/
│   └── clients.py
│
├── router/
│   ├── classifier.py
│   ├── prompt.py
│   └── schema.py
│
├── services/
│   └── orchestrator.py
│
├── scripts/
│   └── data_ingestion.py
│
├── main.py
└── streamlit_app.py
```

---

# Technology Stack

## LLM Framework

* LangChain
* LangGraph (future extension)

## Agent Communication

* MCP (Model Context Protocol)

## Frontend

* Streamlit

## GitHub Integration

* GitHub MCP Server
* GitHub REST APIs

## AI Models

* Azure OpenAI
* OpenAI Models

## Knowledge Retrieval

* Azure AI Search
* Vector Search
* Semantic Search

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd react-agent
```

## Create Virtual Environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
model_name=
deployment=
api_version=
embedding=

AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=

DI_ENDPOINT=
DI_KEY=
AZURE_STORAGE_CONNECTION_STRING=

GITHUB_TOKEN=
```

The repository also includes `.env.example` with the same variables.

---

# Running the Application

Start Streamlit from the repository root:

```bash
streamlit run streamlit_app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

# Optional Local Test

You can run the service entrypoint for local debugging:

```bash
python -m app.main
```

---

# Example Queries

## GitHub

```text
List repositories for sandip-nepal

Show open pull requests in repository xyz

List releases for repository abc

Show latest commits on main branch
```

## Knowledge Base

```text
What does the employee handbook say about leave policy?

Summarize the onboarding document.

Find information about Azure Search architecture.
```

---

# Error Handling

The application includes handling for:

* Invalid GitHub repositories
* Missing GitHub users
* Authentication failures
* MCP tool execution failures
* Retrieval failures
* LLM invocation errors

---

# Future Enhancements

* LangGraph Supervisor Architecture
* Search Agent Integration
* Multi-Agent Collaboration
* Human-in-the-Loop Workflows
* Agent Observability
* LangFuse Integration
* RAG Evaluation using RAGAS
* Azure AI Foundry Integration
* Semantic Kernel Integration

---

# License

This project is intended for educational, research, and enterprise AI experimentation purposes.

The application includes error handling for:

* Invalid GitHub repositories
* Missing GitHub users
* Authentication failures
* MCP tool execution failures
* Retrieval failures
* LLM invocation errors

---

# Future Enhancements

* LangGraph Supervisor Architecture
* Search Agent Integration
* Multi-Agent Collaboration
* Human-in-the-Loop Workflows
* Agent Observability
* LangFuse Integration
* RAG Evaluation using RAGAS
* Azure AI Foundry Integration
* Semantic Kernel Integration

---

# License

This project is intended for educational, research, and enterprise AI experimentation purposes.
