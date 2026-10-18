import json

from openai import OpenAI

from app.config import settings


def get_llm_client() -> OpenAI:
    """Возвращает клиент для OpenAI-совместимого API."""
    return OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )


def ask_llm(prompt: str, system_prompt: str | None = None) -> str:
    """Отправляет промпт в LLM и возвращает текстовый ответ."""
    client = get_llm_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""