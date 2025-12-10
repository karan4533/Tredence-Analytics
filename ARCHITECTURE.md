# Architecture Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│                         (main.py)                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Endpoints                                            │  │
│  │  • POST /graph/create                                │  │
│  │  • POST /graph/run                                   │  │
│  │  • GET /graph/state/{run_id}                         │  │
│  │  • GET /graphs                                       │  │
│  │  • GET /tools                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│   Storage    │        │     Models   │
│ (storage.py) │        │  (models.py) │
│              │        │              │
│ • Graphs     │        │ • GraphDef   │
│ • Runs       │        │ • Request    │
│ • History    │        │ • Response   │
└──────────────┘        └──────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│          Workflow Engine (engine.py)         │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  WorkflowEngine                        │ │
│  │  • nodes: Dict[str, Node]              │ │
│  │  • edges: List[Edge]                   │ │
│  │  • run() → (state, log, error)         │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────┐  ┌────────────┐            │
│  │    Node    │  │    Edge    │            │
│  │  • name    │  │  • from    │            │
│  │  • func    │  │  • to      │            │
│  │  • exec()  │  │  • cond    │            │
│  └────────────┘  └────────────┘            │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  WorkflowState                         │ │
│  │  • data: Dict[str, Any]                │ │
│  │  • history: List[Dict]                 │ │
│  │  • get(), set(), update()              │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│          Tool Registry (tools.py)            │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  ToolRegistry                          │ │
│  │  • tools: Dict[str, Callable]          │ │
│  │  • register(), get_tool()              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Registered Tools:                           │
│  • extract_functions                         │
│  • check_complexity                          │
│  • detect_issues                             │
│  • suggest_improvements                      │
│  • increment_iteration                       │
│  • pass_through                              │
└─────────────────────────────────────────────┘
```

## Workflow Execution Flow

```
1. Client Request
   │
   ▼
2. POST /graph/create
   │
   ├─► Parse GraphDefinition
   ├─► Lookup tools in ToolRegistry
   ├─► Create Nodes and Edges
   ├─► Build WorkflowEngine
   ├─► Save to Storage
   │
   └─► Return graph_id

3. POST /graph/run
   │
   ├─► Load Graph from Storage
   ├─► Initialize WorkflowState with initial_state
   │
   ├─► Start Execution Loop:
   │   │
   │   ├─► Execute current node
   │   ├─► Update state
   │   ├─► Log execution
   │   ├─► Evaluate outgoing edges
   │   ├─► Select next node (conditional routing)
   │   │
   │   └─► Repeat until:
   │       • End node reached
   │       • No more edges
   │       • Max iterations hit
   │       • Error occurs
   │
   ├─► Save run to Storage
   │
   └─► Return final_state + execution_log
```

## Example: Code Review Workflow

```
                    Start
                      │
                      ▼
            ┌─────────────────┐
            │  extract_funcs  │
            │                 │
            │ Input: code     │
            │ Output: funcs   │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
      ┌────►│ check_complex   │
      │     │                 │
      │     │ Input: funcs    │
      │     │ Output: scores  │
      │     └────────┬────────┘
      │              │
      │              ▼
      │     ┌─────────────────┐
      │     │ detect_issues   │
      │     │                 │
      │     │ Input: code     │
      │     │ Output: issues  │
      │     └────────┬────────┘
      │              │
      │              ▼
      │     ┌─────────────────┐
      │     │ suggest_improve │
      │     │                 │
      │     │ Calc: quality   │
      │     │ score           │
      │     └────────┬────────┘
      │              │
      │              ▼
      │     ┌─────────────────┐
      │     │  increment_iter │
      │     │                 │
      │     │ iteration += 1  │
      │     └────────┬────────┘
      │              │
      │              ▼
      │        ┌─────────┐
      │        │ Check:  │
      │        │ quality │
      │        │ >= 70?  │
      │        └────┬────┘
      │             │
      │    No       │       Yes
      │ (iterate<3) │
      │             │
      └─────────────┤
                    │
                    ▼
               ┌────────┐
               │  End   │
               └────────┘
```

## State Flow Example

```
Initial State:
{
  "code": "def func(): ...",
  "iteration": 0
}
        │
        ▼ extract_functions
{
  "code": "def func(): ...",
  "iteration": 0,
  "functions": [...],
  "function_count": 2
}
        │
        ▼ check_complexity
{
  ...,
  "complexity_scores": [...],
  "average_complexity": 5.5,
  "high_complexity_count": 1
}
        │
        ▼ detect_issues
{
  ...,
  "issues": [...],
  "issue_count": 3,
  "high_severity_count": 1
}
        │
        ▼ suggest_improvements
{
  ...,
  "suggestions": [...],
  "quality_score": 55
}
        │
        ▼ increment_iteration
{
  ...,
  "iteration": 1
}
        │
        ▼ [Loop or End?]
```

## Edge Types

### Direct Edge
```
[Node A] ───────► [Node B]
         Always
         traverse
```

### Conditional Edge
```
[Node A] ───┬───► [Node B]
            │     (if condition true)
            │
            └───► [Node C]
                  (if condition false)
```

### Loop Edge
```
[Node A] ───────► [Node B]
   ▲                 │
   │                 │
   │                 ▼
   │            ┌─────────┐
   └────────────│ Check   │
         (loop) │ cond.   │
                └─────────┘
                     │
                     │ (exit)
                     ▼
                 [Node C]
```

## Request/Response Flow

```
Client                Server              Engine              Storage
  │                     │                   │                    │
  │ POST /graph/create  │                   │                    │
  ├────────────────────►│                   │                    │
  │                     │ Create Graph      │                    │
  │                     ├──────────────────►│                    │
  │                     │                   │ Validate nodes     │
  │                     │                   │ Build edges        │
  │                     │◄──────────────────┤                    │
  │                     │ Save graph        │                    │
  │                     ├───────────────────────────────────────►│
  │                     │                   │                    │
  │  graph_id          │                   │                    │
  │◄────────────────────┤                   │                    │
  │                     │                   │                    │
  │ POST /graph/run     │                   │                    │
  ├────────────────────►│                   │                    │
  │                     │ Get graph         │                    │
  │                     ├───────────────────────────────────────►│
  │                     │◄───────────────────────────────────────┤
  │                     │ graph             │                    │
  │                     │                   │                    │
  │                     │ Run workflow      │                    │
  │                     ├──────────────────►│                    │
  │                     │                   │ Execute nodes      │
  │                     │                   │ Track state        │
  │                     │                   │ Log execution      │
  │                     │◄──────────────────┤                    │
  │                     │ state, log        │                    │
  │                     │                   │                    │
  │                     │ Save run          │                    │
  │                     ├───────────────────────────────────────►│
  │                     │                   │                    │
  │  run_id, state, log │                   │                    │
  │◄────────────────────┤                   │                    │
  │                     │                   │                    │
```

## Component Dependencies

```
main.py (FastAPI)
  ├─► models.py (Pydantic models)
  ├─► storage.py (In-memory storage)
  │     └─► engine.py (Graph)
  ├─► engine.py (Workflow execution)
  │     ├─► WorkflowEngine
  │     ├─► WorkflowState
  │     ├─► Node
  │     ├─► Edge
  │     └─► Graph
  └─► tools.py (Tool registry)
        └─► ToolRegistry
              └─► tool functions
```

## Tool Function Pattern

```python
def tool_function(state: WorkflowState) -> Dict[str, Any]:
    """
    Standard tool function signature
    
    Args:
        state: Current workflow state
        
    Returns:
        Dictionary of state updates
    """
    # 1. Read from state
    input_data = state.get('key', default_value)
    
    # 2. Process
    result = process(input_data)
    
    # 3. Return updates
    return {
        'output_key': result,
        'metadata': {...}
    }
```

## Key Algorithms

### 1. Graph Traversal
```
function run(initial_state):
    state = WorkflowState(initial_state)
    current = start_node
    
    while current is not None:
        # Execute node
        result = current.execute(state)
        state.update(result)
        
        # Find next node
        edges = get_outgoing_edges(current)
        next_nodes = []
        
        for edge in edges:
            if edge.condition(state):
                next_nodes.append(edge.to_node)
        
        if len(next_nodes) == 0:
            break
            
        current = next_nodes[0]  # Take first match
    
    return state
```

### 2. Condition Evaluation
```
function evaluate_condition(expr, state):
    # Convert string to function
    # e.g., "quality_score >= 70"
    
    try:
        result = eval(expr, {"__builtins__": {}}, state.data)
        return bool(result)
    except:
        return False
```

### 3. Loop Detection
```
function run_with_loop_detection(initial_state):
    max_iterations = 100
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Execute next node
        # ...
        
        if at_end_node:
            break
    
    if iteration >= max_iterations:
        raise LoopError("Max iterations exceeded")
```
