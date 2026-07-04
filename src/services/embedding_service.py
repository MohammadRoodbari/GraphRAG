from openai import OpenAI

from src.config.settings import settings


class EmbeddingService:
    def __init__(self):
        self._client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=getattr(settings, "OPENAI_BASE_URL", None),
        )
        self._model = settings.EMBEDDING_MODEL

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            model=self._model,
            input=text,
        )

        return response.data[0].embedding

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            model=self._model,
            input=texts,
        )

        return [item.embedding for item in response.data]
    
    def embedding_dim(self) -> int:
        embedding = self.embed("text")

        return len(embedding)