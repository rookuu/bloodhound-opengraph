"""
Unit tests for Node class.
"""
import pytest
from opengraph import Node


class TestNode:
    """Test cases for the Node class."""

    def test_node_creation_minimal(self):
        """Test creating a node with minimal required fields."""
        node = Node(id="test123", kinds=["User"])
        
        assert node.id == "test123"
        assert node.kinds == ["User"]
        assert node.properties is None

    def test_node_creation_with_properties(self):
        """Test creating a node with properties."""
        properties = {
            "email": "test@example.com",
            "active": True,
            "count": 42,
            "score": 98.5
        }
        node = Node(id="test123", kinds=["User"], properties=properties)
        
        assert node.id == "test123"
        assert node.kinds == ["User"]
        assert node.properties == properties

    def test_node_creation_multiple_kinds(self):
        """Test creating a node with multiple kinds."""
        node = Node(id="test123", kinds=["User", "Person", "Employee"])
        
        assert node.id == "test123"
        assert node.kinds == ["User", "Person", "Employee"]

    def test_node_validation_too_many_kinds(self):
        """Test that nodes with more than 3 kinds raise ValueError."""
        with pytest.raises(ValueError, match="Node cannot have more than 3 kinds"):
            Node(id="test123", kinds=["Kind1", "Kind2", "Kind3", "Kind4"])

    def test_node_property_validation_comprehensive(self):
        """Test node property validation (primitive types, arrays, and rejections)."""
        # Test valid primitive and array properties
        valid_properties = {
            "string_prop": "test",
            "int_prop": 42,
            "float_prop": 3.14,
            "bool_prop": True,
            "string_array": ["item1", "item2", "item3"],
            "int_array": [1, 2, 3],
            "bool_array": [True, False, True],
            "empty_array": []
        }
        node = Node(id="test123", kinds=["User"], properties=valid_properties)
        assert node.properties == valid_properties

        # Test rejection of objects
        with pytest.raises(ValueError, match="cannot be an object"):
            Node(id="test123", kinds=["User"], properties={"nested": {"key": "value"}})

        # Test rejection of mixed arrays
        with pytest.raises(ValueError, match="array must be homogeneous"):
            Node(id="test123", kinds=["User"], properties={"mixed": [1, "string", True]})

        # Test rejection of object arrays
        with pytest.raises(ValueError, match="array cannot contain objects"):
            Node(id="test123", kinds=["User"], properties={"objects": [{"key": "value"}]})

    def test_node_property_validation_none_prop(self):
        """Test that properties with None values are stripped."""
        properties_with_none = {
            "valid_prop": "test",
            "none_prop": None,
            "another_valid": 42
        }
        node = Node(id="test123", kinds=["User"], properties=properties_with_none)
        assert node.properties == {
            "valid_prop": "test",
            "another_valid": 42
        }

    def test_node_to_dict_comprehensive(self):
        """Test converting nodes to dictionary in various scenarios."""
        # Minimal node
        node_minimal = Node(id="test123", kinds=["User"])
        assert node_minimal.to_dict() == {"id": "test123", "kinds": ["User"]}
        
        # Node with properties
        properties = {"email": "test@example.com", "active": True}
        node_with_props = Node(id="test123", kinds=["User"], properties=properties)
        expected_with_props = {"id": "test123", "kinds": ["User"], "properties": properties}
        assert node_with_props.to_dict() == expected_with_props
        
        # Node with None properties (should be excluded)
        node_none_props = Node(id="test123", kinds=["User"], properties=None)
        assert node_none_props.to_dict() == {"id": "test123", "kinds": ["User"]}

    @pytest.mark.parametrize("kinds", [
        ["User"],
        ["User", "Person"],
        ["User", "Person", "Employee"]
    ])
    def test_node_valid_kinds_count(self, kinds):
        """Test that 1-3 kinds are accepted."""
        node = Node(id="test123", kinds=kinds)
        assert node.kinds == kinds

    def test_node_equality(self):
        """Test node equality comparison."""
        node1 = Node(id="test123", kinds=["User"], properties={"active": True})
        node2 = Node(id="test123", kinds=["User"], properties={"active": True})
        
        # Note: dataclass equality compares all fields
        assert node1 == node2

    def test_node_inequality(self):
        """Test node inequality comparison."""
        node1 = Node(id="test123", kinds=["User"])
        node2 = Node(id="test456", kinds=["User"])
        
        assert node1 != node2
