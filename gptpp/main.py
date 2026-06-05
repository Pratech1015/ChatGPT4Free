import sys
from client import ChatGPTHybridEngine

def main():
    print("=================================================")
    print("      DIRECT REVERSE CHATGPT INTERACTION CORE    ")
    print("=================================================")
    
    bot = ChatGPTHybridEngine()

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            print("ChatGPT: ", end="", flush=True)
            bot.stream_chat(user_input)
            print() # Insert fresh line break post-stream completion

        except KeyboardInterrupt:
            break
            
    print("\nShutting down network systems...")
    bot.close()
    print("Goodbye!")

if __name__ == "__main__":
    main()