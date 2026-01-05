import streamlit as st
from google import genai
import datetime
import time

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="Adolat AI", page_icon="⚖️", layout="wide")

# --- API KALIT ---
API_KEY = "AIzaSyBJq338ZJDPpf3Lor54-nC5hvD1xxr5XgI"

# --- DIZAYN (Minimalistik) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    .main-header { text-align: center; padding: 30px 0; border-bottom: 1px solid #1e293b; margin-bottom: 20px; }
    .stChatMessage { background-color: #1e293b !important; border-radius: 12px !important; border: 1px solid #334155 !important; }
    section[data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-header'><h1>Adolat AI</h1><p>O'zbekiston Milliy Huquqiy Eksperti</p></div>", unsafe_allow_html=True)

# --- CLIENTNI YOQISH ---
@st.cache_resource
def get_client():
    try:
        return genai.Client(api_key=API_KEY)
    except Exception:
        return None

client = get_client()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Emblem_of_Uzbekistan.png", width=100)
    st.markdown("### 🏛 Tizim")
    st.success("Baza: Lex.uz (Amaldagi)")
    if st.button("🔄 Suhbatni yangilash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if client:
            try:
                # Bugungi sana va instruksiya
                today = datetime.date.today().strftime("%Y-yil %d-yanvar")
                system_instruction = (
                    f"Bugun {today}. Sen O'zbekistonning professional huquqshunosisan. "
                    "Faqat AMALDAGI qonunlar asosida javob ber. Eski tahrirlarni ishlatma."
                )
                
                # YOZISH EFFEKTI (STREAMING) MANTIQI
                def generate_response_stream():
                    # generate_content_stream usulini eng xavfsiz formatda chaqiramiz
                    response = client.models.generate_content_stream(
                        model='gemini-2.0-flash',
                        contents=f"{system_instruction}\n\nSavol: {prompt}"
                    )
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                # Streamlit orqali yozishni ko'rsatish
                full_response = st.write_stream(generate_response_stream())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                # Agar streamingda xato bo'lsa, oddiy usulda sinab ko'ramiz
                try:
                    res = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt
                    )
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                except:
                    st.error("AI javob berishda xatolikka yo'liqdi. Iltimos, birozdan so'ng qayta urinib ko'ring.")
        else:
            st.error("Tizim ulanishida xatolik.")
