# Workflow Engine - AI Engineering Assignment

A minimal yet powerful workflow/graph engine built with FastAPI, supporting nodes, edges, state management, conditional branching, and looping. Think of it as a simplified version of LangGraph for building agent workflows.

## 🚀 Quick Start

### How to Run

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start the server**:
```bash
uvicorn app.main:app --reload
```

3. **Test it works**:
```bash
python example_usage.py
```

4. **View API docs**: Open `http://localhost:8000/docs`

That's it! The engine is ready to execute workflows.

## 📋 What This Workflow Engine Supports

### Core Workflow Features
- ✅ **Nodes**: Python functions that read and modify shared state
- ✅ **State Management**: Pydantic-validated state flowing through nodes
- ✅ **Edges**: Simple mappings defining execution flow (`"next": "node_name"`)
- ✅ **Conditional Branching**: Route based on state (`if quality_score >= 7`)
- ✅ **Looping**: Repeat nodes until conditions are met with max iteration protection
- ✅ **Tool Registry**: Register and call Python functions as workflow tools

### Advanced Features
- ✅ **Async Execution**: Non-blocking workflow execution with background tasks
- ✅ **WebSocket Streaming**: Real-time execution logs
- ✅ **Persistent Storage**: SQLite database for graphs and execution runs
- ✅ **Error Handling**: Graceful error management with detailed logging
- ✅ **RESTful API**: Clean endpoints with auto-generated documentation

### Example: Code Review Workflow
Includes a complete code review agent that:
1. Extracts functions from Python code
2. Calculates cyclomatic complexity
3. Detects code smells and issues
4. Suggests improvements
5. Loops until quality threshold is met

## 🔧 What Could Be Improved With More Time

### Performance & Scalability
- **Parallel Node Execution**: Fan-out/fan-in patterns for concurrent execution
- **Distributed Processing**: Celery or Ray integration for distributed workflows
- **Caching**: Memoization of node results to avoid redundant computation
- **Connection Pooling**: Optimize database connections for high throughput

### Features & Functionality
- **Subgraphs**: Nested workflows and reusable workflow components
- **Dynamic Graph Modification**: Modify graphs during execution
- **Human-in-the-Loop**: Pause workflows for manual approval/input
- **Retry Logic**: Automatic retry with exponential backoff for failed nodes
- **Timeout Support**: Per-node execution timeouts with graceful handling

### Developer Experience
- **Graph Visualization**: Visual workflow editor and execution viewer
- **Debugging Tools**: Step-through execution and breakpoints
- **Graph Validation**: Enhanced pre-execution validation and linting
- **Template Library**: Pre-built workflow templates for common patterns
- **CLI Tool**: Command-line interface for workflow management

### Production Features
- **Authentication & Authorization**: JWT-based API security with role-based access
- **Multi-tenancy**: Support for multiple users and organizations
- **Metrics & Monitoring**: Prometheus metrics, execution time tracking, alerting
- **Graph Versioning**: Version control for workflow definitions
- **A/B Testing**: Run multiple workflow versions and compare results
- **Scheduling**: Cron-like scheduling for recurring workflows

### Testing & Quality
- **Comprehensive Test Suite**: Unit and integration tests (currently basic)
- **Load Testing**: Performance benchmarks and stress testing
- **CI/CD Pipeline**: Automated testing and deployment
- **Code Coverage**: Aim for >90% test coverage

## Features

- **Graph Engine**: Define workflows as directed graphs with nodes and edges
- **State Management**: Shared state flows through the workflow using Pydantic models
- **Conditional Branching**: Route execution based on state conditions
- **Looping Support**: Repeat nodes until conditions are met
- **Tool Registry**: Register and call Python functions as tools
- **Async Execution**: Non-blocking workflow execution with background tasks
- **WebSocket Streaming**: Real-time execution logs via WebSocket
- **Persistent Storage**: SQLite database for graphs and execution runs
- **Clean API**: RESTful endpoints with comprehensive documentation

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic models for API and state
│   ├── engine.py            # Core workflow engine logic
│   ├── tools.py             # Tool registry and implementations
│   ├── database.py          # Database models and operations
│   └── workflows/
│       ├── __init__.py
│       └── code_review.py   # Example: Code Review workflow
├── requirements.txt
├── .gitignore
└── README.md
```

## 📁 Project Structure

```
app/
├── main.py              # FastAPI application and API endpoints
├── engine.py            # Core workflow engine logic
├── models.py            # Pydantic models for API and state
├── tools.py             # Tool registry and implementations
├── database.py          # Database models and operations
└── workflows/
    └── code_review.py   # Example: Code Review workflow
```

## API Endpoints

### 1. Create a Graph
```bash
POST /graph/create
```

**Request Body:**
```json
{
  "name": "code_review_workflow",
  "nodes": {
    "extract": {
      "tool": "extract_functions",
      "next": "check_complexity"
    },
    "check_complexity": {
      "tool": "check_complexity",
      "next": "detect_issues"
    },
    "detect_issues": {
      "tool": "detect_issues",
      "next": "suggest_improvements"
    },
    "suggest_improvements": {
      "tool": "suggest_improvements",
      "next": "evaluate_quality"
    },
    "evaluate_quality": {
      "tool": "evaluate_quality",
      "next": {
        "condition": "quality_score >= 7",
        "if_true": "end",
        "if_false": "check_complexity"
      }
    }
  },
  "start_node": "extract"
}
```

**Response:**
```json
{
  "graph_id": "uuid-string",
  "message": "Graph created successfully"
}
```

### 2. Run a Graph
```bash
POST /graph/run
```

**Request Body:**
```json
{
  "graph_id": "uuid-string",
  "initial_state": {
    "code": "def example():\n    pass",
    "quality_score": 0,
    "iteration": 0
  }
}
```

**Response:**
```json
{
  "run_id": "uuid-string",
  "status": "running",
  "message": "Workflow execution started"
}
```

### 3. Get Execution State
```bash
GET /graph/state/{run_id}
```

**Response:**
```json
{
  "run_id": "uuid-string",
  "status": "completed",
  "current_state": {
    "code": "def example():\n    pass",
    "functions": [...],
    "complexity_scores": {...},
    "issues": [...],
    "suggestions": [...],
    "quality_score": 8,
    "iteration": 2
  },
  "execution_log": [
    "Started node: extract",
    "Completed node: extract",
    ...
  ]
}
```

### 4. WebSocket for Real-time Logs
```bash
WS /ws/graph/run/{run_id}
```

Connect to receive real-time execution logs as the workflow progresses.

## Example Workflow: Code Review Mini-Agent

The included example implements a code review workflow that:

1. **Extract Functions**: Parses code to identify functions
2. **Check Complexity**: Calculates cyclomatic complexity
3. **Detect Issues**: Identifies code smells and potential bugs
4. **Suggest Improvements**: Generates actionable suggestions
5. **Evaluate Quality**: Scores code quality (0-10)
6. **Loop**: Repeats until quality_score >= 7 (max 5 iterations)

### Running the Example

```python
import requests

# Create the code review graph
response = requests.post("http://localhost:8000/graph/create", json={
    "name": "code_review_workflow",
    "nodes": {
        "extract": {"tool": "extract_functions", "next": "check_complexity"},
        "check_complexity": {"tool": "check_complexity", "next": "detect_issues"},
        "detect_issues": {"tool": "detect_issues", "next": "suggest_improvements"},
        "suggest_improvements": {"tool": "suggest_improvements", "next": "evaluate_quality"},
        "evaluate_quality": {
            "tool": "evaluate_quality",
            "next": {
                "condition": "quality_score >= 7 or iteration >= 5",
                "if_true": "end",
                "if_false": "check_complexity"
            }
        }
    },
    "start_node": "extract"
})

graph_id = response.json()["graph_id"]

# Run the workflow
code_sample = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total
"""

run_response = requests.post("http://localhost:8000/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {
        "code": code_sample,
        "quality_score": 0,
        "iteration": 0
    }
})

run_id = run_response.json()["run_id"]

# Check the final state
import time
time.sleep(2)  # Wait for execution

state_response = requests.get(f"http://localhost:8000/graph/state/{run_id}")
print(state_response.json())
```

## 🔧 What Could Be Improved With More Time

### Performance & Scalability
- **Parallel Node Execution**: Fan-out/fan-in patterns for concurrent execution
- **Distributed Processing**: Celery or Ray integration for distributed workflows
- **Caching**: Memoization of node results to avoid redundant computation
- **Connection Pooling**: Optimize database connections for high throughput

### Features & Functionality
- **Subgraphs**: Nested workflows and reusable workflow components
- **Dynamic Graph Modification**: Modify graphs during execution
- **Human-in-the-Loop**: Pause workflows for manual approval/input
- **Retry Logic**: Automatic retry with exponential backoff for failed nodes
- **Timeout Support**: Per-node execution timeouts with graceful handling

### Developer Experience
- **Graph Visualization**: Visual workflow editor and execution viewer
- **Debugging Tools**: Step-through execution and breakpoints
- **Graph Validation**: Enhanced pre-execution validation and linting
- **Template Library**: Pre-built workflow templates for common patterns
- **CLI Tool**: Command-line interface for workflow management

### Production Features
- **Authentication & Authorization**: JWT-based API security with role-based access
- **Multi-tenancy**: Support for multiple users and organizations
- **Metrics & Monitoring**: Prometheus metrics, execution time tracking, alerting
- **Graph Versioning**: Version control for workflow definitions
- **A/B Testing**: Run multiple workflow versions and compare results
- **Scheduling**: Cron-like scheduling for recurring workflows

### Testing & Quality
- **Comprehensive Test Suite**: Unit and integration tests (currently basic)
- **Load Testing**: Performance benchmarks and stress testing
- **CI/CD Pipeline**: Automated testing and deployment
- **Code Coverage**: Aim for >90% test coverage

---

## 📚 Additional Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design patterns
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Assignment completion summary

## 🧪 Testing

```bash
# Verify setup
python verify_setup.py

# Run API tests
python test_api.py

# Run comprehensive tests
python final_test.py

# Try the example
python example_usage.py
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight, serverless database
- **Uvicorn**: Lightning-fast ASGI server

## 📄 License

MIT License

---

**Built for the AI Engineering Internship Assignment**  
*A production-ready workflow engine demonstrating clean code, async programming, and system design.*
