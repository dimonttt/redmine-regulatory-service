import json
import logging


from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.llm.client import ask_llm
from app.llm.schemas import LLMResponse
from app.models.client import Client
from app.models.work_history import WorkHistory

logger = logging.getLogger(__name__)
SYSTEM_PROMPT = """Ты - эксперт по сопровождению IT-инфраструктуры.
Твоя задача - предложить новые полезные регламентные работы для клиента,
у которого не хватает часов по договору. Предлагай только реальные технические
работы, которые могут принести пользу с учётом специфики клиента. 
Отвечай строго в формате JSON."""


def _build_user_prompt(client: Client, target_hours: float, history_summary: str) -> str:
    return f"""Клиент: {client.name}
Отрасль: {client.industry or "не указана"}
Описание: {client.description or "нет описания"}

Недостаток часов по договору: {target_hours:.1f} часов.

ВАЖНОЕ ОГРАНИЧЕНИЕ: суммарная трудоемкость всех предложенных тобой работ НЕ ДОЛЖНА ПРЕВЫШАТЬ {target_hours:.1f} часов. 
Предложи работы так, чтобы их сумма была максимально близка к {target_hours:.1f} часам, но не больше.

Статистика по выполненным работам:
{history_summary}

Предложи {settings.llm_max_suggestions} новых регламентных работ, которые:
1. Принесут реальную пользу этому клиенту с учётом его отрасли.
2. Не дублируют уже выполненные работы.
3. Каждая работа — не более {settings.llm_max_hours_per_suggestion} часов.

Верни ответ строго в таком JSON-формате:
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
    client = db.execute(
        select(Client).where(Client.id == client_id)
    ).scalar_one_or_none()
    if client is None:
        raise ValueError(f"Client {client_id} not found")

    entries = db.execute(
        select(WorkHistory)
        .where(WorkHistory.client_id == client_id)
        .order_by(WorkHistory.spent_on.desc())
        .limit(200)
    ).scalars().all()

    # краткая выжимка по видам деятельности
    activities_count = {}
    total_hours = 0.0
    for e in entries:
        act = e.activity or "Разное"
        activities_count[act] = activities_count.get(act, 0) + 1
        total_hours += float(e.hours)

    history_summary = f"Всего записей о работах: {len(entries)} (суммарно {total_hours:.1f} ч).\n"
    history_summary += "Чаще всего выполнялись работы видов:\n"
    for act, count in activities_count.items():
        history_summary += f"- {act} ({count} раз)\n"

    prompt = _build_user_prompt(client, target_hours, history_summary)
    raw_response = ask_llm(prompt, system_prompt=SYSTEM_PROMPT)

    # Очистка от возможных markdown-обёрток
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    if cleaned.startswith("{") and not cleaned.endswith("}"):
        # Если модель забыла закрыть массив и объект, пробуем починить
        if not cleaned.endswith("]"):
            cleaned += "]"
        cleaned += "}"

    try:
        parsed = json.loads(cleaned)
        validated = LLMResponse(**parsed)
    except Exception as e:
        logger.warning(f"Ошибка парсинга JSON (попытка 2): {e}")
        
        # Отправляем промпт еще раз с жестким указанием
        error_prompt = f"{prompt}\n\nВНИМАНИЕ: Твой предыдущий ответ был невалидным JSON! Обязательно добавь поле 'estimated_hours' и закрой все скобки."
        raw_response_2 = ask_llm(error_prompt, system_prompt=SYSTEM_PROMPT)
        
        # Очистка от markdown
        cleaned_2 = raw_response_2.strip()
        if cleaned_2.startswith("```"):
            cleaned_2 = cleaned_2.split("```")[1]
            if cleaned_2.startswith("json"):
                cleaned_2 = cleaned_2[4:]
            cleaned_2 = cleaned_2.strip()
            
        try:
            parsed = json.loads(cleaned_2)
            validated = LLMResponse(**parsed)
        except Exception as e2:
            raise ValueError(f"Не удалось распарсить ответ LLM после 2 попыток: {e2}\nОтвет: {raw_response_2[:500]}")
    
    # ограничение по количеству и трудоемкости
    suggestions = []
    total_generated_hours = 0.0
    
    for s in validated.suggestions[: settings.llm_max_suggestions]:
        if total_generated_hours + s.estimated_hours > target_hours:
            continue
            
        suggestions.append({
            "title": s.title,
            "description": s.description,
            "reason": s.reason,
            "estimated_hours": s.estimated_hours,
            "source": "LLM",
        })
        total_generated_hours += s.estimated_hours

    return suggestions