import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.llm.client import ask_llm
from app.llm.schemas import LLMResponse
from app.models.client import Client
from app.models.work_history import WorkHistory


SYSTEM_PROMPT = """Ты — эксперт по сопровождению IT-инфраструктуры.
Твоя задача - предложить новые полезные регламентные работы для клиента,
у которого не хватает часов по договору. Предлагай только реальные технические
работы, которые могут принести пользу. Отвечай строго в формате JSON."""


def _build_user_prompt(client: Client, target_hours: float, history_summary: str) -> str:
    return f"""Клиент: {client.name}
Недостаток часов по договору: {target_hours:.1f} часов

История выполненных работ за последний период:
{history_summary or "нет данных"}

Предложи {settings.llm_max_suggestions} новых регламентных работ, которые:
1. Принесут реальную пользу этому клиенту.
2. Не дублируют уже выполненные работы.
3. В сумме покроют часть недостатка часов ({target_hours:.1f} ч).
4. Каждая работа — не более {settings.llm_max_hours_per_suggestion} часов.

Верни ответ строго в таком JSON-формате (без markdown, без пояснений):
{{
  "suggestions": [
    {{
      "title": "Краткое название работы",
      "description": "Что именно делается",
      "reason": "Почему это полезно именно этому клиенту",
      "estimated_hours": 4.0
    }}
  ]
}}"""


def generate_llm_suggestions(
    db: Session,
    client_id: int,
    target_hours: float,
) -> list[dict]:
    """
    Запрашивает у LLM новые предложения регламентных работ для клиента.
    Возвращает список провалидированных предложений.
    """
    client = db.execute(
        select(Client).where(Client.id == client_id)
    ).scalar_one_or_none()
    if client is None:
        raise ValueError(f"Client {client_id} not found")

    # Краткая история работ
    entries = db.execute(
        select(WorkHistory)
        .where(WorkHistory.client_id == client_id)
        .order_by(WorkHistory.spent_on.desc())
        .limit(10)
    ).scalars().all()

    history_lines = [
        f"- {e.spent_on}: {e.activity or 'работа'} — {e.hours} ч"
        for e in entries
    ]
    history_summary = "\n".join(history_lines)

    prompt = _build_user_prompt(client, target_hours, history_summary)
    raw_response = ask_llm(prompt, system_prompt=SYSTEM_PROMPT)

    # Очистка от возможных markdown-обёрток
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        validated = LLMResponse(**parsed)
    except Exception as e:
        raise ValueError(f"Не удалось распарсить ответ LLM: {e}\nОтвет: {raw_response[:500]}")

    # Ограничение по количеству и трудоёмкости (бизнес-правила)
    suggestions = []
    for s in validated.suggestions[: settings.llm_max_suggestions]:
        suggestions.append({
            "title": s.title,
            "description": s.description,
            "reason": s.reason,
            "estimated_hours": min(s.estimated_hours, settings.llm_max_hours_per_suggestion),
            "source": "LLM",
        })

    return suggestions