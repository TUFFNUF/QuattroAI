import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
from io import BytesIO

# Load the Quattro Hotel logo
logo = Image.open("quattro-logo.png")

def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

logo_base64 = image_to_base64(logo)

st.set_page_config(page_title="Quattro Hotel", page_icon=logo, layout="centered")

# Top 100 most spoken languages + Other
language_options = [
    "English", "Mandarin Chinese", "Hindi", "Spanish", "French", "Standard Arabic", "Bengali", "Russian", "Portuguese", "Urdu",
    "Indonesian", "German", "Japanese", "Swahili", "Marathi", "Telugu", "Turkish", "Tamil", "Punjabi", "Wu Chinese",
    "Korean", "Vietnamese", "Javanese", "Gujarati", "Polish", "Ukrainian", "Persian (Farsi)", "Malayalam", "Kannada", "Oriya",
    "Maithili", "Thai", "Hausa", "Burmese", "Romanian", "Dutch", "Cebuano", "Serbo-Croatian", "Sindhi", "Amharic",
    "Hungarian", "Azerbaijani", "Fula", "Igbo", "Uzbek", "Nepali", "Tagalog", "Yoruba", "Malagasy", "Hebrew",
    "Zulu", "Greek", "Tigrinya", "Chichewa", "Kazakh", "Belarusian", "Quechua", "Kinyarwanda", "Swedish", "Haitian Creole",
    "Finnish", "Slovak", "Danish", "Norwegian", "Bulgarian", "Catalan", "Slovenian", "Croatian", "Bosnian", "Lithuanian",
    "Latvian", "Estonian", "Albanian", "Macedonian", "Armenian", "Georgian", "Tajik", "Pashto", "Khmer", "Mongolian",
    "Lao", "Kurdish", "Basque", "Galician", "Sundanese", "Assamese", "Madurese", "Somali", "Tatar", "Sinhala",
    "Irish", "Scottish Gaelic", "Welsh", "Xhosa", "Setswana", "Sesotho", "Tsonga", "Luxembourgish", "Icelandic", "Malti",
    "Other"
]

# Language selection
selected_lang = st.selectbox("Choose your language:", language_options)
if selected_lang == "Other":
    custom_lang = st.text_input("Enter your preferred language:")
    lang_choice = custom_lang.strip() if custom_lang.strip() else "English"
else:
    lang_choice = selected_lang

# Load hotel info
try:
    with open("web_data.txt", "r", encoding="utf-8") as f:
        web_data = f.read()
except:
    web_data = ""

if not web_data.strip():
    web_data = '''
Quattro Hotel Overview:
- Address: 229 Great Northern Road, Sault Ste. Marie, ON P6B 4Z2
- Phone: 705-942-2500 or 800-563-7262
- Location: Uptown Sault Ste. Marie, near restaurants and downtown

Amenities:
• Indoor saltwater pool & sauna
• Spa: Greenhouse Spa (in-house massage & wellness center)
• Free Wi-Fi
• Free hot breakfast
• Fitness centre
• On-site restaurant & bar

Dining:
• Vinotecca – Fine dining
• PizzaTecca – Take-out
• Q-Patio – Outdoor seasonal patio

Nearby Restaurants (Walking Distance):
• Burger Don – Gourmet burgers and craft sodas, 2-minute walk from the hotel
• McDonald’s – Fast food, located next door
• Montana’s BBQ & Bar – Casual dining with ribs, burgers, and beer, 5-minute walk
• Tim Hortons – Coffee and quick bites, across the street
• Giovanni’s – Well-known local Italian restaurant, just down the road
• Wendy’s – Quick service, around the corner from the hotel
• Subway – Sandwiches and wraps, nearby on Great Northern Road
'''

# System prompt with strict language enforcement
system_instructions = f"""
You are a helpful, multilingual hotel concierge for Quattro Hotel.

Use the hotel information below to answer guest questions accurately. You may summarize or paraphrase, but do not invent features not found in the data.

IMPORTANT: Translate all replies into this language: {lang_choice}.
Do NOT respond in English unless English is explicitly selected.
Even fallback responses must be fully translated into {lang_choice}.

If the answer is not available in the provided info, respond with:
"I'm not certain about that at the moment. For the most accurate information, please contact the front desk by dialing ‘0’ from your room phone."
— but **translate that sentence** fully into {lang_choice}.

Hotel Info:
{web_data}
"""

# Title and logo
st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-top: 30px; gap: 12px;">
        <h2 style="margin: 0;">QuattroAI Concierge</h2>
        <img src="data:image/png;base64,{logo_base64}" style="height: 65px; margin-bottom: 4px;" />
    </div>
    """,
    unsafe_allow_html=True
)

# Input
user_input = st.text_input("Ask me anything about the hotel:", placeholder="e.g. What time is check-out?")
send = st.button("Send")

# OpenAI API setup
client = OpenAI(api_key="change later")

if send and user_input:
    with st.spinner("Answering..."):

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "assistant", "content": f"I will now respond only in {lang_choice}."},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3
        )

        reply = response.choices[0].message.content

        st.markdown(
            f"""
            <div style='margin-top: 30px; font-size: 18px; max-width: 600px; margin-left: auto; margin-right: auto;'>
                <strong>Answer:</strong><br>{reply}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Log unanswered questions
        if "contact the front desk" in reply.lower() and user_input and len(user_input.strip()) > 2:
            try:
                with open("unanswered_questions.txt", "a", encoding="utf-8") as f:
                    f.write(user_input.strip() + "\n")
            except Exception as e:
                st.warning(f"⚠️ Could not log unanswered question: {e}")
