"""
Unit tests for node property merging functionality.
"""
import pytest
from opengraph import OpenGraphBuilder, Node


class TestNodeMerging:
    """Test cases for node merging functionality."""

    def test_node_merge_default_behavior(self):
        """Test that nodes merge properties and kinds by default when duplicate ID exists."""
        builder = OpenGraphBuilder()
        
        # Test with create_node
        node1 = builder.create_node(id="user123", kinds=["User"], properties={"name": "Alice", "age": 25})
        node2 = builder.create_node(id="user123", kinds=["Person"], properties={"email": "alice@example.com", "age": 26})
        
        # Should still have only one node in the builder
        assert len(builder.nodes) == 1
        assert builder.get_node_count() == 1
        assert node2 is node1
        
        # Check merged kinds and properties (new values override old ones)
        assert set(node1.kinds) == {"User", "Person"}
        assert node1.properties == {"name": "Alice", "age": 26, "email": "alice@example.com"}
        
        # Test with add_node
        builder2 = OpenGraphBuilder()
        node3 = Node(id="user456", kinds=["Admin"], properties={"role": "super"})
        builder2.add_node(node3)
        node4 = Node(id="user456", kinds=["User"], properties={"name": "Bob", "role": "admin"})
        builder2.add_node(node4)
        
        assert len(builder2.nodes) == 1
        assert set(node3.kinds) == {"Admin", "User"}
        assert node3.properties == {"role": "admin", "name": "Bob"}

    def test_node_merge_disabled(self):
        """Test that merge_properties=False raises error when duplicate ID exists."""
        builder = OpenGraphBuilder()
        
        # Test with create_node
        builder.create_node(id="user123", kinds=["User"], properties={"name": "Alice"})
        with pytest.raises(ValueError, match="Node with ID 'user123' already exists"):
            builder.create_node(id="user123", kinds=["Person"], merge_properties=False)
        
        # Test with add_node
        builder2 = OpenGraphBuilder()
        node1 = Node(id="user456", kinds=["User"], properties={"name": "Bob"})
        builder2.add_node(node1)
        node2 = Node(id="user456", kinds=["Person"], properties={"email": "bob@example.com"})
        with pytest.raises(ValueError, match="Node with ID 'user456' already exists"):
            builder2.add_node(node2, merge_properties=False)

    def test_merge_kinds_with_empty_existing_kinds(self):
        """Test merging when existing node has empty kinds (with source_kind available)."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # Create first node with empty kinds
        node1 = builder.create_node(id="node123", kinds=[])
        
        # Merge with node that has kinds
        node2 = builder.create_node(id="node123", kinds=["User", "Person"])
        
        # Should have merged kinds
        assert node1.kinds == ["User", "Person"]
        assert node2 is node1

    def test_merge_kinds_behavior(self):
        """Test kind merging behavior including limits and duplicates."""
        builder = OpenGraphBuilder()
        
        # Test merging up to 3 kinds limit
        node1 = builder.create_node(id="node123", kinds=["Kind1"])
        node2 = builder.create_node(id="node123", kinds=["Kind2", "Kind3"])
        assert set(node1.kinds) == {"Kind1", "Kind2", "Kind3"}
        assert len(node1.kinds) == 3
        
        # Test that duplicate kinds are ignored
        builder2 = OpenGraphBuilder()
        node3 = builder2.create_node(id="node456", kinds=["User", "Person"])
        node4 = builder2.create_node(id="node456", kinds=["Person", "Employee"])
        assert set(node3.kinds) == {"User", "Person", "Employee"}
        assert len(node3.kinds) == 3
        
        # Test that exceeding 3 kinds raises error
        builder3 = OpenGraphBuilder()
        node5 = builder3.create_node(id="node789", kinds=["Kind1", "Kind2"])
        with pytest.raises(ValueError, match="more than 3 kinds"):
            builder3.create_node(id="node789", kinds=["Kind3", "Kind4"])

    def test_merge_properties_behavior(self):
        """Test property merging behavior in various scenarios."""
        builder = OpenGraphBuilder()
        
        # Test merging None to properties
        node1 = builder.create_node(id="node123", kinds=["User"])
        assert node1.properties is None
        properties = {"name": "Alice", "age": 25}
        builder.create_node(id="node123", kinds=["Person"], properties=properties)
        assert node1.properties == properties
        
        # Test merging properties to None (properties should be preserved)
        builder2 = OpenGraphBuilder()
        initial_properties = {"name": "Bob", "age": 30}
        node2 = builder2.create_node(id="node456", kinds=["User"], properties=initial_properties)
        builder2.create_node(id="node456", kinds=["Person"])  # No properties
        assert node2.properties == initial_properties
        
        # Test property override behavior
        builder3 = OpenGraphBuilder()
        node3 = builder3.create_node(id="node789", kinds=["User"], 
                                    properties={"name": "Charlie", "age": 25, "city": "NYC"})
        builder3.create_node(id="node789", kinds=["Person"], 
                            properties={"age": 26, "email": "charlie@example.com"})
        expected = {"name": "Charlie", "age": 26, "city": "NYC", "email": "charlie@example.com"}
        assert node3.properties == expected

    def test_merge_validates_merged_node(self):
        """Test that merged node is properly validated."""
        builder = OpenGraphBuilder()
        
        # Create first node
        node1 = builder.create_node(id="node123", kinds=["User"])
        
        # Try to merge with invalid properties (should raise validation error)
        with pytest.raises(ValueError, match="cannot be an object"):
            builder.create_node(id="node123", kinds=["Person"], 
                               properties={"invalid": {"nested": "object"}})

    def test_merge_with_source_kind_context(self):
        """Test that merging works correctly with source_kind context."""
        builder = OpenGraphBuilder(source_kind="TestSystem")
        
        # Create node with empty kinds (allowed with source_kind)
        node1 = builder.create_node(id="node123", kinds=[])
        
        # Merge with another node
        node2 = builder.create_node(id="node123", kinds=["User"], properties={"name": "Test"})
        
        assert node1.kinds == ["User"]
        assert node1.properties == {"name": "Test"}
        assert node1.source_kind_available is True

    def test_merge_integration_scenarios(self):
        """Test complex merging scenarios including serialization and edge references."""
        # Test serialization after merge
        builder = OpenGraphBuilder(source_kind="TestSystem")
        builder.create_node(id="user1", kinds=["User"], properties={"name": "Alice"})
        builder.create_node(id="user1", kinds=["Person"], properties={"age": 25})
        
        result = builder.to_dict()
        nodes = result["graph"]["nodes"]
        assert len(nodes) == 1
        
        node = nodes[0]
        assert node["id"] == "user1"
        assert set(node["kinds"]) == {"User", "Person"}
        assert node["properties"] == {"name": "Alice", "age": 25}
        
        # Test edge references after merge
        builder2 = OpenGraphBuilder()
        builder2.create_node(id="user1", kinds=["User"])
        builder2.create_node(id="user2", kinds=["User"])
        builder2.create_edge("user1", "user2", "ConnectedTo")
        
        # Merge properties into first node
        builder2.create_node(id="user1", kinds=["Person"], properties={"name": "Alice"})
        
        # Validation should still pass
        assert builder2.validate() is True
        assert len(builder2.nodes) == 2
        assert len(builder2.edges) == 1
        
        user1 = next(node for node in builder2.nodes if node.id == "user1")
        assert set(user1.kinds) == {"User", "Person"}
        assert user1.properties == {"name": "Alice"}