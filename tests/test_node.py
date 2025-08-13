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

    def test_node_validation_empty_kinds(self):
        """Test that nodes with empty kinds raise ValueError."""
        with pytest.raises(ValueError, match="Node must have at least one kind"):
            Node(id="test123", kinds=[])

    def test_node_validation_too_many_kinds(self):
        """Test that nodes with more than 3 kinds raise ValueError."""
        with pytest.raises(ValueError, match="Node cannot have more than 3 kinds"):
            Node(id="test123", kinds=["Kind1", "Kind2", "Kind3", "Kind4"])

    def test_node_property_validation_primitive_types(self):
        """Test that primitive property types are accepted."""
        properties = {
            "string_prop": "test",
            "int_prop": 42,
            "float_prop": 3.14,
            "bool_prop": True,
            "none_prop": None
        }
        node = Node(id="test123", kinds=["User"], properties=properties)
        assert node.properties == properties

    def test_node_property_validation_arrays(self):
        """Test that valid array properties are accepted."""
        properties = {
            "string_array": ["item1", "item2", "item3"],
            "int_array": [1, 2, 3],
            "bool_array": [True, False, True],
            "empty_array": []
        }
        node = Node(id="test123", kinds=["User"], properties=properties)
        assert node.properties == properties

    def test_node_property_validation_reject_objects(self):
        """Test that object properties are rejected."""
        with pytest.raises(ValueError, match="cannot be an object"):
            Node(
                id="test123",
                kinds=["User"],
                properties={"nested": {"key": "value"}}
            )

    def test_node_property_validation_reject_mixed_arrays(self):
        """Test that mixed-type arrays are rejected."""
        with pytest.raises(ValueError, match="array must be homogeneous"):
            Node(
                id="test123",
                kinds=["User"],
                properties={"mixed": [1, "string", True]}
            )

    def test_node_property_validation_reject_object_arrays(self):
        """Test that arrays containing objects are rejected."""
        with pytest.raises(ValueError, match="array cannot contain objects"):
            Node(
                id="test123",
                kinds=["User"],
                properties={"objects": [{"key": "value"}]}
            )

    def test_node_to_dict_minimal(self):
        """Test converting a minimal node to dictionary."""
        node = Node(id="test123", kinds=["User"])
        result = node.to_dict()
        
        expected = {
            "id": "test123",
            "kinds": ["User"]
        }
        assert result == expected

    def test_node_to_dict_with_properties(self):
        """Test converting a node with properties to dictionary."""
        properties = {"email": "test@example.com", "active": True}
        node = Node(id="test123", kinds=["User"], properties=properties)
        result = node.to_dict()
        
        expected = {
            "id": "test123",
            "kinds": ["User"],
            "properties": properties
        }
        assert result == expected

    def test_node_to_dict_with_none_properties(self):
        """Test that None properties are excluded from dict."""
        node = Node(id="test123", kinds=["User"], properties=None)
        result = node.to_dict()
        
        expected = {
            "id": "test123",
            "kinds": ["User"]
        }
        assert result == expected

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
