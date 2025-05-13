import streamlit as st
import json
import os
from dotenv import load_dotenv
import openai

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load cached knowledge
def load_knowledge():
    with open("haws_knowledge.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Map to specific HAWS URLs
SECTION_URLS = {
    "SNIP Clinic": "https://hawspets.org/snip-clinic/",
    "Surrender Info": "https://hawspets.org/surrender/",
    "Lost Pet Info": "https://hawspets.org/lost-pet/",
    "Adoption Procedures": "https://hawspets.org/adoption-procedures/",
    "Foster-to-Adopt": "https://hawspets.org/foster-to-adopt/",
    "Volunteer Info": "https://hawspets.org/volunteer/",
    "Events Info": "https://hawspets.org/events/",
    "Equine Programs": "https://hawspets.org/equine-programs/",
    "Birthday Parties": "https://hawspets.givecloud.co/birthday-parties",
    "Dog Park": "https://hawspets.org/dogpark/",
    "Ways to Give": "https://hawspets.org/ways-to-give/",
    "Report Abuse": "https://hawspets.org/report-abuse/",
}

# Match input to relevant sections
def get_relevant_sections(user_input, knowledge_sections):
    input_lower = user_input.lower()
    matches = []

    keywords_map = {
        "adopt": ["adopt", "adoption", "procedures"],
        "foster": ["foster"],
        "training": ["training", "behavior"],
        "surrender": ["surrender"],
        "lost": ["lost", "missing"],
        "snip": ["snip", "spay", "neuter"],
        "volunteer": ["volunteer"],
        "events": ["event", "festival", "hawsfest"],
        "equine": ["horse", "equine"],
        "birthday": ["birthday", "party"],
        "dog park": ["dog park"],
        "donate": ["donate", "giving"],
        "report": ["report abuse"],
    }

    for section, text in knowledge_sections.items():
        for topic, keywords in keywords_map.items():
            if any(k in input_lower for k in keywords) and topic in section.lower():
                matches.append((section, text))
                break

    return matches if matches else list(knowledge_sections.items())[:3]

# Send to OpenAI
def get_lucky_response(user_input, knowledge_sections):
    sections = get_relevant_sections(user_input, knowledge_sections)
    relevant_text = "\n\n".join(f"## {title}\n{text}" for title, text in sections)
    urls = [SECTION_URLS.get(title) for title, _ in sections if title in SECTION_URLS]

    url_instruction = (
        f"You may include this helpful page if the answer is incomplete: {urls[0]}"
        if urls else ""
    )

    prompt = (
        f"You are Lucky, the chatbot for HAWS (Humane Animal Welfare Society). "
        f"You speak from an insider’s view — say 'we' or 'us'. Use the info below to answer. "
        f"{url_instruction}\n\n"
        f"{relevant_text}\n\n"
        f"User: {user_input}\nLucky:"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message["content"].strip()

# Streamlit UI
st.set_page_config(page_title="Lucky the HAWS Chatbot 🐶", page_icon="🐾")
st.title("🐶 Talk to Lucky – Your HAWS Helper")

if "chat" not in st.session_state:
    st.session_state.chat = []

knowledge = load_knowledge()

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", "")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.chat.append(("You", user_input))
    reply = get_lucky_response(user_input, knowledge)
    st.session_state.chat.append(("Lucky", reply))

# Chat log
for sender, msg in st.session_state.chat:
    st.markdown(f"**{sender}:** {msg}")
