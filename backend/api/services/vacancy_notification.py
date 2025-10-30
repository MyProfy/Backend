import requests
from config import settings

BOT_SERVICE_URL = getattr(settings, "BOT_SERVICE_URL", "http://bot-service:8000")
BOT_SERVICE_TOKEN = getattr(settings, "BOT_SERVICE_TOKEN", None)

def notify_vacancy(vacancy):
    if not BOT_SERVICE_TOKEN:
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
        print(f"✅ Уведомление о вакансии {vacancy.id} отправлено боту")
    except requests.RequestException as e:
        print(f"Ошибка при отправке уведомления о вакансии: {e}")
