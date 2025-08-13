#!/usr/bin/env python3
"""
Test script to validate README examples work correctly.
This ensures documentation stays in sync with the actual code.
"""
import tempfile
import os
import json

def test_readme_basic_example():
    """Test the basic example from README works end-to-end."""
    from opengraph import OpenGraphBuilder

    # Create a builder and add the README example content
    builder = OpenGraphBuilder(source_kind="MySystem")

    builder.create_node(
        id="alice@company.com",
        kinds=["User", "Person"],
        properties={
            "email": "alice@company.com",
            "displayname": "Alice Johnson",
            "active": True
        }
    )

    builder.create_node(
        id="web-server-01",
        kinds=["Computer", "Server"],
        properties={
            "hostname": "web-server-01.company.com",
            "ip_address": "10.0.1.100"
        }
    )

    builder.create_edge(
        start_value="alice@company.com",
        end_value="web-server-01",
        kind="has_admin_access",
        properties={"granted_date": "2025-01-15"}
    )

    # Test JSON export and file save functionality
    json_output = builder.to_json()
    
    # Verify basic structure and content
    assert "graph" in json_output
    assert "alice@company.com" in json_output
    assert "web-server-01" in json_output
    assert "has_admin_access" in json_output
    assert "MySystem" in json_output
    
    # Test save to file functionality
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        builder.save_to_file(temp_file)
        assert os.path.exists(temp_file)
        
        with open(temp_file, 'r') as f:
            data = json.load(f)
        
        assert "graph" in data
        assert len(data["graph"]["nodes"]) == 2
        assert len(data["graph"]["edges"]) == 1
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)