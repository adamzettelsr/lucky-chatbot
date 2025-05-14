import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Load OpenAI API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------
# Load HAWS Knowledge Base
# -------------------------------
def load_knowledge_base(filepath="haws_knowledge.json"):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

knowledge = load_knowledge_base()

# -------------------------------
# Match Relevant Sections
# -------------------------------
def get_relevant_sections(user_input, knowledge_sections):
    input_lower = user_input.lower()
    matches = []
    for section, text in knowledge_sections.items():
        if any(word in input_lower for word in section.lower().split()):
            matches.append((section, text))
    return matches if matches else list(knowledge_sections.items())[:3]

# -------------------------------
# FAQ Override
# -------------------------------
def check_faq_overrides(user_input):
    input_lower = user_input.lower()
    keywords = [
        "adoption hours", "open tomorrow", "what time are you open",
        "when are you open", "what are your hours", "when do you close",
        "hours of operation", "shelter hours", "what time do you open",
        "are you open", "can i come tomorrow", "are you open tomorrow"
    ]
    if any(k in input_lower for k in keywords):
        return (
            "Our adoption hours are:\n"
            "- Monday to Friday: 1:00 PM – 5:00 PM\n"
            "- Saturday & Sunday: 11:00 AM – 3:00 PM\n"
            "We’d love to see you soon! 🐾"
        )
    return None

# -------------------------------
# Ask OpenAI
# -------------------------------
def ask_openai(user_input, knowledge_sections):
    override = check_faq_overrides(user_input)
    if override:
        return override

    selected = get_relevant_sections(user_input, knowledge_sections)
    relevant_text = "\n\n".join(f"## {title}\n{text}" for title, text in selected)

    prompt = (
        f"You are Lucky, the friendly chatbot at HAWS (Humane Animal Welfare Society). "
        f"You speak from an insider’s view — say 'we' or 'us'. "
        f"Answer the user's question using only the following HAWS knowledge sections. "
        f"If the info is missing or unclear, include a natural suggestion with a direct link to hawspets.org.\n\n"
        f"{relevant_text}\n\n"
        f"User: {user_input}\nLucky:"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# -------------------------------
# CLI Chat
# -------------------------------
def main():
    print("Hi! I’m Lucky 🐶 Ask me anything about HAWS — or type '!update' to refresh my brain.")
    global knowledge
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Lucky: Thanks for stopping by! We hope to see you soon 🐾")
            break
        elif user_input.strip() == "!update":
            print("Lucky: Knowledge update not supported in this version.")
            continue
        reply = ask_openai(user_input, knowledge)
        print(f"Lucky: {reply}\n")

if __name__ == "__main__":
    main()
