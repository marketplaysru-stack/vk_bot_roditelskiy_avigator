"""services/telegram.py"""
import requests
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("telegram")

class TelegramClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id: int, text: str) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                return True
            else:
                logger.error(f"Ошибка отправки: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    def get_updates(self, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": 30, "allowed_updates": ["message"]}
        if offset:
            params["offset"] = offset
        try:
            resp = requests.get(url, params=params, timeout=35)
            if resp.status_code == 200:
                return resp.json().get("result", [])
            else:
                logger.error(f"Ошибка получения обновлений: {resp.status_code} {resp.text}")
                return []
        except Exception as e:
            logger.error(f"Ошибка получения обновлений: {e}")
            return []