from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str

    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str

    QDRANT_URL: str
    QDRANT_KEY: str

    LLM_MODEL: str
    EMBEDDING_MODEL: str

    class Config:
        env_file = ".env"


settings = Settings()