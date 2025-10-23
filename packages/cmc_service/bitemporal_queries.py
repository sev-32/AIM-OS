"""Bitemporal query capabilities for CMC.

Enables time-travel queries:
- as_of queries: "What was true at time T?"
- temporal range queries: "What was valid between T1 and T2?"
- transaction history: "When was this fact recorded?"
- audit trails: "Show all changes to this entity"
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from schemas.mpd import MPDNode
from schemas.edge import BitemporalEdge

from .repository import AtomRepository


class BitemporalQueryEngine:
    """Execute bitemporal queries against CMC repository."""
    
    def __init__(self, repository: AtomRepository):
        self.repo = repository
    
    def query_nodes_as_of(
        self,
        as_of_time: datetime,
        *,
        use_transaction_time: bool = False
    ) -> List[MPDNode]:
        """Query nodes as they existed at a specific point in time.
        
        Args:
            as_of_time: The point in time to query
            use_transaction_time: If True, use transaction time (when recorded)
                                 If False, use valid time (when true in reality)
        
        Returns:
            List of nodes that were valid/recorded at the specified time
            
        Example:
            # What did we know about the system on Oct 15?
            nodes = engine.query_nodes_as_of(
                datetime(2025, 10, 15),
                use_transaction_time=True
            )
        """
        conn = self.repo._conn
        cur = conn.cursor()
        
        if use_transaction_time:
            # Transaction time query: when was it recorded?
            query = """
                SELECT * FROM mpd_nodes
                WHERE tt_start <= ?
                AND (tt_end IS NULL OR tt_end > ?)
                ORDER BY mpd_id
            """
        else:
            # Valid time query: when was it true?
            query = """
                SELECT * FROM mpd_nodes
                WHERE vt_start <= ?
                AND (vt_end IS NULL OR vt_end > ?)
                ORDER BY mpd_id
            """
        
        time_iso = as_of_time.isoformat()
        rows = cur.execute(query, (time_iso, time_iso)).fetchall()
        
        return [self.repo._row_to_mpd_node(row) for row in rows]
    
    def query_edges_as_of(
        self,
        as_of_time: datetime,
        *,
        use_transaction_time: bool = False,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation: Optional[str] = None
    ) -> List[BitemporalEdge]:
        """Query edges as they existed at a specific point in time.
        
        Args:
            as_of_time: The point in time to query
            use_transaction_time: If True, use transaction time; if False, use valid time
            source_id: Optional filter by source node
            target_id: Optional filter by target node
            relation: Optional filter by relation type
            
        Returns:
            List of edges that were valid/recorded at the specified time
        """
        conn = self.repo._conn
        cur = conn.cursor()
        
        if use_transaction_time:
            query = """
                SELECT * FROM mpd_edges
                WHERE tt_start <= ?
                AND (tt_end IS NULL OR tt_end > ?)
            """
        else:
            query = """
                SELECT * FROM mpd_edges
                WHERE vt_start <= ?
                AND (vt_end IS NULL OR vt_end > ?)
            """
        
        params = [as_of_time.isoformat(), as_of_time.isoformat()]
        
        # Add optional filters
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)
        if target_id:
            query += " AND target_id = ?"
            params.append(target_id)
        if relation:
            query += " AND relation = ?"
            params.append(relation)
        
        query += " ORDER BY source_id, target_id, relation"
        
        rows = cur.execute(query, params).fetchall()
        return [self.repo._row_to_mpd_edge(row) for row in rows]
    
    def query_nodes_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
        *,
        use_transaction_time: bool = False
    ) -> List[MPDNode]:
        """Query nodes that were valid/recorded during a time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            use_transaction_time: Which time dimension to query
            
        Returns:
            Nodes that overlapped with the time range
            
        Example:
            # What was valid during October 2025?
            nodes = engine.query_nodes_in_range(
                datetime(2025, 10, 1),
                datetime(2025, 10, 31),
                use_transaction_time=False
            )
        """
        conn = self.repo._conn
        cur = conn.cursor()
        
        if use_transaction_time:
            # Transaction time range
            query = """
                SELECT * FROM mpd_nodes
                WHERE tt_start < ?
                AND (tt_end IS NULL OR tt_end > ?)
                ORDER BY mpd_id
            """
        else:
            # Valid time range
            query = """
                SELECT * FROM mpd_nodes
                WHERE vt_start < ?
                AND (vt_end IS NULL OR vt_end > ?)
                ORDER BY mpd_id
            """
        
        rows = cur.execute(
            query,
            (end_time.isoformat(), start_time.isoformat())
        ).fetchall()
        
        return [self.repo._row_to_mpd_node(row) for row in rows]
    
    def get_node_history(self, mpd_id: str) -> List[MPDNode]:
        """Get complete history of a node across all versions.
        
        Args:
            mpd_id: The node ID to get history for
            
        Returns:
            All versions of the node ordered by transaction time
            
        Example:
            # How did this node evolve?
            history = engine.get_node_history("aimos.cmc")
            for node in history:
                print(f"Version from {node.tt_start} to {node.tt_end}")
        """
        conn = self.repo._conn
        cur = conn.cursor()
        
        # Get all versions (including superseded ones)
        query = """
            SELECT * FROM mpd_nodes
            WHERE mpd_id = ?
            ORDER BY tt_start ASC
        """
        
        rows = cur.execute(query, (mpd_id,)).fetchall()
        return [self.repo._row_to_mpd_node(row) for row in rows]
    
    def query_changes_between(
        self,
        start_time: datetime,
        end_time: datetime,
        *,
        use_transaction_time: bool = True
    ) -> dict:
        """Find all changes that occurred in a time period.
        
        Args:
            start_time: Start of period
            end_time: End of period
            use_transaction_time: Query transaction time (when recorded)
            
        Returns:
            Dictionary with 'nodes_added', 'nodes_modified', 'edges_added', 'edges_modified'
            
        Example:
            # What changed last week?
            changes = engine.query_changes_between(
                datetime(2025, 10, 15),
                datetime(2025, 10, 22)
            )
            print(f"Added {len(changes['nodes_added'])} nodes")
        """
        conn = self.repo._conn
        cur = conn.cursor()
        
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()
        
        if use_transaction_time:
            # Nodes that started in this period
            nodes_added = cur.execute("""
                SELECT * FROM mpd_nodes
                WHERE tt_start >= ? AND tt_start < ?
                ORDER BY tt_start
            """, (start_iso, end_iso)).fetchall()
            
            # Nodes that ended in this period (modifications)
            nodes_modified = cur.execute("""
                SELECT * FROM mpd_nodes
                WHERE tt_end >= ? AND tt_end < ?
                ORDER BY tt_end
            """, (start_iso, end_iso)).fetchall()
            
            # Edges that started in this period
            edges_added = cur.execute("""
                SELECT * FROM mpd_edges
                WHERE tt_start >= ? AND tt_start < ?
                ORDER BY tt_start
            """, (start_iso, end_iso)).fetchall()
            
            # Edges that ended in this period
            edges_modified = cur.execute("""
                SELECT * FROM mpd_edges
                WHERE tt_end >= ? AND tt_end < ?
                ORDER BY tt_end
            """, (start_iso, end_iso)).fetchall()
        else:
            # Valid time dimension
            nodes_added = cur.execute("""
                SELECT * FROM mpd_nodes
                WHERE vt_start >= ? AND vt_start < ?
                ORDER BY vt_start
            """, (start_iso, end_iso)).fetchall()
            
            nodes_modified = cur.execute("""
                SELECT * FROM mpd_nodes
                WHERE vt_end >= ? AND vt_end < ?
                ORDER BY vt_end
            """, (start_iso, end_iso)).fetchall()
            
            edges_added = cur.execute("""
                SELECT * FROM mpd_edges
                WHERE vt_start >= ? AND vt_start < ?
                ORDER BY vt_start
            """, (start_iso, end_iso)).fetchall()
            
            edges_modified = cur.execute("""
                SELECT * FROM mpd_edges
                WHERE vt_end >= ? AND vt_end < ?
                ORDER BY vt_end
            """, (start_iso, end_iso)).fetchall()
        
        return {
            'nodes_added': [self.repo._row_to_mpd_node(r) for r in nodes_added],
            'nodes_modified': [self.repo._row_to_mpd_node(r) for r in nodes_modified],
            'edges_added': [self.repo._row_to_mpd_edge(r) for r in edges_added],
            'edges_modified': [self.repo._row_to_mpd_edge(r) for r in edges_modified],
        }
    
    def audit_trail(
        self,
        entity_id: str,
        *,
        include_edges: bool = True
    ) -> dict:
        """Complete audit trail for a node showing all changes over time.
        
        Args:
            entity_id: Node ID to audit
            include_edges: Whether to include edge changes
            
        Returns:
            Complete audit trail with all versions and timestamps
            
        Example:
            # Complete audit of authentication system
            trail = engine.audit_trail("aimos.auth")
            for version in trail['versions']:
                print(f"{version.tt_start}: {version.purpose}")
        """
        # Get all versions of the node
        versions = self.get_node_history(entity_id)
        
        result = {
            'node_id': entity_id,
            'versions': versions,
            'version_count': len(versions),
            'first_recorded': versions[0].tt_start if versions else None,
            'currently_valid': versions[-1] if versions and not versions[-1].tt_end else None
        }
        
        if include_edges:
            # Get edges involving this node
            conn = self.repo._conn
            cur = conn.cursor()
            
            # Outgoing edges
            outgoing = cur.execute("""
                SELECT * FROM mpd_edges
                WHERE source_id = ?
                ORDER BY tt_start ASC
            """, (entity_id,)).fetchall()
            
            # Incoming edges
            incoming = cur.execute("""
                SELECT * FROM mpd_edges
                WHERE target_id = ?
                ORDER BY tt_start ASC
            """, (entity_id,)).fetchall()
            
            result['outgoing_edges'] = [self.repo._row_to_mpd_edge(r) for r in outgoing]
            result['incoming_edges'] = [self.repo._row_to_mpd_edge(r) for r in incoming]
        
        return result
    
    def time_travel(
        self,
        target_time: datetime,
        *,
        use_transaction_time: bool = False
    ) -> dict:
        """Complete snapshot of the system state at a specific time.
        
        Args:
            target_time: Time to travel to
            use_transaction_time: Use transaction time vs valid time
            
        Returns:
            Complete system snapshot (all nodes and edges as of that time)
            
        Example:
            # What did the system look like on Oct 15?
            snapshot = engine.time_travel(datetime(2025, 10, 15))
            print(f"System had {len(snapshot['nodes'])} nodes")
            print(f"System had {len(snapshot['edges'])} edges")
        """
        nodes = self.query_nodes_as_of(target_time, use_transaction_time=use_transaction_time)
        edges = self.query_edges_as_of(target_time, use_transaction_time=use_transaction_time)
        
        return {
            'timestamp': target_time,
            'time_dimension': 'transaction' if use_transaction_time else 'valid',
            'nodes': nodes,
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }

