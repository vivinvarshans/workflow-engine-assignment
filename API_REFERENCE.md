# API Reference

Complete reference for the Workflow Engine REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. For production use, implement JWT or API key authentication.

## Common Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## Endpoints

### 1. Root Information

Get API information and available endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "name": "Workflow Engine API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "docs": "/docs",
    "create_graph": "POST /graph/create",
    "run_graph": "POST /graph/run",
    "get_state": "GET /graph/state/{run_id}",
    "websocket": "WS /ws/graph/run/{run_id}"
  },
  "registered_tools": ["extract_functions", "check_complexity", ...]
}
```

---

### 2. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

### 3. List Tools

Get all registered tools.

**Endpoint:** `GET /tools`

**Response:**
```json
{
  "tools": [
    "extract_functions",
    "check_complexity",
    "detect_issues",
    "suggest_improvements",
    "evaluate_quality"
  ],
  "count": 5
}
```

---

### 4. Create Graph

Create a new workflow graph.

**Endpoint:** `POST /graph/create`

**Request Body:**
```json
{
  "name": "my_workflow",
  "nodes": {
    "node1": {
      "tool": "tool_name",
      "next": "node2"
    },
    "node2": {
      "tool": "another_tool",
      "next": "end"
    }
  },
  "start_node": "node1",
  "max_iterations": 10
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Workflow name |
| nodes | object | Yes | Node definitions |
| start_node | string | Yes | Starting node name |
| max_iterations | integer | No | Max iterations (default: 10) |

**Node Configuration:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tool | string | Yes | Tool name to execute |
| next | string/object | Yes | Next node or conditional routing |

**Next Node Options:**

1. **Direct routing:**
```json
"next": "node_name"
```

2. **Conditional routing:**
```json
"next": {
  "condition": "quality_score >= 7",
  "if_true": "success_node",
  "if_false": "retry_node"
}
```

3. **End workflow:**
```json
"next": "end"
```

**Response:**
```json
{
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Graph created successfully"
}
```

**Error Responses:**

- `400` - Invalid graph definition
- `400` - Tool not found
- `400` - Start node not in nodes

**Example:**
```bash
curl -X POST "http://localhost:8000/graph/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "code_review",
    "nodes": {
      "extract": {
        "tool": "extract_functions",
        "next": "check_complexity"
      },
      "check_complexity": {
        "tool": "check_complexity",
        "next": {
          "condition": "len(functions) > 0",
          "if_true": "detect_issues",
          "if_false": "end"
        }
      },
      "detect_issues": {
        "tool": "detect_issues",
        "next": "end"
      }
    },
    "start_node": "extract"
  }'
```

---

### 5. Run Graph

Execute a workflow with initial state.

**Endpoint:** `POST /graph/run`

**Request Body:**
```json
{
  "graph_id": "550e8400-e29b-41d4-a716-446655440000",
  "initial_state": {
    "code": "def example():\n    return 42",
    "quality_score": 0,
    "iteration": 0
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| graph_id | string | Yes | UUID of the graph |
| initial_state | object | Yes | Starting state dictionary |

**Response:**
```json
{
  "run_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "Workflow execution started"
}
```

**Status Values:**
- `pending` - Queued for execution
- `running` - Currently executing
- `completed` - Finished successfully
- `failed` - Execution failed

**Error Responses:**

- `404` - Graph not found
- `400` - Invalid initial state

**Example:**
```bash
curl -X POST "http://localhost:8000/graph/run" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "550e8400-e29b-41d4-a716-446655440000",
    "initial_state": {
      "code": "def hello():\n    return \"world\"",
      "quality_score": 0,
      "iteration": 0
    }
  }'
```

---

### 6. Get Execution State

Retrieve the current state of a workflow run.

**Endpoint:** `GET /graph/state/{run_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| run_id | string | UUID of the run |

**Response:**
```json
{
  "run_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "current_state": {
    "code": "def example():\n    return 42",
    "functions": [
      {
        "name": "example",
        "line_start": 1,
        "line_end": 2,
        "args": [],
        "num_lines": 2
      }
    ],
    "complexity_scores": {
      "example": 1
    },
    "issues": [],
    "suggestions": ["Code looks good! No major issues detected."],
    "quality_score": 10,
    "iteration": 1
  },
  "execution_log": [
    "[2024-01-15 10:30:00.123] Starting workflow execution from node 'extract'",
    "[2024-01-15 10:30:00.234] Executing node 'extract' with tool 'extract_functions'",
    "[2024-01-15 10:30:00.345] Node 'extract' completed successfully",
    "[2024-01-15 10:30:00.456] Transitioning from 'extract' to 'check_complexity'",
    "[2024-01-15 10:30:00.567] Workflow completed: reached end node"
  ],
  "error": null,
  "started_at": "2024-01-15T10:30:00.000000",
  "completed_at": "2024-01-15T10:30:01.000000"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| run_id | string | Run identifier |
| status | string | Current status |
| current_state | object | Current workflow state |
| execution_log | array | Log entries |
| error | string/null | Error message if failed |
| started_at | string | Start timestamp |
| completed_at | string/null | Completion timestamp |

**Error Responses:**

- `404` - Run not found

**Example:**
```bash
curl "http://localhost:8000/graph/state/660e8400-e29b-41d4-a716-446655440000"
```

---

### 7. WebSocket - Stream Execution Logs

Connect to a WebSocket for real-time execution updates.

**Endpoint:** `WS /ws/graph/run/{run_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| run_id | string | UUID of the run |

**Message Types:**

1. **Connected:**
```json
{
  "type": "connected",
  "run_id": "660e8400-e29b-41d4-a716-446655440000",
  "message": "WebSocket connected"
}
```

2. **Log Update:**
```json
{
  "type": "log",
  "run_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "logs": [
    "[2024-01-15 10:30:00.123] Starting workflow execution...",
    "[2024-01-15 10:30:00.234] Executing node 'extract'..."
  ]
}
```

3. **Completed:**
```json
{
  "type": "completed",
  "run_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "final_state": {
    "code": "...",
    "quality_score": 8
  }
}
```

**Python Example:**
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
            
            if data['type'] == 'connected':
                print(f"Connected to run: {data['run_id']}")
            
            elif data['type'] == 'log':
                print(f"Status: {data['status']}")
                for log in data['logs']:
                    print(f"  {log}")
            
            elif data['type'] == 'completed':
                print(f"Workflow {data['status']}")
                print(f"Final state: {data['final_state']}")
                break

# Usage
asyncio.run(stream_logs("your-run-id"))
```

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/graph/run/your-run-id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'connected') {
    console.log('Connected:', data.message);
  } else if (data.type === 'log') {
    console.log('Status:', data.status);
    data.logs.forEach(log => console.log(log));
  } else if (data.type === 'completed') {
    console.log('Completed:', data.status);
    console.log('Final state:', data.final_state);
    ws.close();
  }
};
```

---

## Data Models

### GraphDefinition

```typescript
{
  name: string;
  nodes: {
    [nodeName: string]: {
      tool: string;
      next: string | {
        condition: string;
        if_true: string;
        if_false: string;
      };
    };
  };
  start_node: string;
  max_iterations?: number; // default: 10
}
```

### WorkflowState

```typescript
{
  [key: string]: any; // Flexible schema
}
```

### ExecutionStatus

```typescript
enum ExecutionStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Graph not found | 404 | Invalid graph_id | Check graph_id is correct |
| Run not found | 404 | Invalid run_id | Check run_id is correct |
| Tool not found | 400 | Tool doesn't exist | Use /tools to list available tools |
| Invalid graph | 400 | Malformed definition | Check graph structure |
| Start node missing | 400 | start_node not in nodes | Add start_node to nodes |
| Execution failed | 500 | Runtime error | Check execution_log for details |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:

- Recommended: 100 requests/minute per IP
- Burst: 20 requests/second
- WebSocket: 10 concurrent connections per IP

---

## Best Practices

### 1. Graph Design

- Keep nodes focused (single responsibility)
- Use meaningful node names
- Set appropriate max_iterations
- Handle edge cases in conditions

### 2. State Management

- Use consistent key names
- Validate state in tools
- Keep state size reasonable (<1MB)
- Document expected state schema

### 3. Error Handling

- Check execution_log for debugging
- Handle tool errors gracefully
- Use try-except in custom tools
- Validate inputs before execution

### 4. Performance

- Avoid tight loops (use delays)
- Keep tool execution fast (<1s)
- Use WebSocket for long-running workflows
- Clean up old runs periodically

---

## Examples

### Complete Workflow Example

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Create graph
graph_response = requests.post(f"{BASE_URL}/graph/create", json={
    "name": "simple_review",
    "nodes": {
        "extract": {
            "tool": "extract_functions",
            "next": "evaluate"
        },
        "evaluate": {
            "tool": "evaluate_quality",
            "next": "end"
        }
    },
    "start_node": "extract"
})

graph_id = graph_response.json()["graph_id"]
print(f"Created graph: {graph_id}")

# 2. Run workflow
run_response = requests.post(f"{BASE_URL}/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {
        "code": "def test():\n    return 42",
        "quality_score": 0,
        "iteration": 0
    }
})

run_id = run_response.json()["run_id"]
print(f"Started run: {run_id}")

# 3. Poll for completion
while True:
    state_response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
    state = state_response.json()
    
    print(f"Status: {state['status']}")
    
    if state['status'] in ['completed', 'failed']:
        print(f"Final quality score: {state['current_state']['quality_score']}")
        break
    
    time.sleep(0.5)
```

---

## Interactive Documentation

For interactive API documentation with try-it-out functionality:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive request/response testing
- Schema documentation
- Example values
- Authentication testing (when enabled)
