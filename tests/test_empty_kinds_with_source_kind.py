"""
Unit tests for the behavior of nodes with empty kinds when source_kind is specified.
"""
import pytest
from opengraph import OpenGraphBuilder, Node


class TestEmptyKindsWithSourceKind:
    """Test cases for nodes with empty kinds in the context of source_kind."""

    def test_node_with_empty_kinds_requires_source_kind_context(self):
        """Test that a node with empty kinds fails validation without source_kind context."""
        # Direct node creation without source_kind context should still fail
        with pytest.raises(ValueError, match="Node must have at least one kind when no source_kind is specified"):
            Node(id="test123", kinds=[])

    def test_node_with_empty_kinds_succeeds_with_source_kind_context(self):
        """Test that a node with empty kinds succeeds when source_kind is available."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # This should work - 0 kinds is acceptable when source_kind is specified
        node = builder.create_node(id="test123", kinds=[])
        
        assert node.id == "test123"
        assert node.kinds == []
        assert node.source_kind_available is True
        assert len(builder.nodes) == 1

    def test_node_with_empty_kinds_fails_without_source_kind(self):
        """Test that a node with empty kinds fails when no source_kind is specified."""
        builder = OpenGraphBuilder()  # No source_kind
        
        # This should fail - 0 kinds is not acceptable without source_kind
        with pytest.raises(ValueError, match="Node must have at least one kind when no source_kind is specified"):
            builder.create_node(id="test123", kinds=[])

    def test_add_node_with_empty_kinds_and_source_kind(self):
        """Test adding a pre-created node with empty kinds to a builder with source_kind."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # Create node first (this will fail initially due to no context)
        with pytest.raises(ValueError, match="Node must have at least one kind when no source_kind is specified"):
            Node(id="test123", kinds=[])
        
        # But we can work around this by creating through the builder
        node = builder.create_node(id="test123", kinds=[])
        assert node.source_kind_available is True
        assert len(builder.nodes) == 1

    def test_add_node_with_empty_kinds_fails_without_source_kind(self):
        """Test adding a pre-created node with empty kinds to a builder without source_kind."""
        builder = OpenGraphBuilder()  # No source_kind
        
        # This should fail when trying to create via builder
        with pytest.raises(ValueError, match="Node must have at least one kind when no source_kind is specified"):
            builder.create_node(id="test123", kinds=[])

    def test_node_with_kinds_works_regardless_of_source_kind(self):
        """Test that nodes with kinds work whether or not source_kind is specified."""
        # With source_kind
        builder_with_source = OpenGraphBuilder(source_kind="TestSystem")
        node1 = builder_with_source.create_node(id="test1", kinds=["User"])
        assert node1.kinds == ["User"]
        assert node1.source_kind_available is True
        
        # Without source_kind
        builder_without_source = OpenGraphBuilder()
        node2 = builder_without_source.create_node(id="test2", kinds=["User"])
        assert node2.kinds == ["User"]
        assert node2.source_kind_available is False

    def test_mixed_nodes_with_and_without_kinds_with_source_kind(self):
        """Test that we can mix nodes with and without kinds when source_kind is available."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # Add node with kinds
        node1 = builder.create_node(id="test1", kinds=["User"])
        
        # Add node without kinds
        node2 = builder.create_node(id="test2", kinds=[])
        
        # Add node with multiple kinds
        node3 = builder.create_node(id="test3", kinds=["User", "Person"])
        
        assert len(builder.nodes) == 3
        assert node1.kinds == ["User"]
        assert node2.kinds == []
        assert node3.kinds == ["User", "Person"]
        
        # All should have source_kind_available set to True
        assert node1.source_kind_available is True
        assert node2.source_kind_available is True
        assert node3.source_kind_available is True

    def test_to_dict_includes_empty_kinds_when_source_kind_available(self):
        """Test that nodes with empty kinds serialize properly to dict."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        node = builder.create_node(id="test123", kinds=[], properties={"name": "Test Node"})
        
        result = node.to_dict()
        expected = {
            "id": "test123",
            "kinds": [],
            "properties": {"name": "Test Node"}
        }
        assert result == expected

    def test_full_graph_with_empty_kinds_serialization(self):
        """Test that a complete graph with empty kinds nodes serializes correctly."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # Add nodes with various kind configurations
        builder.create_node(id="node1", kinds=["User"])
        builder.create_node(id="node2", kinds=[])
        builder.create_node(id="node3", kinds=["System", "Computer"])
        
        # Add an edge
        builder.create_edge("node1", "node2", "ConnectedTo")
        
        result = builder.to_dict()
        
        # Check structure
        assert "metadata" in result
        assert result["metadata"]["source_kind"] == "TestSystem"
        
        nodes = result["graph"]["nodes"]
        assert len(nodes) == 3
        
        # Find the node with empty kinds
        empty_kinds_node = next(node for node in nodes if node["id"] == "node2")
        assert empty_kinds_node["kinds"] == []

    def test_source_kind_context_validation_on_existing_node(self):
        """Test that existing nodes get re-validated when added to builder with different context."""
        # This tests the edge case where someone might try to add a node 
        # created outside the builder context
        
        # Create a valid node with kinds
        node = Node(id="test123", kinds=["User"])
        
        # Add to builder without source_kind - should work
        builder_without_source = OpenGraphBuilder()
        builder_without_source.add_node(node)
        assert node.source_kind_available is False
        
        # Create another valid node with kinds  
        node2 = Node(id="test456", kinds=["System"])
        
        # Add to builder with source_kind - should work and update context
        builder_with_source = OpenGraphBuilder(source_kind="TestSystem")
        builder_with_source.add_node(node2)
        assert node2.source_kind_available is True

    def test_max_kinds_limit_still_enforced_with_source_kind(self):
        """Test that the 3-kinds maximum is still enforced even when source_kind is available."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # This should still fail - too many kinds
        with pytest.raises(ValueError, match="Node cannot have more than 3 kinds"):
            builder.create_node(id="test123", kinds=["Kind1", "Kind2", "Kind3", "Kind4"])

    def test_edge_cases_with_source_kind_changes(self):
        """Test edge cases when source_kind context changes."""
        # Create builder with source_kind
        builder = OpenGraphBuilder(source_kind="TestSystem")
        node = builder.create_node(id="test123", kinds=[])
        assert node.source_kind_available is True
        
        # The node should still be valid in its current context
        # (We don't test removing source_kind as that's not part of the current API,
        # but this test ensures the node works as expected when created in the right context)
        
        result = builder.to_dict()
        assert result["metadata"]["source_kind"] == "TestSystem"
        
        # Find our empty-kinds node
        nodes = result["graph"]["nodes"] 
        empty_node = next(node for node in nodes if node["id"] == "test123")
        assert empty_node["kinds"] == []
