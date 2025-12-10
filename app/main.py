from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uuid

from app.models import (
    GraphCreate, GraphRunRequest, GraphRunResponse, 
    GraphStateResponse, ExecutionLogEntry
)
from app.engine import Graph
from app.tools import tool_registry
from app.storage import storage

app = FastAPI(
    title="Workflow Engine API",
    description="A minimal workflow/graph engine similar to LangGraph",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Workflow Engine API",
        "version": "1.0.0",
        "endpoints": {
            "create_graph": "POST /graph/create",
            "run_graph": "POST /graph/run",
            "get_state": "GET /graph/state/{run_id}",
            "list_graphs": "GET /graphs",
            "list_tools": "GET /tools"
        }
    }


@app.post("/graph/create")
async def create_graph(graph_def: GraphCreate) -> Dict[str, Any]:
    """
    Create a new workflow graph
    
    Args:
        graph_def: Graph definition with nodes and edges
    
    Returns:
        Dictionary with graph_id and status
    """
    try:
        # Convert Pydantic model to dict
        graph_dict = {
            'name': graph_def.name,
            'description': graph_def.description,
            'nodes': [node.dict() for node in graph_def.nodes],
            'edges': [edge.dict() for edge in graph_def.edges],
            'start_node': graph_def.start_node,
            'end_nodes': graph_def.end_nodes
        }
        
        # Create graph from definition
        graph = Graph.create_from_definition(graph_dict, tool_registry)
        
        # Save graph
        graph_id = storage.save_graph(graph)
        
        return {
            "graph_id": graph_id,
            "name": graph_def.name,
            "status": "created",
            "node_count": len(graph_def.nodes),
            "edge_count": len(graph_def.edges)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create graph: {str(e)}")


@app.post("/graph/run")
async def run_graph(request: GraphRunRequest) -> GraphRunResponse:
    """
    Run a workflow graph with given initial state
    
    Args:
        request: Graph run request with graph_id and initial_state
    
    Returns:
        GraphRunResponse with final state and execution log
    """
    try:
        # Get graph
        graph = storage.get_graph(request.graph_id)
        if not graph:
            raise HTTPException(status_code=404, detail=f"Graph {request.graph_id} not found")
        
        # Generate run ID
        run_id = str(uuid.uuid4())
        
        # Initialize run
        storage.save_run(
            run_id=run_id,
            graph_id=request.graph_id,
            status="running",
            state=request.initial_state,
            execution_log=[]
        )
        
        # Run the graph
        final_state, execution_log, error = graph.run(request.initial_state)
        
        # Determine status
        status = "failed" if error else "completed"
        
        # Save run results
        storage.save_run(
            run_id=run_id,
            graph_id=request.graph_id,
            status=status,
            state=final_state,
            execution_log=execution_log,
            error=error
        )
        
        # Convert execution log to Pydantic models
        log_entries = [
            ExecutionLogEntry(**entry) for entry in execution_log
        ]
        
        return GraphRunResponse(
            run_id=run_id,
            graph_id=request.graph_id,
            status=status,
            final_state=final_state,
            execution_log=log_entries,
            error=error
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run graph: {str(e)}")


@app.get("/graph/state/{run_id}")
async def get_run_state(run_id: str) -> GraphStateResponse:
    """
    Get the current state of a workflow run
    
    Args:
        run_id: ID of the run
    
    Returns:
        GraphStateResponse with current state and execution log
    """
    try:
        run = storage.get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
        
        # Convert execution log to Pydantic models
        log_entries = [
            ExecutionLogEntry(**entry) for entry in run['execution_log']
        ]
        
        return GraphStateResponse(
            run_id=run['run_id'],
            graph_id=run['graph_id'],
            status=run['status'],
            current_state=run['state'],
            execution_log=log_entries
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get run state: {str(e)}")


@app.get("/graphs")
async def list_graphs() -> Dict[str, Any]:
    """List all created graphs"""
    try:
        graph_ids = storage.list_graphs()
        graphs_info = []
        
        for graph_id in graph_ids:
            graph = storage.get_graph(graph_id)
            graphs_info.append({
                "graph_id": graph_id,
                "name": graph.name,
                "description": graph.description,
                "node_count": len(graph.engine.nodes),
                "edge_count": len(graph.engine.edges)
            })
        
        return {
            "count": len(graphs_info),
            "graphs": graphs_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list graphs: {str(e)}")


@app.get("/runs")
async def list_runs(graph_id: str = None) -> Dict[str, Any]:
    """List all runs, optionally filtered by graph_id"""
    try:
        runs = storage.list_runs(graph_id)
        
        # Simplify run info
        runs_info = [
            {
                "run_id": run['run_id'],
                "graph_id": run['graph_id'],
                "status": run['status'],
                "created_at": run['created_at'],
                "updated_at": run['updated_at']
            }
            for run in runs
        ]
        
        return {
            "count": len(runs_info),
            "runs": runs_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list runs: {str(e)}")


@app.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """List all registered tools"""
    try:
        tools = tool_registry.list_tools()
        return {
            "count": len(tools),
            "tools": tools
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
