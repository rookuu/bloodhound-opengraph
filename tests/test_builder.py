"""
Unit tests for OpenGraphBuilder class.
"""
import pytest
import json
import os
from opengraph import OpenGraphBuilder, Node, Edge, NodeReference, MatchBy


class TestOpenGraphBuilder:
    """Test cases for the OpenGraphBuilder class."""

    def test_builder_initialization_comprehensive(self):
        """Test creating builders with different initialization options."""
        # Test default initialization
        builder_default = OpenGraphBuilder()
        assert len(builder_default.nodes) == 0
        assert len(builder_default.edges) == 0
        assert builder_default.metadata is None
        
        # Test to_dict of empty builder
        result_empty = builder_default.to_dict()
        expected_empty = {"graph": {"nodes": [], "edges": []}}
        assert result_empty == expected_empty
        
        # Test initialization with source kind
        builder_with_source = OpenGraphBuilder(source_kind="TestSystem")
        assert len(builder_with_source.nodes) == 0
        assert len(builder_with_source.edges) == 0
        assert builder_with_source.metadata is not None
        assert builder_with_source.metadata.source_kind == "TestSystem"
        
        # Test to_dict with source kind
        result_with_source = builder_with_source.to_dict()
        expected_with_source = {
            "metadata": {"source_kind": "TestSystem"},
            "graph": {"nodes": [], "edges": []}
        }
        assert result_with_source == expected_with_source

    def test_add_node_success(self, sample_user_node):
        """Test adding a node successfully."""
        builder = OpenGraphBuilder()
        result = builder.add_node(sample_user_node)
        
        assert result is sample_user_node  # Should return the node
        assert len(builder.nodes) == 1
        assert builder.nodes[0] == sample_user_node
        assert sample_user_node.id in builder._node_ids

    def test_add_node_duplicate_handling(self, sample_user_node):
        """Test adding nodes with duplicate IDs - both merge and error scenarios."""
        builder = OpenGraphBuilder()
        builder.add_node(sample_user_node)
        
        # Test merge_properties=False raises error
        duplicate_node = Node(id=sample_user_node.id, kinds=["Different"])
        with pytest.raises(ValueError, match="already exists"):
            builder.add_node(duplicate_node, merge_properties=False)
        
        # Test that merging is default behavior (more comprehensive tests in test_node_merging.py)
        duplicate_node_merge = Node(id=sample_user_node.id, kinds=["Different"], properties={"new_prop": "value"})
        result = builder.add_node(duplicate_node_merge)  # Should merge by default
        assert result is sample_user_node  # Should return the existing (merged) node
        assert len(builder.nodes) == 1  # Should still have only one node
        assert "Different" in sample_user_node.kinds  # Should have merged kinds

    def test_add_edge_success(self, sample_edge):
        """Test adding an edge successfully."""
        builder = OpenGraphBuilder()
        result = builder.add_edge(sample_edge)
        
        assert result is builder  # Should return self for chaining
        assert len(builder.edges) == 1
        assert builder.edges[0] == sample_edge

    def test_create_node_success(self):
        """Test creating and adding a node via create_node method."""
        builder = OpenGraphBuilder()
        properties = {"email": "test@example.com", "active": True}
        
        node = builder.create_node(id="test123", kinds=["User"], properties=properties)
        
        assert isinstance(node, Node)
        assert node.id == "test123"
        assert node.kinds == ["User"]
        assert node.properties == properties
        assert len(builder.nodes) == 1
        assert builder.nodes[0] == node

    def test_create_edge_success(self):
        """Test creating and adding an edge via create_edge method."""
        builder = OpenGraphBuilder()
        properties = {"weight": 1.0}
        
        edge = builder.create_edge(
            start_value="start123",
            end_value="end456",
            kind="ConnectedTo",
            properties=properties
        )
        
        assert isinstance(edge, Edge)
        assert edge.start.value == "start123"
        assert edge.start.match_by == MatchBy.ID
        assert edge.end.value == "end456" 
        assert edge.end.match_by == MatchBy.ID
        assert edge.kind == "ConnectedTo"
        assert edge.properties == properties
        assert len(builder.edges) == 1
        assert builder.edges[0] == edge

    def test_create_edge_with_custom_matching(self):
        """Test creating an edge with custom node matching."""
        builder = OpenGraphBuilder()
        
        edge = builder.create_edge(
            start_value="alice",
            end_value="server01",
            kind="AdminTo",
            start_match_by=MatchBy.NAME,
            end_match_by=MatchBy.NAME,
            start_kind="Person",
            end_kind="Computer"
        )
        
        assert edge.start.value == "alice"
        assert edge.start.match_by == MatchBy.NAME
        assert edge.start.kind == "Person"
        assert edge.end.value == "server01"
        assert edge.end.match_by == MatchBy.NAME
        assert edge.end.kind == "Computer"

    def test_to_json_and_dict_comprehensive(self, populated_builder):
        """Test converting to JSON and dictionary with various formatting options."""
        # Test to_dict
        result_dict = populated_builder.to_dict()
        assert "metadata" in result_dict
        assert "graph" in result_dict
        assert "nodes" in result_dict["graph"]
        assert "edges" in result_dict["graph"]
        assert len(result_dict["graph"]["nodes"]) == 2
        assert len(result_dict["graph"]["edges"]) == 1
        assert result_dict["metadata"]["source_kind"] == "TestSystem"
        
        # Test to_json compact
        json_compact = populated_builder.to_json(indent=None)
        data_compact = json.loads(json_compact)
        assert "graph" in data_compact
        assert "metadata" in data_compact
        assert "\n" not in json_compact  # Should be compact
        
        # Test to_json indented
        json_indented = populated_builder.to_json(indent=2)
        data_indented = json.loads(json_indented)
        assert "graph" in data_indented
        assert "\n" in json_indented  # Should be formatted

    def test_to_dict_empty_builder(self):
        """Test converting empty builder to dictionary."""
        builder = OpenGraphBuilder()
        result = builder.to_dict()
        
        expected = {
            "graph": {
                "nodes": [],
                "edges": []
            }
        }
        assert result == expected

    def test_to_dict_with_source_kind(self):
        """Test converting builder with source kind to dictionary."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        result = builder.to_dict()
        
        expected = {
            "metadata": {
                "source_kind": "TestSystem"
            },
            "graph": {
                "nodes": [],
                "edges": []
            }
        }
        assert result == expected

    def test_save_to_file(self, populated_builder, temp_json_file):
        """Test saving builder data to JSON file."""
        populated_builder.save_to_file(temp_json_file)
        
        # File should exist and contain valid JSON
        assert os.path.exists(temp_json_file)
        
        with open(temp_json_file, 'r') as f:
            data = json.load(f)
        
        assert "graph" in data
        assert "metadata" in data
        assert len(data["graph"]["nodes"]) == 2
        assert len(data["graph"]["edges"]) == 1

    def test_builder_state_management(self, populated_builder):
        """Test clearing, counting, and basic state management of builder."""
        # Test get_counts
        assert populated_builder.get_node_count() == 2
        assert populated_builder.get_edge_count() == 1
        
        # Test clear (verify builder has data first)
        assert len(populated_builder.nodes) > 0
        assert len(populated_builder.edges) > 0
        assert len(populated_builder._node_ids) > 0
        
        populated_builder.clear()
        
        assert len(populated_builder.nodes) == 0
        assert len(populated_builder.edges) == 0
        assert len(populated_builder._node_ids) == 0

    def test_validate_success(self, populated_builder):
        """Test successful validation of populated builder."""
        assert populated_builder.validate() is True

    def test_validate_duplicate_node_ids(self):
        """Test validation fails with duplicate node IDs."""
        builder = OpenGraphBuilder()
        
        # Manually add nodes with same ID to bypass add_node validation
        node1 = Node(id="test123", kinds=["User"])
        node2 = Node(id="test123", kinds=["Computer"])
        
        builder.nodes.append(node1)
        builder.nodes.append(node2)
        
        with pytest.raises(ValueError, match="Duplicate node IDs found"):
            builder.validate()

    def test_validate_edge_references_missing_node(self):
        """Test validation fails when edge references non-existent node."""
        builder = OpenGraphBuilder()
        
        # Add edge without corresponding nodes
        edge = Edge(
            start=NodeReference(value="missing1"),
            end=NodeReference(value="missing2"),
            kind="ConnectedTo"
        )
        builder.add_edge(edge)
        
        with pytest.raises(ValueError, match="does not exist"):
            builder.validate()

    def test_validate_edge_references_by_name(self):
        """Test validation of edge references by name."""
        builder = OpenGraphBuilder()
        
        # Add nodes with name properties
        node1 = Node(id="id1", kinds=["User"], properties={"name": "alice"})
        node2 = Node(id="id2", kinds=["Computer"], properties={"name": "server01"})
        builder.add_node(node1)
        builder.add_node(node2)
        
        # Add edge referencing by name
        edge = Edge(
            start=NodeReference(value="alice", match_by=MatchBy.NAME),
            end=NodeReference(value="server01", match_by=MatchBy.NAME),
            kind="AdminTo"
        )
        builder.add_edge(edge)
        
        # Should validate successfully
        assert builder.validate() is True

    def test_validate_edge_references_by_name_missing(self):
        """Test validation fails when name reference doesn't exist."""
        builder = OpenGraphBuilder()
        
        # Add node without name property
        node = Node(id="id1", kinds=["User"])
        builder.add_node(node)
        
        # Add edge referencing by name that doesn't exist
        edge = Edge(
            start=NodeReference(value="alice", match_by=MatchBy.NAME),
            end=NodeReference(value="id1", match_by=MatchBy.ID),
            kind="ConnectedTo"
        )
        builder.add_edge(edge)
        
        with pytest.raises(ValueError, match="does not exist"):
            builder.validate()
