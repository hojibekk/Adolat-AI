import streamlit as st
from google import genai
import datetime
import time

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="Adolat AI", page_icon="⚖️", layout="wide")

# --- API KALIT ---
API_KEY = "AIzaSyBJq338ZJDPpf3Lor54-nC5hvD1xxr5XgI"

# --- MINIMALISTIK VA TOZA DIZAYN (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 40px 0;
        border-bottom: 1px solid #1e293b;
    }
    .main-header h1 {
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -1px;
    }
    /* Chat xabarlari dizayni */
    .stChatMessage {
        background-color: #1e293b !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        margin-bottom: 15px !important;
    }
    /* Sidebar dizayni */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class='main-header'>
        <h1>Adolat AI</h1>
        <p>O'zbekiston Respublikasi Milliy Huquqiy Eksperti</p>
    </div>
""", unsafe_allow_html=True)

# --- YANGI GENAI CLIENT (2026 STANDARTI) ---
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
    st.markdown("### 🏛 Tizim Holati")
    st.success("Baza: Lex.uz (Amaldagi)")
    st.info("AI Model: Gemini 2.0")
    if st.button("🔄 Suhbatni yangilash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- CHAT TARIXI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ASOSIY MANTIQ VA YOZISH EFFEKTI ---
if prompt := st.chat_input("Savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if client:
            try:
                # Bugungi sana va qat'iy instruksiya
                today = datetime.date.today().strftime("%Y-yil %d-yanvar")
                system_instruction = (
                    f"Bugun {today}. Sen O'zbekistonning malakali huquqshunosisan. "
                    "SAVOLGA FAQAT AMALDAGI QONUNLAR ASOSIDA JAVOB BER. "
                    "Agar qonun eskirgan yoki o'z kuchini yo'qotgan bo'lsa (masalan, eski Konstitutsiya), uni umuman ishlatma. "
                    "Faqat yangi tahrirlarga tayan."
                )
                
                full_prompt = f"{system_instruction}\n\nFoydalanuvchi savoli: {prompt}"

                # YOZISH EFFEKTI UCHUN GENERATOR
                def get_streaming_response():
                    # Gemini 2.0 Flash orqali real vaqtda javob olish
                    response_stream = client.models.generate_content_stream(
                        model='gemini-2.0-flash',
                        contents=full_prompt,
                        config={'tools': [{'google_search': {}}]}
                    )
                    for chunk in response_stream:
                        yield chunk.text

                # "Yozish" effektini ko'rsatish
                full_response = st.write_stream(get_streaming_response())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Xatolik: Tizim hozirda javob bera olmaydi.")
        else:
            st.error("API ulanishida xatolik mavjud.")

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Adolat AI")
