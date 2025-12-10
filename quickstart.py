"""
Quick start script to run a simple example
"""
from app.engine import Graph, WorkflowState
from app.tools import tool_registry
from app.workflows import SIMPLE_WORKFLOW, SAMPLE_CODE_SIMPLE
import json


def main():
    print("=" * 60)
    print("WORKFLOW ENGINE - QUICK START EXAMPLE")
    print("=" * 60)
    
    # Create a graph
    print("\n1. Creating workflow graph...")
    graph = Graph.create_from_definition(SIMPLE_WORKFLOW, tool_registry)
    print(f"   Graph created: {graph.name}")
    print(f"   Nodes: {len(graph.engine.nodes)}")
    print(f"   Edges: {len(graph.engine.edges)}")
    
    # Prepare initial state
    print("\n2. Preparing initial state...")
    initial_state = {
        "code": SAMPLE_CODE_SIMPLE
    }
    print(f"   Code sample:")
    for line in SAMPLE_CODE_SIMPLE.strip().split('\n'):
        print(f"     {line}")
    
    # Run the workflow
    print("\n3. Executing workflow...")
    final_state, execution_log, error = graph.run(initial_state)
    
    # Display results
    print("\n4. Results:")
    if error:
        print(f"   ❌ Error: {error}")
    else:
        print(f"   ✅ Execution completed successfully")
    
    print(f"\n   Execution steps:")
    for i, entry in enumerate(execution_log, 1):
        print(f"     {i}. {entry['node_name']}")
    
    print(f"\n   Final state:")
    print(f"     - Functions found: {final_state.get('function_count', 0)}")
    print(f"     - Average complexity: {final_state.get('average_complexity', 0):.2f}")
    
    if final_state.get('functions'):
        print(f"\n   Extracted functions:")
        for func in final_state['functions']:
            print(f"     - {func['name']} (line {func['start_line']})")
    
    if final_state.get('complexity_scores'):
        print(f"\n   Complexity scores:")
        for score in final_state['complexity_scores']:
            status = "⚠️ Complex" if score['is_complex'] else "✅ Simple"
            print(f"     - {score['function']}: {score['complexity']} {status}")
    
    print("\n" + "=" * 60)
    print("Example completed! Now try:")
    print("  1. Start the API server: uvicorn app.main:app --reload")
    print("  2. Run tests: python test_workflow.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
