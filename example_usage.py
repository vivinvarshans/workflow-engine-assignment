"""
Example usage of the Workflow Engine API.

This script demonstrates how to:
1. Create a workflow graph
2. Execute the workflow
3. Monitor execution status
4. Retrieve final results
"""

import requests
import time
import json
from app.workflows.code_review import (
    get_code_review_graph_definition,
    get_sample_initial_state,
    SAMPLE_CODE_BAD,
    SAMPLE_CODE_GOOD,
    SAMPLE_CODE_MODERATE
)

# API base URL
BASE_URL = "http://localhost:8000"


def create_code_review_workflow():
    """Create the code review workflow graph"""
    print("=" * 60)
    print("Creating Code Review Workflow")
    print("=" * 60)
    
    graph_def = get_code_review_graph_definition()
    
    response = requests.post(
        f"{BASE_URL}/graph/create",
        json=graph_def
    )
    
    if response.status_code == 200:
        result = response.json()
        graph_id = result["graph_id"]
        print(f"✓ Graph created successfully!")
        print(f"  Graph ID: {graph_id}")
        print(f"  Name: {graph_def['name']}")
        print(f"  Nodes: {len(graph_def['nodes'])}")
        return graph_id
    else:
        print(f"✗ Error creating graph: {response.text}")
        return None


def run_workflow(graph_id: str, code_sample: str, sample_name: str):
    """Execute a workflow with the given code sample"""
    print("\n" + "=" * 60)
    print(f"Running Workflow: {sample_name}")
    print("=" * 60)
    
    initial_state = get_sample_initial_state(code_sample)
    
    print(f"\nCode to review ({len(code_sample)} characters):")
    print("-" * 60)
    print(code_sample[:200] + "..." if len(code_sample) > 200 else code_sample)
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/graph/run",
        json={
            "graph_id": graph_id,
            "initial_state": initial_state
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        run_id = result["run_id"]
        print(f"\n✓ Workflow execution started!")
        print(f"  Run ID: {run_id}")
        print(f"  Status: {result['status']}")
        return run_id
    else:
        print(f"\n✗ Error starting workflow: {response.text}")
        return None


def monitor_execution(run_id: str):
    """Monitor workflow execution until completion"""
    print("\n" + "-" * 60)
    print("Monitoring Execution...")
    print("-" * 60)
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
        
        if response.status_code == 200:
            result = response.json()
            status = result["status"]
            
            print(f"\rStatus: {status} | Iteration: {result['current_state'].get('iteration', 0)}", end="")
            
            if status in ["completed", "failed"]:
                print()  # New line
                return result
        
        time.sleep(0.5)
        attempt += 1
    
    print("\n✗ Timeout waiting for workflow completion")
    return None


def display_results(result: dict):
    """Display the final workflow results"""
    print("\n" + "=" * 60)
    print("Workflow Results")
    print("=" * 60)
    
    status = result["status"]
    state = result["current_state"]
    
    print(f"\nStatus: {status}")
    print(f"Quality Score: {state.get('quality_score', 0)}/10")
    print(f"Iterations: {state.get('iteration', 0)}")
    
    # Display functions found
    functions = state.get("functions", [])
    print(f"\n📋 Functions Found: {len(functions)}")
    for func in functions:
        if "name" in func:
            print(f"  - {func['name']} ({func.get('num_lines', 0)} lines)")
    
    # Display complexity scores
    complexity = state.get("complexity_scores", {})
    if complexity:
        print(f"\n🔢 Complexity Scores:")
        for func_name, score in complexity.items():
            level = "Low" if score <= 5 else "Medium" if score <= 10 else "High"
            print(f"  - {func_name}: {score} ({level})")
    
    # Display issues
    issues = state.get("issues", [])
    if issues:
        print(f"\n⚠️  Issues Found: {len(issues)}")
        for issue in issues[:5]:  # Show first 5
            severity = issue.get("severity", "unknown")
            message = issue.get("message", "No message")
            print(f"  [{severity.upper()}] {message}")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")
    
    # Display suggestions
    suggestions = state.get("suggestions", [])
    if suggestions:
        print(f"\n💡 Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    # Display execution log summary
    logs = result.get("execution_log", [])
    print(f"\n📝 Execution Log: {len(logs)} entries")
    if logs:
        print(f"  First: {logs[0]}")
        print(f"  Last:  {logs[-1]}")
    
    print("\n" + "=" * 60)


def main():
    """Main execution flow"""
    print("\n" + "=" * 60)
    print("Workflow Engine - Example Usage")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("✗ API is not responding. Please start the server first:")
            print("  uvicorn app.main:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Please start the server first:")
        print("  uvicorn app.main:app --reload")
        return
    
    print("✓ API is running\n")
    
    # Create workflow
    graph_id = create_code_review_workflow()
    if not graph_id:
        return
    
    # Test with different code samples
    samples = [
        (SAMPLE_CODE_GOOD, "Good Quality Code"),
        (SAMPLE_CODE_MODERATE, "Moderate Quality Code"),
        (SAMPLE_CODE_BAD, "Poor Quality Code"),
    ]
    
    for code_sample, sample_name in samples:
        # Run workflow
        run_id = run_workflow(graph_id, code_sample, sample_name)
        if not run_id:
            continue
        
        # Monitor execution
        result = monitor_execution(run_id)
        if result:
            display_results(result)
        
        # Wait before next sample
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - View API docs: http://localhost:8000/docs")
    print("  - Check database: workflow_engine.db")
    print("  - Try WebSocket: ws://localhost:8000/ws/graph/run/{run_id}")
    print()


if __name__ == "__main__":
    main()
