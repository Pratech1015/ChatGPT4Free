import json
import time
import os
from playwright.sync_api import sync_playwright

class ChatGPTHybridEngine:
    def __init__(self):
        self.base_url = "https://chatgpt.com/"
        print("[Engine System] Deploying Low-Level CDP Injection Engine...")
        
        self.playwright = sync_playwright().start()
        
        # We drop all basic stealth flags and focus purely on raw browser emulation
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()
        
        print("[Engine System] Establishing direct document hook...")
        self.page.goto(self.base_url)
        time.sleep(5) 

    def stream_chat(self, prompt: str):
        """
        Bypasses the physical text input elements by evaluating native JavaScript 
        directly into the page execution context.
        """
        stream_state = {"text": "", "completed": False}

        def handle_response(response):
            if "conversation" in response.url and response.status_code == 200:
                try:
                    text_payload = response.text()
                    for line in text_payload.splitlines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                stream_state["completed"] = True
                                break
                            try:
                                data_json = json.loads(data_str)
                                parts = data_json["message"]["content"]["parts"]
                                if parts and parts[0]:
                                    new_text = parts[0]
                                    current_len = len(stream_state["text"])
                                    if len(new_text) > current_len:
                                        chunk = new_text[current_len:]
                                        print(chunk, end="", flush=True)
                                        stream_state["text"] = new_text
                            except:
                                pass
                except:
                    pass

        self.page.on("response", handle_response)

        try:
            print("[Engine System] Injecting prompt payload into JavaScript runtime...")
            
            # RAW RUNTIME INTERCEPTION:
            # We use an evaluation block to find any text fields or contenteditable divs on the page,
            # force our value directly into their state manager, and programmatically trigger the Enter event.
            self.page.evaluate(f"""
                (function() {{
                    // Locate any active input element or contenteditable block anywhere in the body
                    let inputField = document.querySelector('[placeholder*="Ask anything"]') || 
                                     document.querySelector('textarea') || 
                                     document.querySelector('[contenteditable="true"]');
                    
                    if (inputField) {{
                        if (inputField.tagName === 'DIV') {{
                            inputField.innerText = {json.dumps(prompt)};
                        }} else {{
                            inputField.value = {json.dumps(prompt)};
                        }}
                        
                        // Fire a native input event so React knows the text changed
                        inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        // Simulate a physical keypress down sequence to trip the server dispatch
                        let keyEvent = new KeyboardEvent('keydown', {{
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                        }});
                        inputField.dispatchEvent(keyEvent);
                    }}
                }})();
            """)
            
            # Keep runtime bound synchronously until stream completion indicators trip
            timeout_counter = 0
            while not stream_state["completed"] and timeout_counter < 30:
                time.sleep(0.5)
                timeout_counter += 1
                
            if timeout_counter >= 30:
                # Capture a diagnostic state image if the injected event didn't trigger a network stream
                self.page.screenshot(path="live_window_state.png", full_page=True)
                print("\n[Engine Notice] Direct injection window expired without catching server events.")
                
        except Exception as e:
            print(f"\n[Interface Error] Script injection aborted: {e}")
            
        self.page.remove_listener("response", handle_response)

    def close(self):
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
        except:
            pass