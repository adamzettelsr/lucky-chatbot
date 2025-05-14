import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load knowledge base
def load_knowledge_base(filepath="haws_knowledge.json"):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

knowledge = load_knowledge_base()

# Fallback override for FAQ-style questions
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

# Match relevant content based on input
def get_relevant_sections(user_input, knowledge_sections):
    input_lower = user_input.lower()
    matches = []

    keywords_map = {
        "adopt": ["adopt", "adoption", "adoptable", "procedures", "resources", "sanctuary"],
        "foster": ["foster", "foster-to-adopt"],
        "training": ["training", "behavior", "classes"],
        "surrender": ["surrender", "give up", "rehoming"],
        "lost": ["lost", "missing pet", "found", "microchip"],
        "snip": ["snip", "spay", "neuter", "clinic"],
        "volunteer": ["volunteer", "help out", "get involved"],
        "events": ["event", "festival", "hawsfest", "hooves", "tails", "flights"],
        "education": ["education", "camp", "kids", "birthday", "activities", "field trip"],
        "equine": ["horse", "equine"],
        "dog park": ["dog park", "run", "play area"],
        "rescue": ["rescue", "emergency", "team"],
        "donate": ["donate", "giving", "membership", "planned", "corporate"],
        "about": ["about", "mission", "history", "leadership", "who we are"],
        "contact": ["contact", "careers", "report abuse", "news", "email", "phone"],
        "future": ["future", "planning", "estate"],
        "safe keep": ["safe keep", "temporary", "safe housing"]
    }

    for section, text in knowledge_sections.items():
        for topic, keywords in keywords_map.items():
            if any(keyword in input_lower for keyword in keywords):
                if topic in section.lower():
                    matches.append((section, text))
                    break

    return matches if matches else list(knowledge_sections.items())[:3]

# Ask OpenAI with HAWS context
def ask_openai(user_input, knowledge_sections):
    override = check_faq_overrides(user_input)
    if override:
        return override

    selected = get_relevant_sections(user_input, knowledge_sections)
    relevant_text = "\n\n".join(f"## {title}\n{text}" for title, text in selected)

    section_url_map = {
        "Adoption Info": "https://hawspets.org/adopt/",
        "Adoption Procedures": "https://hawspets.org/adoption-procedures/",
        "Adoption Resources": "https://hawspets.org/adoption-resources/",
        "Foster-to-Adopt": "https://hawspets.org/foster-to-adopt/",
        "Seeking Sanctuary": "https://hawspets.org/seeking-sanctuary/",
        "Training & Behavior": "https://hawspets.org/training-behavior/",
        "SNIP Clinic": "https://hawspets.org/snip-clinic/",
        "Surrender Info": "https://hawspets.org/surrender/",
        "Lost Pet Info": "https://hawspets.org/lost-pet/",
        "Safe Keep Program": "https://hawspets.org/safe-keep/",
        "Pet Future Planning": "https://hawspets.org/planning-your-pets-future/",
        "Volunteer Info": "https://hawspets.org/volunteer/",
        "Events Info": "https://hawspets.org/events/",
        "Camp & Kids": "https://hawspets.org/activities-for-kids/",
        "Birthday Parties": "https://hawspets.givecloud.co/birthday-parties",
        "Equine Programs": "https://hawspets.org/equine-programs/",
        "Dog Park": "https://hawspets.org/dogpark/",
        "Animal Rescue Team": "https://hawspets.org/animal-rescue/",
        "Ways to Give": "https://hawspets.org/ways-to-give/",
        "Corporate Giving": "https://hawspets.org/corporate-giving/",
        "About HAWS": "https://hawspets.org/about/",
        "HAWS Leadership": "https://hawspets.org/leadership/",
        "Contact Info": "https://hawspets.org/contact/",
        "Careers": "https://hawspets.org/careers/",
        "Report Abuse": "https://hawspets.org/report-abuse/"
    }

    included_urls = [
        section_url_map[title]
        for title, _ in selected if title in section_url_map
    ]

    url_instruction = (
        f"If you're unable to fully answer the question, include a link to the most relevant section like "
        f"{included_urls[0]} — only use one link, and make sure it directly relates to the question being asked. "
        "Phrase it naturally, in a friendly tone."
    ) if included_urls else ""

    prompt = (
        f"You are Lucky, the friendly chatbot at HAWS (Humane Animal Welfare Society). "
        f"You speak from an insider’s view — say 'we' or 'us'. "
        f"Answer the user's question using only the following HAWS knowledge sections. "
        f"If the info is missing or unclear, include a natural suggestion with a direct link to the most relevant page — "
        f"but only if it's related to the answer.\n\n"
        f"{url_instruction}\n\n"
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

# Streamlit UI
st.set_page_config(page_title="Lucky Chatbot 🐾", layout="centered")
st.title("🐶 Lucky the HAWS Chatbot")
st.markdown("Ask Lucky a question about adoptions, fostering, events, and more at [hawspets.org](https://hawspets.org)!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", placeholder="Ask me anything about HAWS...")

if user_input:
    with st.spinner("Lucky is thinking..."):
        response = ask_openai(user_input, knowledge)
        st.markdown(f"**Lucky:** {response}")
