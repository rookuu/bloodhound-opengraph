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

    def test_node_reference_to_dict_comprehensive(self):
        """Test converting NodeReference to dictionary in various scenarios."""
        # Minimal reference (ID match, no kind)
        ref_minimal = NodeReference(value="test123")
        assert ref_minimal.to_dict() == {"value": "test123", "match_by": "id"}
        
        # Reference with kind filter
        ref_with_kind = NodeReference(value="test123", kind="User")
        assert ref_with_kind.to_dict() == {"value": "test123", "match_by": "id", "kind": "User"}
        
        # Reference with name matching and kind
        ref_name_match = NodeReference(value="testuser", match_by=MatchBy.NAME, kind="Person")
        assert ref_name_match.to_dict() == {"value": "testuser", "match_by": "name", "kind": "Person"}


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

    def test_edge_property_validation_comprehensive(self):
        """Test edge property validation (primitive types, arrays, and rejections)."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        
        # Test valid primitive and array properties
        valid_properties = {
            "string_prop": "test",
            "int_prop": 42,
            "float_prop": 3.14,
            "bool_prop": True,
            "string_array": ["item1", "item2"],
            "int_array": [1, 2, 3],
            "empty_array": []
        }
        edge = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=valid_properties)
        assert edge.properties == valid_properties

        # Test rejection of objects
        with pytest.raises(ValueError, match="cannot be an object"):
            Edge(start=start_ref, end=end_ref, kind="ConnectedTo",
                 properties={"nested": {"key": "value"}})

        # Test rejection of mixed arrays
        with pytest.raises(ValueError, match="array must be homogeneous"):
            Edge(start=start_ref, end=end_ref, kind="ConnectedTo",
                 properties={"mixed": [1, "string", True]})

        # Test rejection of object arrays
        with pytest.raises(ValueError, match="array cannot contain objects"):
            Edge(start=start_ref, end=end_ref, kind="ConnectedTo",
                 properties={"objects": [{"key": "value"}]})

    def test_edge_to_dict_comprehensive(self):
        """Test converting edges to dictionary in various scenarios."""
        start_ref = NodeReference(value="start123")
        end_ref = NodeReference(value="end456")
        
        # Test minimal edge
        edge_minimal = Edge(start=start_ref, end=end_ref, kind="ConnectedTo")
        expected_minimal = {
            "start": {"value": "start123", "match_by": "id"},
            "end": {"value": "end456", "match_by": "id"},
            "kind": "ConnectedTo"
        }
        assert edge_minimal.to_dict() == expected_minimal

        # Test edge with properties
        properties = {"weight": 1.5}
        edge_with_props = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=properties)
        expected_with_props = expected_minimal.copy()
        expected_with_props["properties"] = {"weight": 1.5}
        assert edge_with_props.to_dict() == expected_with_props

        # Test that None properties are excluded
        edge_none_props = Edge(start=start_ref, end=end_ref, kind="ConnectedTo", properties=None)
        assert edge_none_props.to_dict() == expected_minimal

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
