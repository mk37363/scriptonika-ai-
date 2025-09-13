import os
import requests

GIGACHAT_BASE_URL = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1")
CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

def ask_gigachat(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {CLIENT_SECRET}"}
    payload = {"model": "GigaChat", "messages": [{"role": "user", "content": prompt}]}
    response = requests.post(f"{GIGACHAT_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        return f"Error {response.status_code}: {response.text}"
