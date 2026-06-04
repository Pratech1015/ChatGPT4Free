import os
from g4f.client import Client

def main():
    print("=== Automated Auto-Routing ChatGPT Client ===")
    
    # Ensure the cache path exists
    os.makedirs("/home/codespace/.g4f/cookies", exist_ok=True)
    
    client = Client()

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue
                
            print("ChatGPT: ", end="", flush=True)
            
            # Leaving provider out forces g4f to automatically cycle through 
            # its 30+ built-in channels until it finds one that is online.
            response = client.chat.completions.create(
                model="",  # Empty string lets it pick the path of least resistance
                messages=[{"role": "user", "content": user_input}],
                stream=True,
            )
            
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
            print()

        except Exception as e:
            print(f"\n[Routing Error] This specific channel was busy: {e}")
            print("[System] Retrying automatically on next prompt...")

if __name__ == "__main__":
    main()