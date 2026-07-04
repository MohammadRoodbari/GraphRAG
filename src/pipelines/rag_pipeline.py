import structlog

from src.retrieval.graph_retriever import GraphRetriever
from src.services.llm_service import LLMService


logger = structlog.get_logger(__name__)


class RAGPipeline:
    def __init__(self):
        self._graph_retriever = GraphRetriever()
        self._llm_service = LLMService()

        logger.info(
            "pipeline_initialized",
            pipeline="rag",
        )

    def run(self, query: str, collection_name: str, top_k: int = 5) -> str:
        logger.info(
            "rag_pipeline_started",
            collection_name=collection_name,
            top_k=top_k,
        )

        logger.info("retrieving_graph_context")

        graph_context = self._graph_retriever.fetch_context(collection_name, query, top_k)

        logger.info(
            "graph_context_retrieved",
            node_count=len(graph_context["nodes"]),
            edge_count=len(graph_context["edges"]),
        )

        logger.debug("graph_context_payload", graph_context=graph_context)

        logger.info("generating_answer")

        answer = self._llm_service.generate_answer(graph_context, query)

        logger.info("answer_generated")

        logger.info("rag_pipeline_completed", collection_name=collection_name)

        return answer
