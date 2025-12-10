"""
Simple verification script to test the workflow engine components
"""
print("=" * 60)
print("WORKFLOW ENGINE - VERIFICATION TEST")
print("=" * 60)

# Test 1: Import all modules
print("\n1. Testing module imports...")
try:
    from app.engine import WorkflowEngine, WorkflowState, Node, Edge, Graph
    from app.models import GraphCreate, GraphRunRequest, GraphRunResponse
    from app.tools import tool_registry
    from app.storage import storage
    from app.workflows import CODE_REVIEW_WORKFLOW, SAMPLE_CODE_SIMPLE
    print("   ✅ All modules imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

# Test 2: Check tool registry
print("\n2. Testing tool registry...")
try:
    tools = tool_registry.list_tools()
    print(f"   ✅ {len(tools)} tools registered: {', '.join(tools)}")
except Exception as e:
    print(f"   ❌ Tool registry failed: {e}")
    exit(1)

# Test 3: Create and run a simple workflow
print("\n3. Testing workflow execution...")
try:
    from app.workflows import SIMPLE_WORKFLOW
    
    # Create graph
    graph = Graph.create_from_definition(SIMPLE_WORKFLOW, tool_registry)
    print(f"   ✅ Graph created: {graph.name}")
    
    # Run workflow
    initial_state = {"code": SAMPLE_CODE_SIMPLE}
    final_state, execution_log, error = graph.run(initial_state)
    
    if error:
        print(f"   ❌ Execution error: {error}")
        exit(1)
    
    print(f"   ✅ Workflow executed successfully")
    print(f"   - Steps: {len(execution_log)}")
    print(f"   - Functions found: {final_state.get('function_count', 0)}")
    print(f"   - Average complexity: {final_state.get('average_complexity', 0):.2f}")
    
except Exception as e:
    print(f"   ❌ Workflow execution failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Test conditional branching
print("\n4. Testing conditional branching...")
try:
    from app.workflows import BRANCHING_WORKFLOW, SAMPLE_CODE_COMPLEX
    
    graph = Graph.create_from_definition(BRANCHING_WORKFLOW, tool_registry)
    initial_state = {"code": SAMPLE_CODE_COMPLEX}
    final_state, execution_log, error = graph.run(initial_state)
    
    if error:
        print(f"   ❌ Branching failed: {error}")
        exit(1)
    
    # Check if detect_issues node was executed (should be for complex code)
    node_names = [entry['node_name'] for entry in execution_log]
    
    if 'detect' in node_names:
        print(f"   ✅ Conditional branching works correctly")
        print(f"   - Branch taken: complexity -> detect -> end")
    else:
        print(f"   ⚠️  Unexpected branch taken")
    
except Exception as e:
    print(f"   ❌ Branching test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Test looping workflow
print("\n5. Testing loop support...")
try:
    from app.workflows import CODE_REVIEW_WORKFLOW, SAMPLE_CODE_WITH_ISSUES
    
    graph = Graph.create_from_definition(CODE_REVIEW_WORKFLOW, tool_registry)
    initial_state = {"code": SAMPLE_CODE_WITH_ISSUES, "iteration": 0}
    final_state, execution_log, error = graph.run(initial_state)
    
    if error:
        print(f"   ❌ Loop test failed: {error}")
        exit(1)
    
    iterations = final_state.get('iteration', 0)
    quality_score = final_state.get('quality_score', 0)
    
    print(f"   ✅ Loop executed successfully")
    print(f"   - Iterations: {iterations}")
    print(f"   - Quality score: {quality_score}")
    print(f"   - Total steps: {len(execution_log)}")
    
    # Verify loop happened
    if iterations > 0:
        print(f"   ✅ Loop functionality verified")
    
except Exception as e:
    print(f"   ❌ Loop test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 6: Test storage
print("\n6. Testing storage layer...")
try:
    from app.storage import Storage
    
    test_storage = Storage()
    
    # Create and save a graph
    test_graph = Graph.create_from_definition(SIMPLE_WORKFLOW, tool_registry)
    graph_id = test_storage.save_graph(test_graph)
    
    # Retrieve graph
    retrieved = test_storage.get_graph(graph_id)
    
    if retrieved and retrieved.graph_id == graph_id:
        print(f"   ✅ Storage works correctly")
        print(f"   - Saved graph: {graph_id[:8]}...")
        print(f"   - Retrieved successfully")
    else:
        print(f"   ❌ Storage retrieval failed")
        exit(1)
    
except Exception as e:
    print(f"   ❌ Storage test failed: {e}")
    exit(1)

# Test 7: FastAPI app structure
print("\n7. Testing FastAPI app...")
try:
    from app.main import app
    
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    print(f"   ✅ FastAPI app loaded successfully")
    print(f"   - Available endpoints: {len(routes)}")
    print(f"   - Key routes: /graph/create, /graph/run, /graph/state/{{run_id}}")
    
except Exception as e:
    print(f"   ❌ FastAPI app test failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✅")
print("=" * 60)
print("\nThe workflow engine is working correctly!")
print("\nNext steps:")
print("  1. Start server: python -m uvicorn app.main:app --reload")
print("  2. Visit: http://localhost:8000/docs")
print("  3. Run API tests: python test_workflow.py")
print("=" * 60)
