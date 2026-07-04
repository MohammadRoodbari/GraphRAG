"""
Hybrid retrieval: vector search in Qdrant finds candidate entities, then
their neighborhood is pulled from Neo4j and flattened into a text-friendly
graph context for the LLM.

"""

from neo4j_graphrag.retrievers import QdrantNeo4jRetriever

from src.services.embedding_service import EmbeddingService
from src.services.neo4j_service import Neo4jService
from src.services.qdrant_service import QdrantService


class GraphRetriever:
    def __init__(self):
        self._neo4j_service = Neo4jService()
        self._qdrant_service = QdrantService()
        self._embedding_service = EmbeddingService()

    def search(self, collection_name: str, query: str, top_k: int = 5):
        """Vector search over Qdrant, resolved against Neo4j entity ids."""
        retriever = QdrantNeo4jRetriever(
            driver=self._neo4j_service.driver,
            client=self._qdrant_service.client,
            collection_name=collection_name,
            id_property_external="id",
            id_property_neo4j="id",
        )
        query_vector = self._embedding_service.embed(query)
        return retriever.search(query_vector=query_vector, top_k=top_k)
 
    @staticmethod
    def extract_entity_ids(retriever_result) -> list[str]:
        return [
            item.content.split("'id': '")[1].split("'")[0]
            for item in retriever_result.items
        ]
 
    @staticmethod
    def format_graph_context(subgraph: list[dict]) -> dict:
        nodes = set()
        edges = set()  # dedupe identical (source, relation, target) triples
 
        for entry in subgraph:
            entity = entry["entity"]
            related = entry["related_node"]
            relationship = entry["relationship"]
 
            nodes.add(entity["name"])
            nodes.add(related["name"])
            edges.add((entity["name"], relationship["type"], related["name"]))
 
        return {
            "nodes": sorted(nodes),
            "edges": [f"{source} {rel} {target}" for source, rel, target in sorted(edges)],
        }
 
    def fetch_context(self, collection_name: str, query: str, top_k: int = 5) -> dict:
        """End-to-end: vector search -> entity ids -> graph neighborhood -> context dict."""
        retriever_result = self.search(collection_name, query, top_k)
        entity_ids = self.extract_entity_ids(retriever_result)
        subgraph = self._neo4j_service.fetch_related_graph(entity_ids)
        return self.format_graph_context(subgraph)
 