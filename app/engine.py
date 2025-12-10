from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
import uuid
import copy


class WorkflowState:
    """Manages the state that flows through the workflow"""
    
    def __init__(self, initial_state: Dict[str, Any]):
        self.data = initial_state
        self.history: List[Dict[str, Any]] = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in state"""
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple values in state"""
        self.data.update(updates)
    
    def snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of current state"""
        return copy.deepcopy(self.data)
    
    def save_snapshot(self) -> None:
        """Save current state to history"""
        self.history.append(self.snapshot())


class Node:
    """Represents a node in the workflow graph"""
    
    def __init__(self, name: str, function: Callable, node_type: str = "function"):
        self.name = name
        self.function = function
        self.node_type = node_type
    
    def execute(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the node function with the current state"""
        return self.function(state)


class Edge:
    """Represents an edge between nodes"""
    
    def __init__(self, from_node: str, to_node: str, condition: Optional[Callable] = None):
        self.from_node = from_node
        self.to_node = to_node
        self.condition = condition  # Function that evaluates to True/False based on state
    
    def should_traverse(self, state: WorkflowState) -> bool:
        """Check if this edge should be traversed"""
        if self.condition is None:
            return True
        return self.condition(state)


class WorkflowEngine:
    """Core workflow execution engine"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.start_node: Optional[str] = None
        self.end_nodes: List[str] = []
    
    def add_node(self, node: Node) -> None:
        """Add a node to the workflow"""
        self.nodes[node.name] = node
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the workflow"""
        self.edges.append(edge)
    
    def set_start_node(self, node_name: str) -> None:
        """Set the starting node"""
        self.start_node = node_name
    
    def set_end_nodes(self, node_names: List[str]) -> None:
        """Set the ending nodes"""
        self.end_nodes = node_names
    
    def get_next_nodes(self, current_node: str, state: WorkflowState) -> List[str]:
        """Get the next nodes to execute based on current node and state"""
        next_nodes = []
        for edge in self.edges:
            if edge.from_node == current_node and edge.should_traverse(state):
                next_nodes.append(edge.to_node)
        return next_nodes
    
    def run(self, initial_state: Dict[str, Any], max_iterations: int = 100) -> tuple:
        """
        Run the workflow from start to end
        
        Returns:
            tuple: (final_state, execution_log, error)
        """
        if not self.start_node:
            return {}, [], "No start node defined"
        
        state = WorkflowState(initial_state)
        execution_log = []
        visited_sequence = []  # Track node visit sequence for loop detection
        
        current_node = self.start_node
        iterations = 0
        
        try:
            while current_node and iterations < max_iterations:
                iterations += 1
                
                # Check if we've reached an end node
                if current_node in self.end_nodes:
                    break
                
                # Check if node exists
                if current_node not in self.nodes:
                    raise ValueError(f"Node '{current_node}' not found in workflow")
                
                # Execute current node
                node = self.nodes[current_node]
                state.save_snapshot()
                
                try:
                    result = node.execute(state)
                    if result:
                        state.update(result)
                    
                    # Log execution
                    log_entry = {
                        "node_name": current_node,
                        "timestamp": datetime.utcnow().isoformat(),
                        "state_snapshot": state.snapshot(),
                        "error": None
                    }
                    execution_log.append(log_entry)
                    
                except Exception as e:
                    log_entry = {
                        "node_name": current_node,
                        "timestamp": datetime.utcnow().isoformat(),
                        "state_snapshot": state.snapshot(),
                        "error": str(e)
                    }
                    execution_log.append(log_entry)
                    raise
                
                # Get next nodes
                next_nodes = self.get_next_nodes(current_node, state)
                
                if not next_nodes:
                    # No more nodes to execute
                    break
                
                # For simplicity, take the first valid next node
                # In a more complex system, you might handle multiple branches
                current_node = next_nodes[0]
                visited_sequence.append(current_node)
            
            if iterations >= max_iterations:
                return state.snapshot(), execution_log, "Max iterations reached - possible infinite loop"
            
            return state.snapshot(), execution_log, None
            
        except Exception as e:
            return state.snapshot(), execution_log, str(e)


class Graph:
    """Represents a complete workflow graph"""
    
    def __init__(self, graph_id: str, name: str, description: str = ""):
        self.graph_id = graph_id
        self.name = name
        self.description = description
        self.engine = WorkflowEngine()
    
    @classmethod
    def create_from_definition(cls, graph_def: Dict[str, Any], tool_registry: 'ToolRegistry') -> 'Graph':
        """Create a graph from a definition dictionary"""
        graph_id = str(uuid.uuid4())
        graph = cls(graph_id, graph_def['name'], graph_def.get('description', ''))
        
        # Add nodes
        for node_def in graph_def['nodes']:
            function = tool_registry.get_tool(node_def['function_name'])
            if not function:
                raise ValueError(f"Tool '{node_def['function_name']}' not found in registry")
            
            node = Node(node_def['name'], function, node_def.get('type', 'function'))
            graph.engine.add_node(node)
        
        # Add edges
        for edge_def in graph_def['edges']:
            condition = None
            if edge_def.get('condition'):
                # Create a condition function from the expression
                condition = cls._create_condition_function(edge_def['condition'])
            
            edge = Edge(edge_def['from_node'], edge_def['to_node'], condition)
            graph.engine.add_edge(edge)
        
        # Set start and end nodes
        graph.engine.set_start_node(graph_def['start_node'])
        graph.engine.set_end_nodes(graph_def.get('end_nodes', []))
        
        return graph
    
    @staticmethod
    def _create_condition_function(condition_expr: str) -> Callable:
        """Create a condition function from a string expression"""
        def condition_fn(state: WorkflowState) -> bool:
            try:
                # Evaluate the expression with state data as local variables
                return eval(condition_expr, {"__builtins__": {}}, state.data)
            except Exception:
                return False
        return condition_fn
    
    def run(self, initial_state: Dict[str, Any]) -> tuple:
        """Run the graph with the given initial state"""
        return self.engine.run(initial_state)
