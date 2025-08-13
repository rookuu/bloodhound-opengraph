"""
Integration tests for the complete OpenGraph workflow.
"""
import pytest
import json
import tempfile
import os
from opengraph import OpenGraphBuilder, Node, Edge, NodeReference, MatchBy


@pytest.mark.integration
class TestOpenGraphIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow_basic(self):
        """Test a complete basic workflow from creation to JSON export."""
        builder = OpenGraphBuilder(source_kind="IntegrationTest")
        
        # Create users
        alice = builder.create_node(
            id="alice@company.com",
            kinds=["User", "Person"],
            properties={
                "email": "alice@company.com",
                "displayname": "Alice Johnson",
                "active": True,
                "department": "IT"
            }
        )
        
        bob = builder.create_node(
            id="bob@company.com",
            kinds=["User", "Person"],
            properties={
                "email": "bob@company.com",
                "displayname": "Bob Smith",
                "active": False,
                "department": "HR"
            }
        )
        
        # Create computers
        web_server = builder.create_node(
            id="web-server-01",
            kinds=["Computer", "Server"],
            properties={
                "hostname": "web-server-01.company.com",
                "ip_address": "10.0.1.100",
                "os": "Ubuntu 20.04",
                "ports": [80, 443, 22]
            }
        )
        
        db_server = builder.create_node(
            id="db-server-01",
            kinds=["Computer", "Server"],
            properties={
                "hostname": "db-server-01.company.com",
                "ip_address": "10.0.1.200",
                "os": "CentOS 8"
            }
        )
        
        # Create relationships
        builder.create_edge(
            start_value="alice@company.com",
            end_value="web-server-01",
            kind="AdminTo",
            properties={"granted_date": "2025-01-01", "permissions": ["read", "write"]}
        )
        
        builder.create_edge(
            start_value="alice@company.com",
            end_value="db-server-01",
            kind="AdminTo",
            properties={"granted_date": "2025-01-15", "permissions": ["read"]}
        )
        
        builder.create_edge(
            start_value="bob@company.com",
            end_value="web-server-01",
            kind="CanRDP",
            properties={"granted_date": "2024-12-01"}
        )
        
        # Validate the structure
        assert builder.validate() is True
        
        # Export to JSON
        json_str = builder.to_json()
        data = json.loads(json_str)
        
        # Verify structure
        assert "metadata" in data
        assert "graph" in data
        assert data["metadata"]["source_kind"] == "IntegrationTest"
        assert len(data["graph"]["nodes"]) == 4
        assert len(data["graph"]["edges"]) == 3
        
        # Verify nodes have correct structure
        for node in data["graph"]["nodes"]:
            assert "id" in node
            assert "kinds" in node
            assert isinstance(node["kinds"], list)
            assert len(node["kinds"]) >= 1
        
        # Verify edges have correct structure
        for edge in data["graph"]["edges"]:
            assert "start" in edge
            assert "end" in edge
            assert "kind" in edge
            assert "value" in edge["start"]
            assert "match_by" in edge["start"]
            assert "value" in edge["end"]
            assert "match_by" in edge["end"]

    def test_workflow_with_name_references(self):
        """Test workflow using name-based node references."""
        builder = OpenGraphBuilder(source_kind="NameRefTest")
        
        # Create nodes with name properties
        builder.create_node(
            id="user123",
            kinds=["User"],
            properties={"name": "alice", "email": "alice@test.com"}
        )
        
        builder.create_node(
            id="comp456",
            kinds=["Computer"],
            properties={"name": "webserver", "hostname": "web.test.com"}
        )
        
        # Create edge using name references
        builder.create_edge(
            start_value="alice",
            end_value="webserver",
            kind="AdminTo",
            start_match_by=MatchBy.NAME,
            end_match_by=MatchBy.NAME
        )
        
        # Should validate successfully
        assert builder.validate() is True
        
        # Export and verify
        data = json.loads(builder.to_json())
        edge = data["graph"]["edges"][0]
        assert edge["start"]["match_by"] == "name"
        assert edge["end"]["match_by"] == "name"

    def test_workflow_with_kind_filters(self):
        """Test workflow using kind filters in references."""
        builder = OpenGraphBuilder(source_kind="KindFilterTest")
        
        # Create multiple nodes with same name but different kinds
        builder.create_node(
            id="alice_user",
            kinds=["User"],
            properties={"name": "alice", "type": "user_account"}
        )
        
        builder.create_node(
            id="alice_computer",
            kinds=["Computer"],
            properties={"name": "alice", "type": "workstation"}
        )
        
        builder.create_node(
            id="server01",
            kinds=["Computer", "Server"],
            properties={"hostname": "server01.test.com"}
        )
        
        # Create edges with kind filters to disambiguate
        builder.create_edge(
            start_value="alice",
            end_value="server01",
            kind="AdminTo",
            start_match_by=MatchBy.NAME,
            start_kind="User",
            end_match_by=MatchBy.ID
        )
        
        builder.create_edge(
            start_value="alice",
            end_value="server01",
            kind="ConnectedTo",
            start_match_by=MatchBy.NAME,
            start_kind="Computer",
            end_match_by=MatchBy.ID
        )
        
        # Should validate successfully
        assert builder.validate() is True
        
        # Export and verify
        data = json.loads(builder.to_json())
        assert len(data["graph"]["edges"]) == 2
        
        # Both edges should have kind filters
        for edge in data["graph"]["edges"]:
            if edge["kind"] == "AdminTo":
                assert edge["start"]["kind"] == "User"
            elif edge["kind"] == "ConnectedTo":
                assert edge["start"]["kind"] == "Computer"

    def test_large_graph_performance(self):
        """Test performance with a larger graph."""
        builder = OpenGraphBuilder(source_kind="PerformanceTest")
        
        # Create 100 users
        for i in range(100):
            builder.create_node(
                id=f"user{i:03d}",
                kinds=["User"],
                properties={
                    "email": f"user{i:03d}@test.com",
                    "active": i % 2 == 0
                }
            )
        
        # Create 50 computers
        for i in range(50):
            builder.create_node(
                id=f"comp{i:03d}",
                kinds=["Computer"],
                properties={
                    "hostname": f"comp{i:03d}.test.com",
                    "ip": f"192.168.1.{i+1}"
                }
            )
        
        # Create relationships (each user to 2-3 computers)
        edge_count = 0
        for user_i in range(100):
            for comp_i in range(min(3, 50)):
                if (user_i + comp_i) % 7 != 0:  # Skip some for variety
                    continue
                builder.create_edge(
                    start_value=f"user{user_i:03d}",
                    end_value=f"comp{(comp_i + user_i) % 50:03d}",
                    kind="CanLogin"
                )
                edge_count += 1
        
        # Validate
        assert builder.validate() is True
        assert builder.get_node_count() == 150
        assert builder.get_edge_count() == edge_count
        
        # Export to JSON
        json_str = builder.to_json()
        data = json.loads(json_str)
        
        assert len(data["graph"]["nodes"]) == 150
        assert len(data["graph"]["edges"]) == edge_count

    def test_file_integration_workflow(self):
        """Test saving to file and verifying the output (integration with filesystem)."""
        builder = OpenGraphBuilder(source_kind="FileSaveTest")
        
        # Create sample data
        builder.create_node(id="test_user", kinds=["User"], properties={"email": "test@example.com"})
        builder.create_node(id="test_computer", kinds=["Computer"], properties={"hostname": "test.local"})
        builder.create_edge("test_user", "test_computer", "AdminTo")
        
        # Save to temporary file and verify integration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            builder.save_to_file(temp_file)
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r') as f:
                data = json.load(f)
            
            # Integration test: verify complete workflow worked end-to-end
            assert data["metadata"]["source_kind"] == "FileSaveTest"
            assert len(data["graph"]["nodes"]) == 2
            assert len(data["graph"]["edges"]) == 1
            
            user_node = next(n for n in data["graph"]["nodes"] if n["id"] == "test_user")
            assert user_node["kinds"] == ["User"]
            assert user_node["properties"]["email"] == "test@example.com"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @pytest.mark.slow
    def test_stress_test_many_validations(self):
        """Stress test with many validation calls (integration performance test)."""
        builder = OpenGraphBuilder(source_kind="StressTest")
        
        # Add nodes incrementally and validate each time
        for i in range(50):
            builder.create_node(id=f"node{i}", kinds=["TestNode"], properties={"index": i})
            # Validate after each addition
            assert builder.validate() is True
        
        # Add edges and validate
        for i in range(25):
            builder.create_edge(f"node{i}", f"node{i+25}", "ConnectedTo")
            # Validate after each edge addition
            assert builder.validate() is True
        
        # Final validation
        assert builder.get_node_count() == 50
        assert builder.get_edge_count() == 25
        assert builder.validate() is True
