"""Isolated LLM client. Groq is the single provider; swap this module to change models."""

from __future__ import annotations

import logging

from src.config import get_groq_api_key, get_groq_model, llm_is_configured

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an enterprise knowledge assistant.
Answer the user's question using ONLY the document excerpts provided in the context.
Rules:
- Do not invent facts, policies, numbers, names, or dates.
- Do not use general knowledge that is not in the context.
- If the context does not contain enough information, say clearly that the information was not found in the available documents.
- Keep the answer concise but useful.
- Cite sources using the document names and page numbers supplied with each excerpt.
- Never pretend you read a document that is not in the context.
"""


class LLMError(Exception):
    pass


def is_available() -> bool:
    return llm_is_configured()


def generate_answer(question: str, context: str) -> str:
    if not is_available():
        raise LLMError(
            "No LLM API key is configured. Retrieval still works. "
            "Add GROQ_API_KEY to your .env file or Streamlit secrets to enable answer generation."
        )

    api_key = get_groq_api_key()
    model = get_groq_model()
    user_prompt = (
        f"Context from retrieved documents:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        "Write a grounded answer. If the context is insufficient, say so."
    )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=700,
        )
        content = response.choices[0].message.content
        if not content or not str(content).strip():
            raise LLMError("The language model returned an empty response.")
        return str(content).strip()
    except LLMError:
        raise
    except Exception as exc:
        logger.exception("Groq API call failed")
        raise LLMError(
            "The language model request failed. Check your API key, model name, and network connection."
        ) from exc
