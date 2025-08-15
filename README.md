# BloodHound OpenGraph Helper Library

A Python library for creating BloodHound OpenGraph JSON data that conforms to the [BloodHound OpenGraph schema specification](https://bloodhound.specterops.io/opengraph/schema).

## Features

- **Type-safe**: Uses Python dataclasses and type hints for better code quality
- **Schema compliant**: Validates data against BloodHound OpenGraph requirements

## Installation

```bash
pip install bloodhound-opengraph
```

## Quick Start

```python
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
print(json_output)

# Or save to file
builder.save_to_file("opengraph_data.json")
```

## Core Classes

### OpenGraphBuilder
The main class for building OpenGraph structures:
- `add_node(node)`: Add a Node object
- `add_edge(edge)`: Add an Edge object  
- `create_node(id, kinds, properties=None)`: Create and add a node
- `create_edge(start_value, end_value, kind, ...)`: Create and add an edge
- `to_json(indent=2)`: Export as JSON string
- `save_to_file(filepath)`: Save to JSON file

### Node
Represents a graph node:
- `id`: Unique identifier (required)
- `kinds`: List of 0-3 kind labels (required, 0 only acceptable if source kind is set)
- `properties`: Optional dictionary of attributes

### Edge  
Represents a relationship between nodes:
- `start`: NodeReference to start node (required)
- `end`: NodeReference to end node (required)
- `kind`: Relationship type string (required)
- `properties`: Optional dictionary of attributes

### NodeReference
References a node in an edge:
- `value`: ID or name to match (required)
- `match_by`: MatchBy.ID or MatchBy.NAME (default: ID)
- `kind`: Optional kind filter

## Property Rules

Properties must follow BloodHound schema rules:
- Only primitive types: string, number, boolean
- Arrays of primitive types (must be homogeneous)
- No nested objects or arrays of objects
- Empty arrays are allowed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [SpecterOps](https://specterops.io/) for BloodHound development and documentation
