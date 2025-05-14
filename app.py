import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple message history
chat_history = [{"role": "system", "content": "You are Lucky, a helpful assistant for the Humane Animal Welfare Society (HAWS) in Waukesha, WI."}]

def get_lucky_response(user_input):
    chat_history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )
    reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply

# Main loop for local interaction
if __name__ == "__main__":
    print("🐾 Welcome to Lucky, your HAWS Chatbot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = get_lucky_response(user_input)
        print(f"Lucky: {response}\n")
