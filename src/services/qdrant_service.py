"""Qdrant service: owns the client, collection lifecycle, and vector ingestion."""

import uuid

from qdrant_client import QdrantClient, models

from src.config.settings import settings


class QdrantService:
    def __init__(self):
        self._client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_KEY)

    def create_collection(self, collection_name: str, vector_dimension: int | None = None):

        try:
            self._client.get_collection(collection_name)
            print(f"Skipping creating collection; '{collection_name}' already exists.")
        except Exception as e:
            if "Not found: Collection" in str(e) or "doesn't exist" in str(e) or "404" in str(e):
                print(f"Collection '{collection_name}' not found. Creating it now...")
                self._client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_dimension, distance=models.Distance.COSINE
                    ),
                )
                print(f"Collection '{collection_name}' created successfully.")
            else:
                print(f"Error while checking collection: {e}")

    def ingest(self, collection_name: str, node_id_mapping: dict[str, str], embeddings: list[list[float]]):
        """
        node_id_mapping: {name: node_id}
        embeddings: list of vectors, aligned by position to node_id_mapping.keys()
        """
        names = list(node_id_mapping.keys())

        self._client.upsert(
            collection_name=collection_name,
            points=[
                {
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "payload": {"id": node_id_mapping[name], "name": name},
                }
                for name, embedding in zip(names, embeddings)
            ],
        )

    @property
    def client(self):
        """Exposed so GraphRetriever can hand it to QdrantNeo4jRetriever."""
        return self._client