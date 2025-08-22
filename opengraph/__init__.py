"""
BloodHound OpenGraph Helper Library

A comprehensive Python library for creating BloodHound OpenGraph JSON data 
that conforms to the BloodHound OpenGraph schema specification.

This library provides classes and methods to:
- Create nodes with properties and kinds
- Create edges between nodes
- Build complete OpenGraph JSON structures
- Validate data according to the schema requirements
"""

from .core import (
    OpenGraphBuilder,
    Node,
    Edge,
    NodeReference,
    OpenGraphMetadata,
    MatchBy
)

__version__ = "1.0.1"
__author__ = "Luke Roberts"
__email__ = "rookuu@github.com"
__license__ = "MIT"

__all__ = [
    "OpenGraphBuilder",
    "Node", 
    "Edge",
    "NodeReference",
    "OpenGraphMetadata",
    "MatchBy",
]
