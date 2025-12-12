# Quick Start Guide

Get up and running with the Workflow Engine in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (or extract the files)

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Verify Installation

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **API Info**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

## Run the Example

In a new terminal (keep the server running):

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the example
python example_usage.py
```

This will:
1. Create a code review workflow
2. Run it with 3 different code samples
3. Display the results

## Run Tests

```bash
python test_api.py
```

## Using the API

### 1. Create a Workflow

```bash
curl -X POST "http://localhost:8000/graph/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "simple_workflow",
    "nodes": {
      "extract": {
        "tool": "extract_functions",
        "next": "check_complexity"
      },
      "check_complexity": {
        "tool": "check_complexity",
        "next": "end"
      }
    },
    "start_node": "extract"
  }'
```

Response:
```json
{
  "graph_id": "uuid-here",
  "message": "Graph created successfully"
}
```

### 2. Run the Workflow

```bash
curl -X POST "http://localhost:8000/graph/run" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "uuid-from-step-1",
    "initial_state": {
      "code": "def hello():\n    return \"world\"",
      "quality_score": 0,
      "iteration": 0
    }
  }'
```

Response:
```json
{
  "run_id": "uuid-here",
  "status": "running",
  "message": "Workflow execution started"
}
```

### 3. Check Status

```bash
curl "http://localhost:8000/graph/state/uuid-from-step-2"
```

Response:
```json
{
  "run_id": "uuid-here",
  "status": "completed",
  "current_state": {
    "code": "def hello():\n    return \"world\"",
    "functions": [...],
    "complexity_scores": {...},
    ...
  },
  "execution_log": [...]
}
```

## Using Python

```python
import requests

# Create graph
response = requests.post("http://localhost:8000/graph/create", json={
    "name": "my_workflow",
    "nodes": {
        "extract": {"tool": "extract_functions", "next": "end"}
    },
    "start_node": "extract"
})
graph_id = response.json()["graph_id"]

# Run workflow
response = requests.post("http://localhost:8000/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {"code": "def test(): pass"}
})
run_id = response.json()["run_id"]

# Get results
import time
time.sleep(1)  # Wait for execution
response = requests.get(f"http://localhost:8000/graph/state/{run_id}")
print(response.json())
```

## WebSocket Example

```python
import asyncio
import websockets
import json

async def stream_logs(run_id):
    uri = f"ws://localhost:8000/ws/graph/run/{run_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Type: {data['type']}")
            if data['type'] == 'completed':
                break

# Run after starting a workflow
asyncio.run(stream_logs("your-run-id"))
```

## Next Steps

- Explore the **interactive API docs** at http://localhost:8000/docs
- Check out the **example workflow** in `app/workflows/code_review.py`
- Read the full **README.md** for advanced features
- Examine the **code structure** in the `app/` directory

## Troubleshooting

### Port already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Module not found
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database locked
```bash
# Remove the database file and restart
rm workflow_engine.db
```

## Support

For issues or questions, check:
- API documentation: http://localhost:8000/docs
- Code comments in `app/` directory
- README.md for detailed information
