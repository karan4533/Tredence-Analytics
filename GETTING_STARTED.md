# Getting Started Guide

Welcome! This guide will help you get the workflow engine up and running in minutes.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

Check your Python version:
```bash
python --version
```

## 🚀 Quick Start (3 Minutes)

### Step 1: Install Dependencies (30 seconds)

```bash
# Navigate to project directory
cd "Tredence Analytics"

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Installation (30 seconds)

```bash
# Run verification tests
python verify.py
```

You should see:
```
ALL TESTS PASSED ✅
```

### Step 3: Try the Quick Demo (30 seconds)

```bash
# Run a simple workflow example
python quickstart.py
```

### Step 4: Start the API Server (30 seconds)

```bash
# Start the FastAPI server
python -m uvicorn app.main:app --reload
```

Server will start at: `http://localhost:8000`

### Step 5: Explore the API (1 minute)

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 What's Next?

### Option A: Try the Interactive API (Recommended for beginners)

1. Go to http://localhost:8000/docs
2. Click on **POST /graph/create**
3. Click "Try it out"
4. Use this example:

```json
{
  "name": "My First Workflow",
  "description": "Simple function extraction",
  "nodes": [
    {
      "name": "extract",
      "type": "function",
      "function_name": "extract_functions",
      "description": "Extract functions"
    },
    {
      "name": "end",
      "type": "function",
      "function_name": "pass_through",
      "description": "End"
    }
  ],
  "edges": [
    {
      "from_node": "extract",
      "to_node": "end",
      "type": "direct"
    }
  ],
  "start_node": "extract",
  "end_nodes": ["end"]
}
```

5. Click "Execute"
6. Copy the returned `graph_id`
7. Try **POST /graph/run** with:

```json
{
  "graph_id": "PASTE_YOUR_GRAPH_ID_HERE",
  "initial_state": {
    "code": "def hello():\n    return 'world'\n"
  }
}
```

### Option B: Run Comprehensive Tests

```bash
# Make sure the server is running, then:
python test_workflow.py
```

This will:
- Create 3 different workflows
- Run them with various inputs
- Show execution logs and results

### Option C: Use curl Commands

```bash
# 1. List available tools
curl http://localhost:8000/tools

# 2. Create a graph
curl -X POST http://localhost:8000/graph/create \
  -H "Content-Type: application/json" \
  -d @examples/create_simple_graph.json

# 3. Run the graph (replace GRAPH_ID)
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{"graph_id":"GRAPH_ID","initial_state":{"code":"def test(): pass"}}'
```

### Option D: Python Script

```python
import requests

# Create graph
response = requests.post(
    'http://localhost:8000/graph/create',
    json={
        "name": "Test Workflow",
        "nodes": [
            {"name": "extract", "function_name": "extract_functions"},
            {"name": "end", "function_name": "pass_through"}
        ],
        "edges": [
            {"from_node": "extract", "to_node": "end"}
        ],
        "start_node": "extract",
        "end_nodes": ["end"]
    }
)
graph_id = response.json()['graph_id']

# Run graph
response = requests.post(
    'http://localhost:8000/graph/run',
    json={
        "graph_id": graph_id,
        "initial_state": {"code": "def hello(): pass"}
    }
)
print(response.json()['final_state'])
```

## 📖 Learn More

### Understanding the System

1. **Read the README**
   - `README.md` - Complete documentation
   - `PROJECT_SUMMARY.md` - Project overview
   - `ARCHITECTURE.md` - Technical diagrams

2. **Explore the Code**
   - `app/engine.py` - Core workflow engine
   - `app/tools.py` - Example tools
   - `app/main.py` - API endpoints

3. **Try Examples**
   - `examples/` - Pre-made requests
   - `app/workflows.py` - Workflow definitions
   - `quickstart.py` - Simple demo

## 🔧 Common Tasks

### Create a New Tool

Edit `app/tools.py`:

```python
def my_custom_tool(state: WorkflowState) -> Dict[str, Any]:
    """My custom processing"""
    input_value = state.get('input_key')
    result = process(input_value)
    return {'output_key': result}

# Register it
tool_registry.register('my_custom_tool', my_custom_tool)
```

### Create a New Workflow

```python
my_workflow = {
    "name": "My Workflow",
    "nodes": [
        {"name": "step1", "function_name": "my_custom_tool"},
        {"name": "step2", "function_name": "another_tool"},
        {"name": "end", "function_name": "pass_through"}
    ],
    "edges": [
        {"from_node": "step1", "to_node": "step2"},
        {"from_node": "step2", "to_node": "end"}
    ],
    "start_node": "step1",
    "end_nodes": ["end"]
}
```

### Add Conditional Branching

```python
edges = [
    {
        "from_node": "check",
        "to_node": "path_a",
        "type": "conditional",
        "condition": "score > 50"  # Python expression
    },
    {
        "from_node": "check",
        "to_node": "path_b",
        "type": "conditional",
        "condition": "score <= 50"
    }
]
```

### Add a Loop

```python
edges = [
    {"from_node": "process", "to_node": "check"},
    {
        "from_node": "check",
        "to_node": "end",
        "condition": "quality >= 70"  # Exit condition
    },
    {
        "from_node": "check",
        "to_node": "process",
        "condition": "quality < 70 and iteration < 3"  # Loop back
    }
]
```

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
# Windows:
netstat -ano | findstr :8000

# Try a different port:
python -m uvicorn app.main:app --port 8001
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Tests fail
```bash
# Make sure server is running
# Check http://localhost:8000/health

# Try the basic verify script
python verify.py
```

### Module not found
```bash
# Make sure you're in the project directory
cd "Tredence Analytics"

# Check PYTHONPATH
python -c "import sys; print(sys.path)"
```

## 📊 Example Workflows

### 1. Simple Analysis
```python
# Just extract and analyze
extract → complexity → end
```

### 2. Conditional Branch
```python
# Different paths based on complexity
extract → complexity → [high: detect_issues, low: end]
```

### 3. Iterative Improvement (Loop)
```python
# Keep improving until quality threshold met
extract → analyze → improve → check_quality
    ↑                              ↓
    └──────── (if quality < 70) ───┘
                  ↓ (if quality >= 70)
                 end
```

## 🎯 Next Steps

1. **Experiment**: Try different code samples
2. **Create**: Build your own tools and workflows
3. **Extend**: Add new features (see PROJECT_SUMMARY.md)
4. **Share**: Show what you've built!

## 💡 Tips

- Start with simple linear workflows
- Test tools individually before combining
- Use the quickstart.py script for inspiration
- Check the examples/ folder for templates
- Read error messages carefully - they're descriptive

## 📞 Need Help?

- Check README.md for detailed documentation
- Review examples/ folder for templates
- Look at PROJECT_SUMMARY.md for architecture
- Run verify.py to check your setup

## 🎉 Success!

If you've reached this point, you have:
- ✅ Installed the workflow engine
- ✅ Verified it works
- ✅ Started the API server
- ✅ Tried a demo workflow

You're ready to start building workflows! 🚀

---

**Happy workflow building!**
