"""
Unit tests for the behavior of nodes with empty kinds when source_kind is specified.
"""
import pytest
from opengraph import OpenGraphBuilder, Node


class TestEmptyKindsWithSourceKind:
    """Test cases for nodes with empty kinds in the context of source_kind."""

    def test_empty_kinds_source_kind_behavior(self):
        """Test comprehensive empty kinds behavior with and without source_kind."""
        # Direct node creation without source_kind context should fail
        with pytest.raises(ValueError, match="Node must have at least one kind when no source_kind is specified"):
            Node(id="test123", kinds=[])

        # With source_kind available - empty kinds should work
        builder_with_source = OpenGraphBuilder(source_kind="TestSystem")
        node_empty_kinds = builder_with_source.create_node(id="test123", kinds=[])
        assert node_empty_kinds.kinds == []
        assert node_empty_kinds.source_kind_available is True

        # Without source_kind - empty kinds should fail
        builder_without_source = OpenGraphBuilder()
        with pytest.raises(ValueError, match="Node must have at least one kind when no source_kind is specified"):
            builder_without_source.create_node(id="test123", kinds=[])

        # Mixed node types with source_kind
        node_with_kinds = builder_with_source.create_node(id="test456", kinds=["User"])
        assert node_with_kinds.kinds == ["User"]
        assert node_with_kinds.source_kind_available is True
        
        # Verify serialization works correctly
        result = builder_with_source.to_dict()
        assert result["metadata"]["source_kind"] == "TestSystem"
        nodes = result["graph"]["nodes"]
        empty_kinds_node = next(node for node in nodes if node["id"] == "test123")
        assert empty_kinds_node["kinds"] == []

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

    def test_max_kinds_limit_still_enforced_with_source_kind(self):
        """Test that the 3-kinds maximum is still enforced even when source_kind is available."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # This should still fail - too many kinds
        with pytest.raises(ValueError, match="Node cannot have more than 3 kinds"):
            builder.create_node(id="test123", kinds=["Kind1", "Kind2", "Kind3", "Kind4"])
