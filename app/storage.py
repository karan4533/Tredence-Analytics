from typing import Dict, Any
import uuid
from datetime import datetime
from app.engine import Graph
from app.models import ExecutionLogEntry


class Storage:
    """In-memory storage for graphs and runs"""
    
    def __init__(self):
        self.graphs: Dict[str, Graph] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
    
    def save_graph(self, graph: Graph) -> str:
        """Save a graph and return its ID"""
        self.graphs[graph.graph_id] = graph
        return graph.graph_id
    
    def get_graph(self, graph_id: str) -> Graph:
        """Get a graph by ID"""
        return self.graphs.get(graph_id)
    
    def list_graphs(self) -> list:
        """List all graph IDs"""
        return list(self.graphs.keys())
    
    def delete_graph(self, graph_id: str) -> bool:
        """Delete a graph"""
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            return True
        return False
    
    def save_run(self, run_id: str, graph_id: str, status: str, 
                 state: Dict[str, Any], execution_log: list, error: str = None) -> None:
        """Save a run result"""
        self.runs[run_id] = {
            'run_id': run_id,
            'graph_id': graph_id,
            'status': status,
            'state': state,
            'execution_log': execution_log,
            'error': error,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get a run by ID"""
        return self.runs.get(run_id)
    
    def list_runs(self, graph_id: str = None) -> list:
        """List all runs, optionally filtered by graph_id"""
        if graph_id:
            return [run for run in self.runs.values() if run['graph_id'] == graph_id]
        return list(self.runs.values())
    
    def update_run_status(self, run_id: str, status: str, 
                         state: Dict[str, Any] = None, 
                         execution_log: list = None) -> None:
        """Update run status"""
        if run_id in self.runs:
            self.runs[run_id]['status'] = status
            self.runs[run_id]['updated_at'] = datetime.utcnow().isoformat()
            if state:
                self.runs[run_id]['state'] = state
            if execution_log:
                self.runs[run_id]['execution_log'] = execution_log


# Global storage instance
storage = Storage()
