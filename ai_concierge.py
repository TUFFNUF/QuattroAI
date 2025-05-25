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

# Load hotel info from web_data.txt
try:
    with open("web_data.txt", "r", encoding="utf-8") as f:
        web_data = f.read()
except:
    web_data = ""

# Fallback content if web_data is empty
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
'''

# Friendly but accurate system prompt
system_instructions = f"""
You are a helpful, professional hotel concierge for Quattro Hotel.

Answer guest questions naturally, confidently, and informatively using the provided hotel info and guest reviews. You may **paraphrase, summarize, and infer** from reviews — do not quote them directly. Act like you know the hotel inside and out based on years of guest feedback and internal details.

If something isn’t mentioned at all, respond:
"I'm not certain about that at the moment. For the most accurate information, please contact the front desk by dialing ‘0’ from your room phone."

Below is your source info:

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

# Text input with button
user_input = st.text_input("Ask me anything about the hotel:", placeholder="e.g. What time is check-out?")
send = st.button("Send")

# OpenAI API setup
client = OpenAI(api_key="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")

if send and user_input:
    with st.spinner("Answering..."):

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message.content

        # Display the reply
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



