# Workflow Engine

A minimal workflow/graph engine similar to LangGraph, built with Python and FastAPI. This system allows you to define sequences of steps (nodes), connect them with edges, maintain shared state, and execute workflows end-to-end via REST APIs.

## Features

- ✅ **Node-based Workflow**: Define workflows as directed graphs with nodes and edges
- ✅ **Shared State Management**: State flows through the workflow and can be modified by each node
- ✅ **Conditional Branching**: Route execution based on state conditions
- ✅ **Loop Support**: Execute nodes repeatedly until conditions are met
- ✅ **Tool Registry**: Register and manage reusable Python functions as tools
- ✅ **REST API**: Complete FastAPI interface for creating and running workflows
- ✅ **Execution Logging**: Track workflow execution with detailed logs
- ✅ **In-Memory Storage**: Store graphs and run history

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── engine.py        # Core workflow engine (nodes, edges, execution)
│   ├── models.py        # Pydantic models for API requests/responses
│   ├── tools.py         # Tool registry and example tools
│   ├── storage.py       # In-memory storage for graphs and runs
│   └── workflows.py     # Example workflow definitions
├── test_workflow.py     # Test script with examples
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup

1. **Clone or navigate to the project directory**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### 1. Create a Graph
**POST** `/graph/create`

Create a new workflow graph with nodes and edges.

**Request Body:**
```json
{
  "name": "My Workflow",
  "description": "A sample workflow",
  "nodes": [
    {
      "name": "step1",
      "type": "function",
      "function_name": "extract_functions",
      "description": "Extract functions from code"
    }
  ],
  "edges": [
    {
      "from_node": "step1",
      "to_node": "step2",
      "type": "direct"
    }
  ],
  "start_node": "step1",
  "end_nodes": ["step3"]
}
```

**Response:**
```json
{
  "graph_id": "uuid-here",
  "name": "My Workflow",
  "status": "created",
  "node_count": 3,
  "edge_count": 2
}
```

#### 2. Run a Graph
**POST** `/graph/run`

Execute a workflow with an initial state.

**Request Body:**
```json
{
  "graph_id": "uuid-here",
  "initial_state": {
    "code": "def hello(): pass",
    "iteration": 0
  }
}
```

**Response:**
```json
{
  "run_id": "uuid-here",
  "graph_id": "uuid-here",
  "status": "completed",
  "final_state": {
    "code": "def hello(): pass",
    "functions": [...],
    "quality_score": 85
  },
  "execution_log": [...],
  "error": null
}
```

#### 3. Get Run State
**GET** `/graph/state/{run_id}`

Retrieve the current state of a workflow run.

#### 4. List Graphs
**GET** `/graphs`

List all created graphs.

#### 5. List Tools
**GET** `/tools`

List all registered tools/functions.

### Running the Example

The project includes a test script that demonstrates all features:

```bash
# Make sure the server is running first
python test_workflow.py
```

This will:
1. Create example workflows (simple, branching, and looping)
2. Execute them with different inputs
3. Show execution logs and final states

## Example Workflows

### 1. Code Review Workflow (With Loop)

This workflow analyzes code quality iteratively:

```
extract_functions → check_complexity → detect_issues → suggest_improvements → increment_iteration
                                                                                      ↓
                                                                           quality >= 70? → end
                                                                                      ↓ no
                                                                           ← back to complexity
```

**Features:**
- Extracts functions from code
- Checks complexity metrics
- Detects code issues (naming, security, style)
- Suggests improvements
- Loops until quality score ≥ 70 or 3 iterations

**Sample Usage:**
```python
initial_state = {
    "code": """
def risky_function(code):
    try:
        result = eval(code)
    except:
        result = None
    return result
    """,
    "iteration": 0
}
```

### 2. Simple Linear Workflow

Basic sequential execution:
```
extract_functions → check_complexity → end
```

### 3. Branching Workflow

Conditional routing based on complexity:
```
extract_functions → check_complexity → detect_issues (if complex) → end
                                    → end (if simple)
```

## Core Concepts

### Nodes
Nodes are the building blocks of workflows. Each node:
- Has a unique name
- Executes a registered tool/function
- Receives the current state
- Can modify and return state updates

### Edges
Edges connect nodes and define execution flow:
- **Direct edges**: Always traverse to the next node
- **Conditional edges**: Only traverse if a condition evaluates to true

Conditions are Python expressions evaluated against the state:
```python
"quality_score >= 70"
"average_complexity > 5"
"iteration < 3"
```

### State
State is a dictionary that flows through the workflow:
- Each node receives the current state
- Nodes can read from and write to state
- State changes are tracked in execution logs

### Tools
Tools are Python functions that perform workflow operations:
```python
def my_tool(state: WorkflowState) -> Dict[str, Any]:
    # Read from state
    value = state.get('some_key')
    
    # Process...
    result = process(value)
    
    # Return updates to state
    return {'result': result}
```

Register tools in `app/tools.py`:
```python
tool_registry.register('my_tool', my_tool)
```

## Built-in Tools

The system includes several pre-registered tools for code analysis:

1. **extract_functions**: Extract function definitions from Python code
2. **check_complexity**: Calculate cyclomatic complexity
3. **detect_issues**: Find common code issues (security, style, naming)
4. **suggest_improvements**: Generate improvement suggestions
5. **increment_iteration**: Increment loop counter
6. **pass_through**: No-op node (useful for end nodes)
7. **log_state**: Debug tool to print current state

## What the Engine Supports

### ✅ Implemented Features

- Node execution with custom functions
- State management and flow
- Direct edges between nodes
- Conditional edges with expression evaluation
- Loop detection and max iteration limits
- Execution logging with timestamps
- Error handling and reporting
- In-memory storage
- RESTful API with FastAPI
- Multiple workflow support
- Run history tracking

### 🚀 Potential Improvements

With more time, the following features could be added:

1. **Persistence**
   - SQLite/PostgreSQL database storage
   - Save/load workflows from files
   - Persistent run history

2. **Advanced Execution**
   - Async/await support for long-running tasks
   - Background task execution with Celery
   - Parallel node execution for independent branches
   - Priority-based execution

3. **WebSocket Support**
   - Real-time execution streaming
   - Live state updates
   - Progress notifications

4. **Enhanced Workflow Features**
   - Sub-workflows (call one workflow from another)
   - Dynamic graph modification during execution
   - Rollback/retry mechanisms
   - Checkpoint and resume

5. **Monitoring & Observability**
   - Metrics collection (execution time, success rate)
   - Performance profiling
   - Detailed error tracking
   - Workflow visualization

6. **Security & Auth**
   - API authentication
   - User-specific workflows
   - Rate limiting
   - Input validation and sanitization

7. **Developer Experience**
   - Web UI for graph creation
   - Visual workflow editor
   - Step-through debugger
   - Hot reload for tool changes

8. **Testing & Validation**
   - Workflow validation before execution
   - Unit test framework for nodes
   - Mock state for testing
   - Integration test suite

## Architecture

### Engine Flow

```
1. Graph Creation
   ↓
2. Tool Registry Lookup
   ↓
3. Node & Edge Initialization
   ↓
4. Execution Starts at Start Node
   ↓
5. For Each Node:
   - Save state snapshot
   - Execute node function
   - Update state
   - Log execution
   - Evaluate outgoing edges
   - Select next node
   ↓
6. Continue Until:
   - End node reached
   - No more edges
   - Max iterations hit
   - Error occurs
   ↓
7. Return final state + logs
```

### Key Classes

- **WorkflowState**: Manages state data and history
- **Node**: Wraps a tool function for execution
- **Edge**: Defines connections with optional conditions
- **WorkflowEngine**: Orchestrates node execution
- **Graph**: Complete workflow definition
- **ToolRegistry**: Manages available tools
- **Storage**: Handles persistence

## Example: Creating a Custom Workflow

### 1. Define Your Tools

```python
# In app/tools.py

def process_data(state: WorkflowState) -> Dict[str, Any]:
    data = state.get('data', [])
    processed = [x * 2 for x in data]
    return {'processed_data': processed}

def validate_result(state: WorkflowState) -> Dict[str, Any]:
    result = state.get('processed_data', [])
    is_valid = len(result) > 0
    return {'is_valid': is_valid}

# Register tools
tool_registry.register('process_data', process_data)
tool_registry.register('validate_result', validate_result)
```

### 2. Define Workflow

```python
workflow = {
    "name": "Data Processing",
    "nodes": [
        {"name": "process", "function_name": "process_data"},
        {"name": "validate", "function_name": "validate_result"},
        {"name": "end", "function_name": "pass_through"}
    ],
    "edges": [
        {"from_node": "process", "to_node": "validate"},
        {"from_node": "validate", "to_node": "end"}
    ],
    "start_node": "process",
    "end_nodes": ["end"]
}
```

### 3. Execute via API

```python
# Create graph
response = requests.post(
    "http://localhost:8000/graph/create",
    json=workflow
)
graph_id = response.json()['graph_id']

# Run graph
response = requests.post(
    "http://localhost:8000/graph/run",
    json={
        "graph_id": graph_id,
        "initial_state": {"data": [1, 2, 3, 4, 5]}
    }
)
print(response.json()['final_state'])
# Output: {'data': [1,2,3,4,5], 'processed_data': [2,4,6,8,10], 'is_valid': True}
```

## Testing

The project includes a comprehensive test script:

```bash
python test_workflow.py
```

This demonstrates:
- Simple linear workflows
- Conditional branching
- Iterative loops with exit conditions
- State management
- Error handling

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type hints

See `requirements.txt` for specific versions.

## Contributing

To extend the workflow engine:

1. **Add new tools**: Register functions in `app/tools.py`
2. **Create workflows**: Define graph structures in `app/workflows.py`
3. **Extend the engine**: Modify `app/engine.py` for new features
4. **Add endpoints**: Extend `app/main.py` with new API routes

## License

This project is provided as-is for educational and evaluation purposes.

## Contact

For questions or feedback about this implementation, please refer to the project documentation.

---

**Built with Python, FastAPI, and clean architecture principles.**
