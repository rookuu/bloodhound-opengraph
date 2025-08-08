"""
Core classes and functionality for the BloodHound OpenGraph library.
"""

import json
from typing import Dict, List, Union, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class MatchBy(Enum):
    """Enumeration for node matching strategies."""
    ID = "id"
    NAME = "name"


@dataclass
class NodeReference:
    """
    Represents a reference to a node in an edge.
    
    Args:
        value: The value used for matching (either an object ID or a name)
        match_by: Whether to match by 'id' or 'name' (defaults to 'id')
        kind: Optional kind filter; the referenced node must have this kind
    """
    value: str
    match_by: MatchBy = MatchBy.ID
    kind: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "value": self.value,
            "match_by": self.match_by.value
        }
        if self.kind:
            result["kind"] = self.kind
        return result


@dataclass
class Node:
    """
    Represents a node in the OpenGraph.
    
    Args:
        id: Unique identifier for the node
        kinds: Array of kind labels (1-3 items, first is primary kind)
        properties: Optional key-value map of node attributes
    """
    id: str
    kinds: List[str]
    properties: Optional[Dict[str, Union[str, int, float, bool, List]]] = None
    
    def __post_init__(self):
        """Validate node data after initialization."""
        if not self.kinds:
            raise ValueError("Node must have at least one kind")
        if len(self.kinds) > 3:
            raise ValueError("Node cannot have more than 3 kinds")
        
        # Validate properties if present
        if self.properties:
            self._validate_properties()
    
    def _validate_properties(self):
        """Validate that properties conform to schema requirements."""
        for key, value in self.properties.items():
            if isinstance(value, dict):
                raise ValueError(f"Property '{key}' cannot be an object - only primitive types and arrays allowed")
            
            if isinstance(value, list):
                if not value:
                    continue  # Empty arrays are allowed
                
                # Check that array is homogeneous
                first_type = type(value[0])
                if not all(isinstance(item, first_type) for item in value):
                    raise ValueError(f"Property '{key}' array must be homogeneous (all items same type)")
                
                # Check that array doesn't contain objects
                if any(isinstance(item, dict) for item in value):
                    raise ValueError(f"Property '{key}' array cannot contain objects")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "kinds": self.kinds
        }
        if self.properties is not None:
            result["properties"] = self.properties
        return result


@dataclass
class Edge:
    """
    Represents an edge between two nodes in the OpenGraph.
    
    Args:
        start: Reference to the start node
        end: Reference to the end node
        kind: The relationship type
        properties: Optional key-value map of edge attributes
    """
    start: NodeReference
    end: NodeReference
    kind: str
    properties: Optional[Dict[str, Union[str, int, float, bool, List]]] = None
    
    def __post_init__(self):
        """Validate edge data after initialization."""
        if not self.kind:
            raise ValueError("Edge must have a kind")
        
        # Validate properties if present
        if self.properties:
            self._validate_properties()
    
    def _validate_properties(self):
        """Validate that properties conform to schema requirements."""
        for key, value in self.properties.items():
            if isinstance(value, dict):
                raise ValueError(f"Property '{key}' cannot be an object - only primitive types and arrays allowed")
            
            if isinstance(value, list):
                if not value:
                    continue  # Empty arrays are allowed
                
                # Check that array is homogeneous
                first_type = type(value[0])
                if not all(isinstance(item, first_type) for item in value):
                    raise ValueError(f"Property '{key}' array must be homogeneous (all items same type)")
                
                # Check that array doesn't contain objects
                if any(isinstance(item, dict) for item in value):
                    raise ValueError(f"Property '{key}' array cannot contain objects")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "kind": self.kind
        }
        if self.properties is not None:
            result["properties"] = self.properties
        return result


@dataclass
class OpenGraphMetadata:
    """
    Optional metadata for the OpenGraph.
    
    Args:
        source_kind: A string that applies to all nodes in the file, used to attribute a source
    """
    source_kind: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}
        if self.source_kind:
            result["source_kind"] = self.source_kind
        return result


class OpenGraphBuilder:
    """
    Builder class for creating BloodHound OpenGraph JSON structures.
    
    This class provides methods to add nodes and edges, and then export
    the complete structure as JSON conforming to the BloodHound schema.
    """
    
    def __init__(self, source_kind: Optional[str] = None):
        """
        Initialize the OpenGraph builder.
        
        Args:
            source_kind: Optional source kind to apply to all nodes
        """
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.metadata = OpenGraphMetadata(source_kind=source_kind) if source_kind else None
        self._node_ids: set = set()  # Track node IDs to prevent duplicates
    
    def add_node(self, node: Node) -> 'OpenGraphBuilder':
        """
        Add a node to the graph.
        
        Args:
            node: The node to add
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If a node with the same ID already exists
        """
        if node.id in self._node_ids:
            raise ValueError(f"Node with ID '{node.id}' already exists")
        
        self.nodes.append(node)
        self._node_ids.add(node.id)
        return self
    
    def add_edge(self, edge: Edge) -> 'OpenGraphBuilder':
        """
        Add an edge to the graph.
        
        Args:
            edge: The edge to add
            
        Returns:
            Self for method chaining
        """
        self.edges.append(edge)
        return self
    
    def create_node(self, id: str, kinds: List[str], 
                   properties: Optional[Dict[str, Any]] = None) -> Node:
        """
        Create and add a node to the graph.
        
        Args:
            id: Unique identifier for the node
            kinds: Array of kind labels
            properties: Optional properties dictionary
            
        Returns:
            The created node
        """
        node = Node(id=id, kinds=kinds, properties=properties)
        self.add_node(node)
        return node
    
    def create_edge(self, start_value: str, end_value: str, kind: str,
                   start_match_by: MatchBy = MatchBy.ID,
                   end_match_by: MatchBy = MatchBy.ID,
                   start_kind: Optional[str] = None,
                   end_kind: Optional[str] = None,
                   properties: Optional[Dict[str, Any]] = None) -> Edge:
        """
        Create and add an edge to the graph.
        
        Args:
            start_value: Value to match the start node
            end_value: Value to match the end node
            kind: The relationship type
            start_match_by: How to match the start node (default: ID)
            end_match_by: How to match the end node (default: ID)
            start_kind: Optional kind filter for start node
            end_kind: Optional kind filter for end node
            properties: Optional properties dictionary
            
        Returns:
            The created edge
        """
        start_ref = NodeReference(value=start_value, match_by=start_match_by, kind=start_kind)
        end_ref = NodeReference(value=end_value, match_by=end_match_by, kind=end_kind)
        edge = Edge(start=start_ref, end=end_ref, kind=kind, properties=properties)
        self.add_edge(edge)
        return edge
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the OpenGraph to a dictionary structure.
        
        Returns:
            Dictionary representation ready for JSON serialization
        """
        result = {
            "graph": {
                "nodes": [node.to_dict() for node in self.nodes],
                "edges": [edge.to_dict() for edge in self.edges]
            }
        }
        
        if self.metadata and self.metadata.source_kind:
            result["metadata"] = self.metadata.to_dict()
        
        return result
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Export the OpenGraph as JSON string.
        
        Args:
            indent: Number of spaces for indentation (None for compact JSON)
            
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    def save_to_file(self, filepath: str, indent: Optional[int] = 2):
        """
        Save the OpenGraph to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
            indent: Number of spaces for indentation (None for compact JSON)
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=indent)
    
    def clear(self):
        """Clear all nodes and edges from the builder."""
        self.nodes.clear()
        self.edges.clear()
        self._node_ids.clear()
    
    def get_node_count(self) -> int:
        """Get the number of nodes in the graph."""
        return len(self.nodes)
    
    def get_edge_count(self) -> int:
        """Get the number of edges in the graph."""
        return len(self.edges)
    
    def validate(self) -> bool:
        """
        Validate the current graph structure.
        
        Returns:
            True if valid, raises exception otherwise
            
        Raises:
            ValueError: If validation fails
        """
        # Check for duplicate node IDs
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Duplicate node IDs found")
        
        # Check that all edges reference existing nodes
        self._validate_edge_references()
        
        # All validations passed
        return True
    
    def _validate_edge_references(self):
        """
        Validate that all edge start and end references can be resolved to existing nodes.
        
        Raises:
            ValueError: If any edge references a non-existent node
        """
        if not self.edges:
            return  # No edges to validate
        
        # Build lookup maps for node resolution
        nodes_by_id = {node.id: node for node in self.nodes}
        nodes_by_name = {}
        
        # Build name lookup map (only for nodes that have a 'name' property)
        for node in self.nodes:
            if node.properties and 'name' in node.properties:
                name = node.properties['name']
                if isinstance(name, str):
                    if name in nodes_by_name:
                        # Multiple nodes with same name - store as list
                        if not isinstance(nodes_by_name[name], list):
                            nodes_by_name[name] = [nodes_by_name[name]]
                        nodes_by_name[name].append(node)
                    else:
                        nodes_by_name[name] = node
        
        # Validate each edge
        for i, edge in enumerate(self.edges):
            # Validate start node reference
            self._validate_node_reference(edge.start, f"edge {i} start", nodes_by_id, nodes_by_name)
            
            # Validate end node reference
            self._validate_node_reference(edge.end, f"edge {i} end", nodes_by_id, nodes_by_name)
    
    def _validate_node_reference(self, ref: NodeReference, ref_description: str, 
                               nodes_by_id: Dict[str, Node], 
                               nodes_by_name: Dict[str, Union[Node, List[Node]]]):
        """
        Validate a single node reference.
        
        Args:
            ref: The NodeReference to validate
            ref_description: Description for error messages (e.g., "edge 0 start")
            nodes_by_id: Dictionary mapping node IDs to nodes
            nodes_by_name: Dictionary mapping node names to nodes (or lists of nodes)
            
        Raises:
            ValueError: If the reference cannot be resolved
        """
        if ref.match_by == MatchBy.ID:
            # Match by ID
            if ref.value not in nodes_by_id:
                raise ValueError(f"Node referenced by {ref_description} with ID '{ref.value}' does not exist")
            
            # If kind filter specified, validate it
            if ref.kind:
                node = nodes_by_id[ref.value]
                if ref.kind not in node.kinds:
                    raise ValueError(
                        f"Node referenced by {ref_description} with ID '{ref.value}' "
                        f"does not have required kind '{ref.kind}'. "
                        f"Node kinds: {node.kinds}"
                    )
        
        elif ref.match_by == MatchBy.NAME:
            # Match by name
            if ref.value not in nodes_by_name:
                raise ValueError(f"Node referenced by {ref_description} with name '{ref.value}' does not exist")
            
            candidate_nodes = nodes_by_name[ref.value]
            
            # If multiple nodes have the same name, kind filter is required for disambiguation
            if isinstance(candidate_nodes, list):
                if not ref.kind:
                    raise ValueError(
                        f"Multiple nodes found with name '{ref.value}' for {ref_description}. "
                        f"Kind filter is required for disambiguation. "
                        f"Available kinds: {[kind for node in candidate_nodes for kind in node.kinds]}"
                    )
                
                # Find nodes matching the kind filter
                matching_nodes = [node for node in candidate_nodes if ref.kind in node.kinds]
                
                if not matching_nodes:
                    available_kinds = [kind for node in candidate_nodes for kind in node.kinds]
                    raise ValueError(
                        f"No node with name '{ref.value}' and kind '{ref.kind}' found for {ref_description}. "
                        f"Available kinds for nodes with this name: {list(set(available_kinds))}"
                    )
                
                if len(matching_nodes) > 1:
                    raise ValueError(
                        f"Multiple nodes with name '{ref.value}' and kind '{ref.kind}' found for {ref_description}. "
                        f"Node references must resolve to exactly one node."
                    )
            
            else:
                # Single node with this name
                if ref.kind and ref.kind not in candidate_nodes.kinds:
                    raise ValueError(
                        f"Node referenced by {ref_description} with name '{ref.value}' "
                        f"does not have required kind '{ref.kind}'. "
                        f"Node kinds: {candidate_nodes.kinds}"
                    )
