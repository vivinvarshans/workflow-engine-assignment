"""
Pydantic models for API requests, responses, and workflow state.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ExecutionStatus(str, Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class NodeConfig(BaseModel):
    """Configuration for a single node in the workflow"""
    tool: str = Field(..., description="Name of the tool to execute")
    next: Union[str, Dict[str, Any]] = Field(
        ..., 
        description="Next node name or conditional routing config"
    )


class GraphDefinition(BaseModel):
    """Definition of a workflow graph"""
    name: str = Field(..., description="Name of the workflow")
    nodes: Dict[str, NodeConfig] = Field(..., description="Node configurations")
    start_node: str = Field(..., description="Starting node name")
    max_iterations: int = Field(
        default=10, 
        description="Maximum iterations to prevent infinite loops"
    )


class GraphCreateResponse(BaseModel):
    """Response after creating a graph"""
    graph_id: str
    message: str = "Graph created successfully"


class GraphRunRequest(BaseModel):
    """Request to run a workflow"""
    graph_id: str
    initial_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Initial state for the workflow"
    )


class GraphRunResponse(BaseModel):
    """Response after starting a workflow run"""
    run_id: str
    status: ExecutionStatus
    message: str = "Workflow execution started"


class GraphStateResponse(BaseModel):
    """Response containing the current state of a workflow run"""
    run_id: str
    status: ExecutionStatus
    current_state: Dict[str, Any]
    execution_log: List[str]
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowState(BaseModel):
    """Base class for workflow state - can be extended for specific workflows"""
    
    class Config:
        extra = "allow"  # Allow additional fields
        
    def dict(self, *args, **kwargs):
        """Override dict to include extra fields"""
        return super().model_dump(*args, **kwargs)


class CodeReviewState(WorkflowState):
    """State model for code review workflow"""
    code: str = Field(..., description="Source code to review")
    quality_score: int = Field(default=0, description="Quality score (0-10)")
    iteration: int = Field(default=0, description="Current iteration count")
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    complexity_scores: Dict[str, int] = Field(default_factory=dict)
    issues: List[Dict[str, str]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
