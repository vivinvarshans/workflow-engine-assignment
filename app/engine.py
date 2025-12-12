"""
Core workflow engine for executing graphs.
Supports nodes, edges, state management, conditional branching, and looping.
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
from datetime import datetime
from app.models import ExecutionStatus, GraphDefinition
from app.tools import tool_registry
from app.database import DatabaseOperations
import logging

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Core engine for executing workflow graphs.
    
    Features:
    - Sequential node execution
    - Conditional branching based on state
    - Loop detection and prevention
    - State management
    - Execution logging
    """
    
    def __init__(self, graph_definition: GraphDefinition):
        self.graph = graph_definition
        self.execution_log: List[str] = []
        self.max_iterations = graph_definition.max_iterations
    
    def log(self, message: str):
        """Add a message to the execution log"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        logger.info(message)
    
    def evaluate_condition(self, condition: str, state: Dict[str, Any]) -> bool:
        """
        Evaluate a conditional expression against the current state.
        
        Args:
            condition: Python expression as string (e.g., "quality_score >= 7")
            state: Current workflow state
            
        Returns:
            Boolean result of the condition
        """
        try:
            # Create a safe evaluation context with only the state variables
            eval_context = {k: v for k, v in state.items() if isinstance(k, str)}
            result = eval(condition, {"__builtins__": {}}, eval_context)
            return bool(result)
        except Exception as e:
            self.log(f"Error evaluating condition '{condition}': {str(e)}")
            return False
    
    def get_next_node(
        self, 
        current_node: str, 
        state: Dict[str, Any]
    ) -> Optional[str]:
        """
        Determine the next node to execute based on current node configuration.
        
        Args:
            current_node: Name of the current node
            state: Current workflow state
            
        Returns:
            Name of the next node, or None if workflow should end
        """
        node_config = self.graph.nodes.get(current_node)
        if not node_config:
            return None
        
        next_config = node_config.next
        
        # Simple string next node
        if isinstance(next_config, str):
            return next_config if next_config != "end" else None
        
        # Conditional routing
        if isinstance(next_config, dict):
            condition = next_config.get("condition")
            if_true = next_config.get("if_true")
            if_false = next_config.get("if_false")
            
            if condition:
                result = self.evaluate_condition(condition, state)
                self.log(f"Condition '{condition}' evaluated to: {result}")
                
                next_node = if_true if result else if_false
                return next_node if next_node != "end" else None
        
        return None
    
    def execute_node(
        self, 
        node_name: str, 
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single node by calling its associated tool.
        
        Args:
            node_name: Name of the node to execute
            state: Current workflow state
            
        Returns:
            Updated state after node execution
        """
        node_config = self.graph.nodes.get(node_name)
        if not node_config:
            raise ValueError(f"Node '{node_name}' not found in graph")
        
        tool_name = node_config.tool
        self.log(f"Executing node '{node_name}' with tool '{tool_name}'")
        
        try:
            tool_func = tool_registry.get(tool_name)
            updated_state = tool_func(state)
            self.log(f"Node '{node_name}' completed successfully")
            return updated_state
        except Exception as e:
            error_msg = f"Error in node '{node_name}': {str(e)}"
            self.log(error_msg)
            raise RuntimeError(error_msg) from e
    
    async def execute(
        self, 
        initial_state: Dict[str, Any],
        run_id: str
    ) -> Dict[str, Any]:
        """
        Execute the entire workflow graph.
        
        Args:
            initial_state: Starting state for the workflow
            run_id: Unique identifier for this execution run
            
        Returns:
            Final state after workflow completion
        """
        state = initial_state.copy()
        current_node = self.graph.start_node
        iteration_count = 0
        visited_nodes = []
        
        self.log(f"Starting workflow execution from node '{current_node}'")
        
        # Update run status to running
        DatabaseOperations.update_run(
            run_id=run_id,
            status=ExecutionStatus.RUNNING,
            current_state=state,
            execution_log=self.execution_log
        )
        
        try:
            while current_node and iteration_count < self.max_iterations:
                # Execute current node
                state = self.execute_node(current_node, state)
                visited_nodes.append(current_node)
                iteration_count += 1
                
                # Update database with current progress
                DatabaseOperations.update_run(
                    run_id=run_id,
                    current_state=state,
                    execution_log=self.execution_log
                )
                
                # Determine next node
                next_node = self.get_next_node(current_node, state)
                
                if next_node is None:
                    self.log("Workflow completed: reached end node")
                    break
                
                if next_node == current_node:
                    self.log(f"Loop detected: node '{current_node}' points to itself")
                
                self.log(f"Transitioning from '{current_node}' to '{next_node}'")
                current_node = next_node
                
                # Small delay to prevent tight loops
                await asyncio.sleep(0.1)
            
            if iteration_count >= self.max_iterations:
                self.log(
                    f"Workflow stopped: maximum iterations ({self.max_iterations}) reached"
                )
            
            self.log(f"Workflow execution completed. Visited {len(visited_nodes)} nodes")
            
            # Mark as completed
            DatabaseOperations.update_run(
                run_id=run_id,
                status=ExecutionStatus.COMPLETED,
                current_state=state,
                execution_log=self.execution_log,
                completed_at=datetime.utcnow()
            )
            
            return state
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            self.log(error_msg)
            
            # Mark as failed
            DatabaseOperations.update_run(
                run_id=run_id,
                status=ExecutionStatus.FAILED,
                current_state=state,
                execution_log=self.execution_log,
                error=error_msg,
                completed_at=datetime.utcnow()
            )
            
            raise


class WorkflowManager:
    """Manager for creating and executing workflows"""
    
    @staticmethod
    async def execute_workflow(
        graph_definition: GraphDefinition,
        initial_state: Dict[str, Any],
        run_id: str
    ) -> Dict[str, Any]:
        """
        Create an engine instance and execute a workflow.
        
        Args:
            graph_definition: The workflow graph to execute
            initial_state: Starting state
            run_id: Unique run identifier
            
        Returns:
            Final state after execution
        """
        engine = WorkflowEngine(graph_definition)
        return await engine.execute(initial_state, run_id)
