import json
from playwright.sync_api import sync_playwright

def fetch_fresh_session():
    print("[Broker] Spinning up background token collector...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        session_data = {}

        # Capture tokens flying through the staging network requests
        def handle_request(request):
            if "backend-anon" in request.url or "conversation" in request.url:
                headers = request.headers
                if "x-conduit-token" in headers:
                    session_data["x-conduit-token"] = headers["x-conduit-token"]
                if "openai-sentinel-chat-requirements-token" in headers:
                    session_data["chat-requirements-token"] = headers["openai-sentinel-chat-requirements-token"]
                if "openai-sentinel-proof-token" in headers:
                    session_data["proof-token"] = headers["openai-sentinel-proof-token"]
                if "oai-device-id" in headers:
                    session_data["device-id"] = headers["oai-device-id"]
                if "oai-session-id" in headers:
                    session_data["session-id"] = headers["oai-session-id"]
                if "oai-client-version" in headers:
                    session_data["client-version"] = headers["oai-client-version"]

        page.on("request", handle_request)

        # 1. Navigate to landing page to warm cookies and trigger basic Turnstile
        page.goto("https://chatgpt.com/")
        page.wait_for_selector("#prompt-textarea", timeout=15000)
        
        # 2. Trigger the /conversation/prepare step using browser JavaScript context
        # This tells OpenAI to generate an unused token pool without sending a message
        print("[Broker] Triggering token preparation staging...")
        page.evaluate("""() => {
            fetch('https://chatgpt.com/backend-anon/f/conversation/prepare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'x-conduit-token': 'no-token' },
                body: JSON.stringify({})
            }).catch(() => {});
        }""")
        
        # Give the background fetch call 4 seconds to resolve and be caught by handle_request
        page.wait_for_timeout(4000)

        cookies = context.cookies()
        cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        session_data["cookie_string"] = cookie_string
        browser.close()

        if "x-conduit-token" in session_data and session_data["x-conduit-token"] != "no-token":
            with open("session.json", "w") as f:
                json.dump(session_data, f, indent=4)
            print("[Broker] Fresh UNUSED tokens saved to session.json.")
            return True
        else:
            print("[Broker] Staging handshake missed. Cloudflare Turnstile block.")
            return False

if __name__ == "__main__":
    fetch_fresh_session()