"""
FastAPI application for the Workflow Engine.
Provides REST API endpoints for creating and executing workflow graphs.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid
import json
import asyncio
import logging
from datetime import datetime

from app.models import (
    GraphDefinition,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    GraphStateResponse,
    ExecutionStatus
)
from app.database import DatabaseOperations, RunDB
from app.engine import WorkflowManager
from app.tools import tool_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Workflow Engine API",
    description="A minimal yet powerful workflow/graph engine for building agent workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time log streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, run_id: str, websocket: WebSocket):
        """Accept and store a WebSocket connection"""
        await websocket.accept()
        self.active_connections[run_id] = websocket
        logger.info(f"WebSocket connected for run_id: {run_id}")
    
    def disconnect(self, run_id: str):
        """Remove a WebSocket connection"""
        if run_id in self.active_connections:
            del self.active_connections[run_id]
            logger.info(f"WebSocket disconnected for run_id: {run_id}")
    
    async def send_log(self, run_id: str, message: str):
        """Send a log message to a specific connection"""
        if run_id in self.active_connections:
            try:
                await self.active_connections[run_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {run_id}: {e}")
                self.disconnect(run_id)

manager = ConnectionManager()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
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
        "registered_tools": tool_registry.list_tools()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(graph_def: GraphDefinition):
    """
    Create a new workflow graph.
    
    Args:
        graph_def: Graph definition with nodes, edges, and configuration
        
    Returns:
        Graph ID and success message
    """
    try:
        # Validate that start node exists
        if graph_def.start_node not in graph_def.nodes:
            raise HTTPException(
                status_code=400,
                detail=f"Start node '{graph_def.start_node}' not found in nodes"
            )
        
        # Validate that all tools exist
        for node_name, node_config in graph_def.nodes.items():
            tool_name = node_config.tool
            try:
                tool_registry.get(tool_name)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tool '{tool_name}' not found in registry for node '{node_name}'"
                )
        
        # Generate unique graph ID
        graph_id = str(uuid.uuid4())
        
        # Store in database
        DatabaseOperations.create_graph(
            graph_id=graph_id,
            name=graph_def.name,
            definition=graph_def.model_dump()
        )
        
        logger.info(f"Created graph '{graph_def.name}' with ID: {graph_id}")
        
        return GraphCreateResponse(graph_id=graph_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_workflow_background(
    graph_def: GraphDefinition,
    initial_state: Dict[str, Any],
    run_id: str
):
    """
    Background task to execute a workflow.
    
    Args:
        graph_def: Graph definition
        initial_state: Initial state for execution
        run_id: Unique run identifier
    """
    try:
        await WorkflowManager.execute_workflow(
            graph_definition=graph_def,
            initial_state=initial_state,
            run_id=run_id
        )
    except Exception as e:
        logger.error(f"Background workflow execution failed for run {run_id}: {e}")


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(
    request: GraphRunRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a workflow graph with the given initial state.
    
    Args:
        request: Contains graph_id and initial_state
        background_tasks: FastAPI background tasks
        
    Returns:
        Run ID and execution status
    """
    try:
        # Retrieve graph from database
        graph_db = DatabaseOperations.get_graph(request.graph_id)
        if not graph_db:
            raise HTTPException(
                status_code=404,
                detail=f"Graph with ID '{request.graph_id}' not found"
            )
        
        # Parse graph definition
        graph_def_dict = json.loads(graph_db.definition)
        graph_def = GraphDefinition(**graph_def_dict)
        
        # Generate unique run ID
        run_id = str(uuid.uuid4())
        
        # Create run record in database
        DatabaseOperations.create_run(
            run_id=run_id,
            graph_id=request.graph_id,
            initial_state=request.initial_state
        )
        
        # Execute workflow in background
        background_tasks.add_task(
            execute_workflow_background,
            graph_def,
            request.initial_state,
            run_id
        )
        
        logger.info(f"Started workflow execution with run_id: {run_id}")
        
        return GraphRunResponse(
            run_id=run_id,
            status=ExecutionStatus.RUNNING
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=GraphStateResponse)
async def get_graph_state(run_id: str):
    """
    Get the current state and execution log of a workflow run.
    
    Args:
        run_id: Unique run identifier
        
    Returns:
        Current state, status, and execution log
    """
    try:
        # Retrieve run from database
        run_db = DatabaseOperations.get_run(run_id)
        if not run_db:
            raise HTTPException(
                status_code=404,
                detail=f"Run with ID '{run_id}' not found"
            )
        
        # Parse JSON fields
        current_state = json.loads(run_db.current_state)
        execution_log = json.loads(run_db.execution_log)
        
        return GraphStateResponse(
            run_id=run_id,
            status=run_db.status,
            current_state=current_state,
            execution_log=execution_log,
            error=run_db.error,
            started_at=run_db.started_at,
            completed_at=run_db.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving run state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/graph/run/{run_id}")
async def websocket_graph_run(websocket: WebSocket, run_id: str):
    """
    WebSocket endpoint for real-time workflow execution logs.
    
    Args:
        websocket: WebSocket connection
        run_id: Unique run identifier
    """
    await manager.connect(run_id, websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "run_id": run_id,
            "message": "WebSocket connected"
        })
        
        # Keep connection alive and stream logs
        while True:
            # Check run status periodically
            run_db = DatabaseOperations.get_run(run_id)
            if run_db:
                execution_log = json.loads(run_db.execution_log)
                
                # Send latest logs
                await websocket.send_json({
                    "type": "log",
                    "run_id": run_id,
                    "status": run_db.status.value,
                    "logs": execution_log
                })
                
                # If completed or failed, send final message and close
                if run_db.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                    await websocket.send_json({
                        "type": "completed",
                        "run_id": run_id,
                        "status": run_db.status.value,
                        "final_state": json.loads(run_db.current_state)
                    })
                    break
            
            await asyncio.sleep(0.5)  # Poll every 500ms
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for run_id: {run_id}")
    except Exception as e:
        logger.error(f"WebSocket error for run_id {run_id}: {e}")
    finally:
        manager.disconnect(run_id)


@app.get("/tools")
async def list_tools():
    """List all registered tools"""
    return {
        "tools": tool_registry.list_tools(),
        "count": len(tool_registry.list_tools())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
