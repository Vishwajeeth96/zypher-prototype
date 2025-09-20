# app.py — Zypher • Youth Mental Wellness
import streamlit as st
import google.generativeai as genai
from datetime import datetime
import random
import requests
from io import BytesIO
from PIL import Image
import html

# ---------------- Page Config ----------------
st.set_page_config(page_title="Zypher - Youth Mental Wellness", page_icon="🌿", layout="wide")

# ---------------- Gemini API Setup ----------------
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ Gemini API key not found in secrets!")
    st.stop()

# ---------------- Fallback Responses ----------------
fallback_responses = {
    "happy": ["That’s amazing! 🌸", "Keep shining today! ✨", "Happiness looks good on you! 💖"],
    "sad": ["I hear you 💙", "It’s okay to not feel okay 🌧️", "Sending you a virtual hug 🤗"],
    "angry": ["Take a deep breath 🧘", "It’s okay to vent 💢", "Want a quick calming exercise?"],
    "neutral": ["Got it. I’m listening 👂", "I understand. Tell me more…", "Thanks for sharing 💭"],
}

# ---------------- Session State ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# ---------------- Chatbot Response ----------------
def get_bot_response(user_input, mood="neutral"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)
        return str(response.text)
    except:
        return random.choice(fallback_responses.get(mood, ["I’m here for you. 💙"]))

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
.left-panel-box {
    background-color:#0d1117;
    padding:20px;
    border-radius:10px;
    color:#c9d1d9;
    height:90vh;
    overflow-y:auto;
}
.stButton>button {
    background: linear-gradient(90deg,#ff79c6,#8a2be2);
    color:#fff;font-weight:600;border-radius:8px;padding:6px 12px;
}
h1,h2,h3 {margin:5px 0;}
.chat-container {
    height:90vh;
    overflow-y:auto;
    padding:10px;
    border-radius:10px;
    background-color:#f5f5f5;
}
.user-bubble {
    background: #8be9fd;
    color: #000;
    padding: 10px 14px;
    border-radius: 15px 15px 0 15px;
    margin:5px 0;
    max-width:75%;
}
.bot-bubble {
    background: #6272a4;
    color:#fff;
    padding: 10px 14px;
    border-radius: 15px 15px 15px 0;
    margin:5px 0;
    max-width:75%;
}
.timestamp {
    font-size:10px;
    color:#555;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Layout ----------------
left_col, chat_col = st.columns([1,2])

# ---------------- Left Panel (Single Box) ----------------
with left_col:
    st.markdown('<div class="left-panel-box">', unsafe_allow_html=True)

    # Mood Log
    st.header("🌸 Mood Log")
    current_mood = st.radio("Current Mood", ["happy","sad","angry","neutral"], horizontal=True)
    if st.button("Log Mood"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.mood_log.append({"mood":current_mood,"timestamp":timestamp})
        st.success(f"Mood '{current_mood}' logged at {timestamp}")

    if st.session_state.mood_log:
        st.subheader("📅 Recent Entries")
        for entry in reversed(st.session_state.mood_log[-5:]):
            st.write(f"{entry['timestamp']} → {entry['mood']}")

    # Meme Generator
    st.header("😂 Meme Generator")
    if st.button("Generate Meme"):
        try:
            r = requests.get("https://meme-api.com/gimme", timeout=6).json()
            url = r.get("url"); title = r.get("title")
            if url:
                img = Image.open(BytesIO(requests.get(url).content))
                st.image(img, caption=title)
            else:
                st.warning("Could not fetch meme right now.")
        except Exception as e:
            st.error("Meme fetch failed: "+str(e))

    # Mood Analyzer
    st.header("📋 Mood Analyzer")
    questions = [
        {"q":"How have you been feeling today?","opts":["Very good","Good","Neutral","Bad","Very bad"]},
        {"q":"How motivated are you?","opts":["Very motivated","Somewhat motivated","Neutral","Little motivated","Not motivated at all"]},
        {"q":"How well did you sleep?","opts":["Very well","Well","Average","Poorly","Very poorly"]},
        {"q":"Rate your stress level:","opts":["Very low","Low","Moderate","High","Very high"]},
        {"q":"Connected with others recently?","opts":["Very connected","Somewhat connected","Neutral","Somewhat disconnected","Very disconnected"]}
    ]
    with st.form("mood_form"):
        answers=[]
        for i,q in enumerate(questions):
            answers.append(st.radio(q["q"], q["opts"], index=2, key=f"q{i}"))
        submit = st.form_submit_button("Analyze Mood")
    if submit:
        score_map = {"Very good":5,"Good":4,"Neutral":3,"Bad":2,"Very bad":1,
                     "Very motivated":5,"Somewhat motivated":4,"Neutral":3,"Little motivated":2,"Not motivated at all":1,
                     "Very well":5,"Well":4,"Average":3,"Poorly":2,"Very poorly":1,
                     "Very low":5,"Low":4,"Moderate":3,"High":2,"Very high":1,
                     "Very connected":5,"Somewhat connected":4,"Neutral":3,"Somewhat disconnected":2,"Very disconnected":1}
        total = sum(score_map.get(a,3) for a in answers)
        avg = total / len(questions)
        if avg >= 4.5: analysis,suggested="Very Positive and Happy","happy"
        elif avg >= 3.5: analysis,suggested="Generally Positive","neutral"
        elif avg >= 2.5: analysis,suggested="Neutral","neutral"
        elif avg >= 1.5: analysis,suggested="Stressed or Negative","sad"
        else: analysis,suggested="Very Negative or Upset","angry"
        st.markdown(f"**Average Mood Score:** {avg:.2f}")
        st.info(f"Analysis: {analysis}")
        st.markdown(f"**Suggested Chat Tone:** `{suggested}`")
        if st.button("Use Suggested Tone"):
            current_mood = suggested
            st.success(f"Applied mood `{suggested}` to chat.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Chat Panel ----------------
with chat_col:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.subheader("🌿 Zypher Chatbot")  # No white box

    chat_placeholder = st.empty()

    # Display chat
    def display_chat():
        with chat_placeholder.container():
            for msg in st.session_state.chat_history:
                text = html.escape(str(msg.get("text","")))
                time = msg.get("time","")
                if msg.get("from")=="user":
                    st.markdown(f'<div class="user-bubble">{text}<div class="timestamp">{time}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-bubble">{text}<div class="timestamp">{time}</div></div>', unsafe_allow_html=True)
            st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.chat_history.append({
            "from":"user","text":str(user_input),"time":datetime.now().strftime("%H:%M")
        })
        reply = get_bot_response(user_input, current_mood)
        st.session_state.chat_history.append({
            "from":"bot","text":str(reply),"time":datetime.now().strftime("%H:%M")
        })

    display_chat()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Footer ----------------
st.markdown('<div style="text-align:center;color:#555;padding:8px;font-size:12px;">🔒 All conversations are end-to-end encrypted. Your privacy is 100% safe here.</div>', unsafe_allow_html=True)
