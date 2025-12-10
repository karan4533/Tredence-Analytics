from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class NodeType(str, Enum):
    """Type of node in the workflow"""
    FUNCTION = "function"
    CONDITIONAL = "conditional"
    LOOP = "loop"


class EdgeType(str, Enum):
    """Type of edge connection"""
    DIRECT = "direct"
    CONDITIONAL = "conditional"


class NodeDefinition(BaseModel):
    """Definition of a node in the workflow"""
    name: str
    type: NodeType = NodeType.FUNCTION
    function_name: str
    description: Optional[str] = None


class EdgeDefinition(BaseModel):
    """Definition of an edge between nodes"""
    from_node: str
    to_node: str
    type: EdgeType = EdgeType.DIRECT
    condition: Optional[str] = None  # Python expression evaluated on state


class GraphDefinition(BaseModel):
    """Complete graph definition"""
    name: str
    description: Optional[str] = None
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node: str
    end_nodes: List[str] = Field(default_factory=list)


class GraphCreate(BaseModel):
    """Request model for creating a graph"""
    name: str
    description: Optional[str] = None
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node: str
    end_nodes: List[str] = Field(default_factory=list)


class GraphRunRequest(BaseModel):
    """Request model for running a graph"""
    graph_id: str
    initial_state: Dict[str, Any]


class ExecutionLogEntry(BaseModel):
    """Single entry in execution log"""
    node_name: str
    timestamp: str
    state_snapshot: Dict[str, Any]
    error: Optional[str] = None


class GraphRunResponse(BaseModel):
    """Response model for graph execution"""
    run_id: str
    graph_id: str
    status: str  # completed, failed, running
    final_state: Dict[str, Any]
    execution_log: List[ExecutionLogEntry]
    error: Optional[str] = None


class GraphStateResponse(BaseModel):
    """Response model for getting run state"""
    run_id: str
    graph_id: str
    status: str
    current_state: Dict[str, Any]
    execution_log: List[ExecutionLogEntry]
