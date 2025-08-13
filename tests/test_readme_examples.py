#!/usr/bin/env python3
"""
Test script to validate README examples work correctly.
This ensures documentation stays in sync with the actual code.
"""

def test_readme_basic_example():
    """Test the basic example from README."""
    from opengraph import OpenGraphBuilder

    # Create a builder
    builder = OpenGraphBuilder(source_kind="MySystem")

    # Add nodes
    user = builder.create_node(
        id="alice@company.com",
        kinds=["User", "Person"],
        properties={
            "email": "alice@company.com",
            "displayname": "Alice Johnson",
            "active": True
        }
    )

    server = builder.create_node(
        id="web-server-01",
        kinds=["Computer", "Server"],
        properties={
            "hostname": "web-server-01.company.com",
            "ip_address": "10.0.1.100"
        }
    )

    # Add relationships
    builder.create_edge(
        start_value="alice@company.com",
        end_value="web-server-01",
        kind="has_admin_access",
        properties={"granted_date": "2025-01-15"}
    )

    # Export as JSON
    json_output = builder.to_json()
    
    # Basic validations
    assert "graph" in json_output
    assert "nodes" in json_output  
    assert "edges" in json_output
    assert "alice@company.com" in json_output
    assert "web-server-01" in json_output
    assert "has_admin_access" in json_output
    assert "MySystem" in json_output
    
    print("✅ README basic example works correctly")

    # Test save to file functionality
    import tempfile
    import os
    import json
    
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
        
        print("✅ README save_to_file example works correctly")
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)