"""
Unit tests for Edge and NodeReference classes.
"""
import pytest
from opengraph import Edge, NodeReference, MatchBy


class TestNodeReference:
    """Test cases for the NodeReference class."""

    def test_node_reference_creation_default(self):
        """Test creating a NodeReference with default values."""
        ref = NodeReference(value="test123")
        
        assert ref.value == "test123"
        assert ref.match_by == MatchBy.ID
        assert ref.kind is None

    def test_node_reference_creation_with_name_match(self):
        """Test creating a NodeReference with name matching."""
        ref = NodeReference(value="testuser", match_by=MatchBy.NAME)
        
        assert ref.value == "testuser"
        assert ref.match_by == MatchBy.NAME
        assert ref.kind is None

    def test_node_reference_creation_with_kind_filter(self):
        """Test creating a NodeReference with kind filter."""
        ref = NodeReference(value="test123", kind="User")
        
        assert ref.value == "test123"
        assert ref.match_by == MatchBy.ID
        assert ref.kind == "User"

    def test_node_reference_to_dict_minimal(self):
        """Test converting minimal NodeReference to dictionary."""
        ref = NodeReference(value="test123")
        result = ref.to_dict()
        
        expected = {
            "value": "test123",
            "match_by": "id"
        }
        assert result == expected

    def test_node_reference_to_dict_with_kind(self):
        """Test converting NodeReference with kind to dictionary."""
        ref = NodeReference(value="test123", kind="User")
        result = ref.to_dict()
        
        expected = {
            "value": "test123",
            "match_by": "id",
            "kind": "User"
        }
        assert result == expected

    def test_node_reference_to_dict_name_match(self):
        """Test converting NodeReference with name matching to dictionary."""
        ref = NodeReference(value="testuser", match_by=MatchBy.NAME, kind="Person")
        result = ref.to_dict()
        
        expected = {
            "value": "testuser",
            "match_by": "name",
            "kind": "Person"
        }
        assert result == expected


class TestEdge:
    """Test cases for the Edge class."""

    def test_edge_creation_minimal(self):
        """Test creating an edge with minimal required fields."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo")
        
        assert edge.start == start_ref
        assert edge.end == end_ref
        assert edge.kind == "ConnectedTo"
        assert edge.properties is None

    def test_edge_creation_with_properties(self):
        """Test creating an edge with properties."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        properties = {"weight": 1.5, "created_at": "2025-01-01"}
        
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=properties)
        
        assert edge.start == start_ref
        assert edge.end == end_ref
        assert edge.kind == "ConnectedTo"
        assert edge.properties == properties

    def test_edge_validation_empty_kind(self):
        """Test that edges with empty kind raise ValueError."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        
        with pytest.raises(ValueError, match="Edge must have a kind"):
            Edge(start=start_ref, end=end_ref, kind="")

    def test_edge_property_validation_primitive_types(self):
        """Test that primitive property types are accepted."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        properties = {
            "string_prop": "test",
            "int_prop": 42,
            "float_prop": 3.14,
            "bool_prop": True
        }
        
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=properties)
        assert edge.properties == properties

    def test_edge_property_validation_arrays(self):
        """Test that valid array properties are accepted."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        properties = {
            "string_array": ["item1", "item2"],
            "int_array": [1, 2, 3],
            "empty_array": []
        }
        
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=properties)
        assert edge.properties == properties

    def test_edge_property_validation_reject_objects(self):
        """Test that object properties are rejected."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        
        with pytest.raises(ValueError, match="cannot be an object"):
            Edge(
                start=start_ref,
                end=end_ref,
                kind="ConnectedTo",
                properties={"nested": {"key": "value"}}
            )

    def test_edge_property_validation_reject_mixed_arrays(self):
        """Test that mixed-type arrays are rejected."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        
        with pytest.raises(ValueError, match="array must be homogeneous"):
            Edge(
                start=start_ref,
                end=end_ref,
                kind="ConnectedTo",
                properties={"mixed": [1, "string", True]}
            )

    def test_edge_property_validation_reject_object_arrays(self):
        """Test that arrays containing objects are rejected."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        
        with pytest.raises(ValueError, match="array cannot contain objects"):
            Edge(
                start=start_ref,
                end=end_ref,
                kind="ConnectedTo",
                properties={"objects": [{"key": "value"}]}
            )

    def test_edge_to_dict_minimal(self):
        """Test converting a minimal edge to dictionary."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo")
        
        result = edge.to_dict()
        
        expected = {
            "start": {
                "value": "start123",
                "match_by": "id"
            },
            "end": {
                "value": "end456",
                "match_by": "id"
            },
            "kind": "ConnectedTo"
        }
        assert result == expected

    def test_edge_to_dict_with_properties(self):
        """Test converting an edge with properties to dictionary."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        properties = {"weight": 1.5}
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=properties)
        
        result = edge.to_dict()
        
        expected = {
            "start": {
                "value": "start123",
                "match_by": "id"
            },
            "end": {
                "value": "end456",
                "match_by": "id"
            },
            "kind": "ConnectedTo",
            "properties": {"weight": 1.5}
        }
        assert result == expected

    def test_edge_to_dict_with_none_properties(self):
        """Test that None properties are excluded from dict."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=None)
        
        result = edge.to_dict()
        
        expected = {
            "start": {
                "value": "start123",
                "match_by": "id"
            },
            "end": {
                "value": "end456",
                "match_by": "id"
            },
            "kind": "ConnectedTo"
        }
        assert result == expected

    def test_edge_with_complex_references(self):
        """Test edge with complex node references."""
        start_ref = NodeReference(value="alice", match_by=MatchBy.NAME, kind="Person")
        end_ref = NodeReference(value="server123", match_by=MatchBy.ID, kind="Computer")
        
        edge = Edge(start=start_ref, end=end_ref, kind="AdminTo")
        result = edge.to_dict()
        
        expected = {
            "start": {
                "value": "alice",
                "match_by": "name",
                "kind": "Person"
            },
            "end": {
                "value": "server123",
                "match_by": "id",
                "kind": "Computer"
            },
            "kind": "AdminTo"
        }
        assert result == expected
