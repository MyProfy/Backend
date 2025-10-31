import requests
import logging
from config import settings

BOT_SERVICE_URL = getattr(settings, "BOT_SERVICE_URL", "http://bot-service:8000")
BOT_SERVICE_TOKEN = getattr(settings, "BOT_SERVICE_TOKEN", None)

logger = logging.getLogger("app")

def notify_vacancy(vacancy):
    if not BOT_SERVICE_TOKEN:
        logger.warning(f"BOT_SERVICE_TOKEN не задан. Уведомление о вакансии {vacancy.id} не отправлено.")
        return

    url = f"{BOT_SERVICE_URL}/send_vacancy_notification/"
    headers = {
        "Content-Type": "application/json",
        "X-Internal-Token": BOT_SERVICE_TOKEN,
    }

    client = vacancy.client
    data = {
        "id": vacancy.id,
        "title": vacancy.title,
        "description": vacancy.description,
        "price": float(vacancy.price),
        "username": getattr(client, "telegram_username", None),
        "phone": str(getattr(client, "phone", "")) if getattr(client, "phone", None) else None,
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        logger.info(f"✅ Уведомление о вакансии {vacancy.id} отправлено боту. Ответ: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Ошибка при отправке уведомления о вакансии {vacancy.id}: {e}")
