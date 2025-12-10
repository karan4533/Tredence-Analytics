"""
Test script to demonstrate the workflow engine
Run this after starting the FastAPI server
"""
import requests
import json
from app.workflows import (
    CODE_REVIEW_WORKFLOW, 
    SIMPLE_WORKFLOW, 
    BRANCHING_WORKFLOW,
    SAMPLE_CODE_SIMPLE,
    SAMPLE_CODE_COMPLEX,
    SAMPLE_CODE_WITH_ISSUES
)

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_list_tools():
    """Test listing available tools"""
    print("\n=== Listing Available Tools ===")
    response = requests.get(f"{BASE_URL}/tools")
    data = response.json()
    print(f"Available tools ({data['count']}):")
    for tool in data['tools']:
        print(f"  - {tool}")
    return response.status_code == 200


def test_create_graph(workflow_def):
    """Test creating a graph"""
    print(f"\n=== Creating Graph: {workflow_def['name']} ===")
    response = requests.post(f"{BASE_URL}/graph/create", json=workflow_def)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Graph created successfully!")
        print(f"  Graph ID: {data['graph_id']}")
        print(f"  Nodes: {data['node_count']}")
        print(f"  Edges: {data['edge_count']}")
        return data['graph_id']
    else:
        print(f"Failed to create graph: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def test_run_graph(graph_id, initial_state, description=""):
    """Test running a graph"""
    print(f"\n=== Running Graph {description} ===")
    print(f"Graph ID: {graph_id}")
    print(f"Initial state keys: {list(initial_state.keys())}")
    
    request = {
        "graph_id": graph_id,
        "initial_state": initial_state
    }
    
    response = requests.post(f"{BASE_URL}/graph/run", json=request)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nExecution completed!")
        print(f"  Run ID: {data['run_id']}")
        print(f"  Status: {data['status']}")
        print(f"  Steps executed: {len(data['execution_log'])}")
        
        if data.get('error'):
            print(f"  Error: {data['error']}")
        
        print(f"\nFinal State:")
        for key, value in data['final_state'].items():
            if isinstance(value, list):
                print(f"  {key}: [{len(value)} items]")
            elif isinstance(value, dict):
                print(f"  {key}: {{{len(value)} keys}}")
            else:
                print(f"  {key}: {value}")
        
        print(f"\nExecution Log:")
        for i, entry in enumerate(data['execution_log'], 1):
            print(f"  {i}. {entry['node_name']} @ {entry['timestamp']}")
            if entry.get('error'):
                print(f"     ERROR: {entry['error']}")
        
        return data['run_id']
    else:
        print(f"Failed to run graph: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def test_get_state(run_id):
    """Test getting run state"""
    print(f"\n=== Getting State for Run {run_id} ===")
    response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"State keys: {list(data['current_state'].keys())}")
        return True
    else:
        print(f"Failed to get state: {response.status_code}")
        return False


def test_list_graphs():
    """Test listing all graphs"""
    print("\n=== Listing All Graphs ===")
    response = requests.get(f"{BASE_URL}/graphs")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total graphs: {data['count']}")
        for graph in data['graphs']:
            print(f"  - {graph['name']} (ID: {graph['graph_id'][:8]}...)")
            print(f"    Nodes: {graph['node_count']}, Edges: {graph['edge_count']}")
        return True
    else:
        print(f"Failed to list graphs: {response.status_code}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("WORKFLOW ENGINE TEST SUITE")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\nERROR: Server is not running. Start it with:")
        print("  python -m uvicorn app.main:app --reload")
        return
    
    # Test list tools
    test_list_tools()
    
    # Test 1: Simple Linear Workflow
    print("\n" + "=" * 60)
    print("TEST 1: SIMPLE LINEAR WORKFLOW")
    print("=" * 60)
    graph_id = test_create_graph(SIMPLE_WORKFLOW)
    if graph_id:
        test_run_graph(graph_id, {"code": SAMPLE_CODE_SIMPLE}, "with simple code")
    
    # Test 2: Branching Workflow
    print("\n" + "=" * 60)
    print("TEST 2: BRANCHING WORKFLOW")
    print("=" * 60)
    graph_id = test_create_graph(BRANCHING_WORKFLOW)
    if graph_id:
        # Run with simple code (should skip detect issues)
        run_id = test_run_graph(graph_id, {"code": SAMPLE_CODE_SIMPLE}, "with simple code")
        if run_id:
            test_get_state(run_id)
        
        # Run with complex code (should detect issues)
        test_run_graph(graph_id, {"code": SAMPLE_CODE_COMPLEX}, "with complex code")
    
    # Test 3: Code Review Workflow with Loop
    print("\n" + "=" * 60)
    print("TEST 3: CODE REVIEW WORKFLOW (WITH LOOP)")
    print("=" * 60)
    graph_id = test_create_graph(CODE_REVIEW_WORKFLOW)
    if graph_id:
        # Run with code that has issues (will loop)
        run_id = test_run_graph(
            graph_id, 
            {"code": SAMPLE_CODE_WITH_ISSUES, "iteration": 0}, 
            "with problematic code"
        )
        
        if run_id:
            test_get_state(run_id)
    
    # List all graphs
    test_list_graphs()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server at http://localhost:8000")
        print("Please start the server first:")
        print("  python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
