import json
import httpx

class GPTClient:
    def __init__(self, session_token: str, url: str):
        self.session_token = session_token
        self.url = url

        self.session = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {session_token}",
                "Content-Type": "application/json"
            }
        )

        self.conversation_id = None
        self.parent_message_id = None

    async def send(self, prompt: str, debug_raw: bool = True):
        payload = {
            "action": "next",
            "messages": [{
                "id": None,
                "author": {"role": "user"},
                "content": {
                    "content_type": "text",
                    "parts": [prompt]
                }
            }],
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_message_id,
            "model": "auto"
        }

        async with self.session.stream("POST", self.url, json=payload) as r:

            full_text = ""
            last_msg_id = None

            async for line in r.aiter_lines():

                # 🔴 RAW STREAM (your debug request)
                if debug_raw:
                    print(line)

                if not line:
                    continue

                if not line.startswith("data:"):
                    continue

                data = line[5:].strip()

                if data == "[DONE]":
                    break

                try:
                    obj = json.loads(data)
                except:
                    continue

                # 🔍 parsed debug
                if debug_raw:
                    print("PARSED:", obj)

                # -------------------------
                # 🧠 update conversation state
                # -------------------------
                if "conversation_id" in obj:
                    self.conversation_id = obj["conversation_id"]

                if "message" in obj and isinstance(obj["message"], dict):
                    last_msg_id = obj["message"].get("id")

                # -------------------------
                # 🧠 extract text safely
                # -------------------------
                text = ""

                msg = obj.get("message")
                if isinstance(msg, dict):
                    content = msg.get("content")

                    if isinstance(content, dict):
                        parts = content.get("parts")

                        if isinstance(parts, list):
                            text = "".join(parts)

                        elif "text" in content:
                            text = content["text"]

                # fallback formats
                if not text:
                    text = obj.get("delta") or obj.get("text") or ""

                if text:
                    print(text, end="", flush=True)
                    full_text += text

            print()

            # 🔁 update parent_message_id for next turn
            if last_msg_id:
                self.parent_message_id = last_msg_id

            return full_text