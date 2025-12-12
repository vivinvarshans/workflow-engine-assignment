"""
Simple test script for the Workflow Engine API.

Run this after starting the server to verify everything works.
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")


def test_root():
    """Test root endpoint"""
    print("\nTesting / endpoint...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    print("✓ Root endpoint passed")


def test_list_tools():
    """Test tools listing"""
    print("\nTesting /tools endpoint...")
    response = requests.get(f"{BASE_URL}/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0
    print(f"✓ Found {len(data['tools'])} registered tools")


def test_create_graph():
    """Test graph creation"""
    print("\nTesting POST /graph/create...")
    
    graph_def = {
        "name": "test_workflow",
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
    }
    
    response = requests.post(f"{BASE_URL}/graph/create", json=graph_def)
    assert response.status_code == 200
    data = response.json()
    assert "graph_id" in data
    print(f"✓ Graph created with ID: {data['graph_id']}")
    return data["graph_id"]


def test_run_graph(graph_id):
    """Test graph execution"""
    print("\nTesting POST /graph/run...")
    
    initial_state = {
        "code": "def test():\n    return 42",
        "quality_score": 0,
        "iteration": 0
    }
    
    response = requests.post(
        f"{BASE_URL}/graph/run",
        json={
            "graph_id": graph_id,
            "initial_state": initial_state
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    print(f"✓ Workflow started with run_id: {data['run_id']}")
    return data["run_id"]


def test_get_state(run_id):
    """Test state retrieval"""
    print("\nTesting GET /graph/state/{run_id}...")
    
    # Wait for execution to complete
    max_attempts = 20
    for _ in range(max_attempts):
        response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
        assert response.status_code == 200
        data = response.json()
        
        if data["status"] in ["completed", "failed"]:
            print(f"✓ Workflow {data['status']}")
            print(f"  Final state keys: {list(data['current_state'].keys())}")
            print(f"  Execution log entries: {len(data['execution_log'])}")
            return data
        
        time.sleep(0.5)
    
    raise Exception("Workflow did not complete in time")


def test_invalid_graph():
    """Test error handling for invalid graph"""
    print("\nTesting error handling...")
    
    # Invalid graph (non-existent tool)
    graph_def = {
        "name": "invalid_workflow",
        "nodes": {
            "test": {
                "tool": "non_existent_tool",
                "next": "end"
            }
        },
        "start_node": "test"
    }
    
    response = requests.post(f"{BASE_URL}/graph/create", json=graph_def)
    assert response.status_code == 400
    print("✓ Invalid graph rejected correctly")


def test_invalid_run():
    """Test error handling for invalid run"""
    print("\nTesting invalid run...")
    
    response = requests.post(
        f"{BASE_URL}/graph/run",
        json={
            "graph_id": "non-existent-id",
            "initial_state": {}
        }
    )
    assert response.status_code == 404
    print("✓ Invalid graph_id rejected correctly")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Workflow Engine API Tests")
    print("=" * 60)
    
    try:
        # Check if server is running
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            print("\n✗ Cannot connect to API. Please start the server first:")
            print("  uvicorn app.main:app --reload")
            sys.exit(1)
        
        # Run tests
        test_health()
        test_root()
        test_list_tools()
        
        graph_id = test_create_graph()
        run_id = test_run_graph(graph_id)
        test_get_state(run_id)
        
        test_invalid_graph()
        test_invalid_run()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
