"""
Ingestion pipeline: raw document text -> extracted entities -> graph ->
Neo4j (structure) + Qdrant (vectors).
"""

import structlog

from src.extraction.entity_extractor import EntityExtractor
from src.graph.graph_builder import LegalGraphBuilder
from src.services.embedding_service import EmbeddingService
from src.services.neo4j_service import Neo4jService
from src.services.qdrant_service import QdrantService


logger = structlog.get_logger(__name__)


class IngestionPipeline:
    def __init__(self):
        self._entity_extractor = EntityExtractor()
        self._graph_builder = LegalGraphBuilder()
        self._neo4j_service = Neo4jService()
        self._qdrant_service = QdrantService()
        self._embedding_service = EmbeddingService()

        logger.info(
            "pipeline_initialized",
            pipeline="ingestion",
        )

    def run(self, raw_data: str, collection_name: str) -> dict[str, str]:
        logger.info("ingestion_pipeline_started", collection_name=collection_name)

        logger.info("creating_qdrant_collection", collection_name=collection_name)

        embedding_dim = self._embedding_service.embedding_dim()

        logger.debug("embedding_dimension_resolved", embedding_dimension=embedding_dim)

        self._qdrant_service.create_collection(
            collection_name,
            embedding_dim,
        )

        logger.info("extracting_entities")

        extractions = self._entity_extractor.extract(raw_data)

        logger.info("entity_extraction_completed", extraction_count=len(extractions))

        logger.info("building_graph")

        nodes, relationships = self._graph_builder.build(extractions)

        logger.info(
            "graph_build_completed",
            node_count=len(nodes),
            relationship_count=len(relationships),
        )

        logger.info("ingesting_into_neo4j")

        node_id_mapping = self._neo4j_service.ingest(
            nodes,
            relationships,
        )

        logger.info("neo4j_ingestion_completed", indexed_node_count=len(node_id_mapping))

        logger.info("generating_embeddings")

        embeddings = self._embedding_service.embed_many(
            list(node_id_mapping.keys())
        )

        logger.info("embedding_generation_completed", embedding_count=len(embeddings))

        logger.info("ingesting_into_qdrant", collection_name=collection_name)

        self._qdrant_service.ingest(
            collection_name,
            node_id_mapping,
            embeddings,
        )

        logger.info("qdrant_ingestion_completed", collection_name=collection_name)

        logger.info("ingestion_pipeline_completed",collection_name=collection_name)

        return node_id_mapping