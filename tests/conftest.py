"""
Test configuration and shared fixtures.
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from opengraph import (
    OpenGraphBuilder,
    Node,
    Edge,
    NodeReference,
    MatchBy
)


@pytest.fixture
def sample_user_node():
    """Create a sample user node for testing."""
    return Node(
        id="user123",
        kinds=["User", "Person"],
        properties={
            "email": "test@example.com",
            "displayname": "Test User",
            "active": True,
            "roles": ["admin", "developer"]
        }
    )


@pytest.fixture
def sample_computer_node():
    """Create a sample computer node for testing."""
    return Node(
        id="computer456",
        kinds=["Computer", "Server"],
        properties={
            "hostname": "test-server.local",
            "ip_address": "192.168.1.100",
            "os": "Ubuntu 20.04"
        }
    )


@pytest.fixture
def sample_edge(sample_user_node, sample_computer_node):
    """Create a sample edge for testing."""
    return Edge(
        start=NodeReference(value=sample_user_node.id, match_by=MatchBy.ID),
        end=NodeReference(value=sample_computer_node.id, match_by=MatchBy.ID),
        kind="AdminTo",
        properties={
            "granted_date": "2025-01-01",
            "permissions": ["read", "write", "execute"]
        }
    )


@pytest.fixture
def builder():
    """Create a fresh OpenGraphBuilder instance."""
    return OpenGraphBuilder(source_kind="TestSystem")


@pytest.fixture
def populated_builder(builder, sample_user_node, sample_computer_node, sample_edge):
    """Create a builder with sample data."""
    builder.add_node(sample_user_node)
    builder.add_node(sample_computer_node)
    builder.add_edge(sample_edge)
    return builder


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        yield f.name
    # Clean up after test
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def sample_json_data():
    """Sample JSON data that matches the BloodHound OpenGraph schema."""
    return {
        "metadata": {
            "source_kind": "TestSystem"
        },
        "graph": {
            "nodes": [
                {
                    "id": "user123",
                    "kinds": ["User", "Person"],
                    "properties": {
                        "email": "test@example.com",
                        "displayname": "Test User",
                        "active": True
                    }
                },
                {
                    "id": "computer456",
                    "kinds": ["Computer"],
                    "properties": {
                        "hostname": "test-computer.local"
                    }
                }
            ],
            "edges": [
                {
                    "start": {
                        "value": "user123",
                        "match_by": "id"
                    },
                    "end": {
                        "value": "computer456",
                        "match_by": "id"
                    },
                    "kind": "AdminTo",
                    "properties": {
                        "granted_date": "2025-01-01"
                    }
                }
            ]
        }
    }


@pytest.fixture
def invalid_property_values():
    """Invalid property values for testing validation."""
    return [
        {"nested_object": {"key": "value"}},  # Nested object
        {"mixed_array": [1, "string", True]},  # Mixed array
        {"object_array": [{"key": "value"}]},  # Array of objects
    ]


# Helper functions for tests
def assert_valid_json_structure(json_data: Dict[str, Any]):
    """Assert that JSON data has the expected OpenGraph structure."""
    assert "graph" in json_data
    assert "nodes" in json_data["graph"]
    assert "edges" in json_data["graph"]
    assert isinstance(json_data["graph"]["nodes"], list)
    assert isinstance(json_data["graph"]["edges"], list)


def assert_valid_node_structure(node_data: Dict[str, Any]):
    """Assert that node data has the expected structure."""
    assert "id" in node_data
    assert "kinds" in node_data
    assert isinstance(node_data["id"], str)
    assert isinstance(node_data["kinds"], list)
    assert len(node_data["kinds"]) >= 1
    assert len(node_data["kinds"]) <= 3


def assert_valid_edge_structure(edge_data: Dict[str, Any]):
    """Assert that edge data has the expected structure."""
    assert "start" in edge_data
    assert "end" in edge_data
    assert "kind" in edge_data
    assert isinstance(edge_data["kind"], str)
    
    # Validate node references
    for ref_key in ["start", "end"]:
        ref = edge_data[ref_key]
        assert "value" in ref
        assert "match_by" in ref
        assert isinstance(ref["value"], str)
        assert ref["match_by"] in ["id", "name"]
