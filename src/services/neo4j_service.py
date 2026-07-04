"""Neo4j service: owns the driver connection and all graph read/write operations."""

from neo4j import GraphDatabase

from src.config.settings import settings
from src.utils import sanitize_relationship_type


class Neo4jService:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )

    def ingest(self, nodes: dict[str, str], relationships: list[dict]) -> dict[str, str]:
        """
        Create Entity nodes and typed relationships in Neo4j.

        nodes: {name: node_id}
        relationships: [{"source": id, "target": id, "type": str}, ...]
        """
        with self._driver.session() as session:
            for name, node_id in nodes.items():
                session.run(
                    "CREATE (n:Entity {id: $id, name: $name})",
                    id=node_id,
                    name=name,
                )

            for relationship in relationships:
                rel_type = sanitize_relationship_type(relationship["type"])
                session.run(
                    "MATCH (a:Entity {id: $source_id}), (b:Entity {id: $target_id}) "
                    f"CREATE (a)-[:{rel_type} {{type: $type}}]->(b)",
                    source_id=relationship["source"],
                    target_id=relationship["target"],
                    type=relationship["type"],
                )

        return nodes

    def fetch_related_graph(self, entity_ids: list[str], limit: int = 200) -> list[dict]:
        """Fetch a 2-hop neighborhood around the given entity ids.

        DISTINCT collapses rows produced when several starting entities
        share the same neighbor (a very common case in a dense legal
        graph); `limit` caps the total relationships returned so a single
        query can't blow up the context with a huge neighborhood.
        """
        query = """
        MATCH (e:Entity)-[r1]-(n1)-[r2]-(n2)
        WHERE e.id IN $entity_ids
        RETURN DISTINCT e, r1 as r, n1 as related, r2, n2
        UNION
        MATCH (e:Entity)-[r]-(related)
        WHERE e.id IN $entity_ids
        RETURN DISTINCT e, r, related, null as r2, null as n2
        LIMIT $limit
        """
        with self._driver.session() as session:
            result = session.run(query, entity_ids=entity_ids, limit=limit)
            subgraph = []
            for record in result:
                subgraph.append(
                    {
                        "entity": record["e"],
                        "relationship": record["r"],
                        "related_node": record["related"],
                    }
                )
                if record["r2"] and record["n2"]:
                    subgraph.append(
                        {
                            "entity": record["related"],
                            "relationship": record["r2"],
                            "related_node": record["n2"],
                        }
                    )
        return subgraph

    @property
    def driver(self):
        """Exposed so GraphRetriever can hand it to QdrantNeo4jRetriever."""
        return self._driver

    def close(self):
        self._driver.close()