import json
import uuid
from curl_cffi import requests

class ChatGPTBrokerClient:
    def __init__(self):
        self.client = requests.Session(impersonate="chrome")
        self.load_fresh_tokens()

    def load_fresh_tokens(self):
        try:
            with open("session.json", "r") as f:
                data = json.load(f)
            
            # Map dynamic browser identities directly into your raw Python client headers
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/event-stream",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://chatgpt.com/",
                "Content-Type": "application/json",
                "X-OpenAI-Target-Path": "/backend-api/f/conversation",
                "X-OpenAI-Target-Route": "/backend-api/f/conversation",
                "OAI-Device-Id": data.get("device-id", str(uuid.uuid4())),
                "OAI-Session-Id": data.get("session-id", str(uuid.uuid4())),
                "OAI-Client-Version": data.get("client-version", "prod-41183dd6bcf6c4453798fd7d7cebafa88e930320"),
                "OpenAI-Sentinel-Chat-Requirements-Token": data.get("chat-requirements-token", ""),
                "OpenAI-Sentinel-Proof-Token": data.get("proof-token", ""),
                "x-conduit-token": data.get("x-conduit-token", ""),
                "Cookie": data.get("cookie_string", ""),
                "Origin": "https://chatgpt.com",
                "Connection": "keep-alive"
            }
        except FileNotFoundError:
            raise Exception("No active session database found. Run browser.py token broker first.")

    def stream_chat(self, prompt):
        # Refresh configuration keys right before making the stream execution pass
        self.load_fresh_tokens()
        
        url = "https://chatgpt.com/backend-anon/f/conversation"
        payload = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "author": {"role": "user"},
                    "content": {"content_type": "text", "parts": [prompt]},
                    "metadata": {}
                }
            ],
            "parent_message_id": str(uuid.uuid4()),
            "model": "auto",
            "client_prepare_state": "success",
            "timezone_offset_min": -330,
            "history_and_training_disabled": True
        }

        response = self.client.post(url, headers=self.headers, json=payload, stream=True)
        
        if response.status_code != 200:
            yield f"\n[Session Expired] Status {response.status_code}. Refreshing broker mandatory."
            return

        for line in response.iter_lines():
            if not line:
                continue
            line_decoded = line.decode('utf-8')
            if line_decoded.startswith("data: "):
                data_str = line_decoded[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    data_json = json.loads(data_str)
                    parts = data_json["message"]["content"]["parts"]
                    if parts:
                        yield parts[0]
                except:
                    pass