# Example API Requests

This folder contains example JSON files for testing the workflow engine API.

## Files

### Graph Creation

1. **create_simple_graph.json** - Simple linear workflow
   - Extracts functions and checks complexity
   
2. **create_code_review_graph.json** - Full code review workflow with loop
   - Complete analysis with iterative improvement

### Graph Execution

3. **run_simple_code.json** - Run with simple, clean code
   - Basic functions without issues
   
4. **run_problematic_code.json** - Run with code that has issues
   - Contains security issues, naming violations
   - Will trigger the loop in code review workflow

## Usage

### Using curl

1. **Create a graph:**
```bash
curl -X POST http://localhost:8000/graph/create \
  -H "Content-Type: application/json" \
  -d @examples/create_simple_graph.json
```

2. **Run the graph (replace GRAPH_ID):**
```bash
# First, update the graph_id in run_simple_code.json
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d @examples/run_simple_code.json
```

3. **Check run state (replace RUN_ID):**
```bash
curl http://localhost:8000/graph/state/RUN_ID
```

### Using Python

```python
import requests
import json

# Create graph
with open('examples/create_simple_graph.json') as f:
    graph_def = json.load(f)

response = requests.post('http://localhost:8000/graph/create', json=graph_def)
graph_id = response.json()['graph_id']
print(f"Created graph: {graph_id}")

# Run graph
with open('examples/run_simple_code.json') as f:
    run_request = json.load(f)
    run_request['graph_id'] = graph_id

response = requests.post('http://localhost:8000/graph/run', json=run_request)
result = response.json()
print(f"Run ID: {result['run_id']}")
print(f"Status: {result['status']}")
print(f"Final state: {result['final_state']}")
```

### Using Postman

1. Import the JSON files as request bodies
2. Set the method to POST
3. Set URL to `http://localhost:8000/graph/create` or `/graph/run`
4. Set Content-Type header to `application/json`
5. Send the request

## Workflow Comparison

| Workflow | Nodes | Edges | Loop | Branching | Best For |
|----------|-------|-------|------|-----------|----------|
| Simple | 3 | 2 | No | No | Quick analysis |
| Code Review | 6 | 6 | Yes | Yes | Full analysis |

## Tips

- Always create the graph before running it
- Save the returned `graph_id` to run the workflow
- The code review workflow requires `iteration: 0` in initial state
- Quality score threshold is 70 (can be modified in edges)
- Maximum 3 iterations to prevent infinite loops
