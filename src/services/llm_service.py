"""LLM service: wraps the chat-completion call that turns graph context into an answer."""

import textwrap

from openai import OpenAI

from src.config.settings import settings


class LLMService:
    def __init__(self):
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self._model = settings.LLM_MODEL

    def generate_answer(self, graph_context: dict, user_query: str) -> str:
        nodes_str = ", ".join(graph_context["nodes"])
        edges_str = "; ".join(graph_context["edges"])

        prompt = f"""
        You are a highly accurate GraphRAG assistant specialized in legal and regulatory documents.

        You must answer questions strictly based on the provided knowledge graph.

        GRAPH CONTEXT

        Nodes:
        {nodes_str}

        Edges:
        {edges_str}

        Reasoning Rules:
        - Use node relationships as the primary source of reasoning.
        - Combine connected entities when forming the answer.
        - Preserve legal and regulatory terminology accurately.
        - Include exceptions, conditions, and special cases if present in the graph.
        - Do not invent missing facts.
        - If information is incomplete, explicitly state that the graph lacks sufficient data.

        Question:
        {user_query}

        Grounded Answer:
        """


        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Provide the answer for the following question:"},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error querying LLM: {str(e)}"