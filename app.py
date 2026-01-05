import streamlit as st
from google import genai
import datetime
import time

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="Adolat AI", page_icon="⚖️", layout="wide")

# --- API KALIT ---
API_KEY = "AIzaSyBJq338ZJDPpf3Lor54-nC5hvD1xxr5XgI"

# --- MUKAMMAL MINIMALISTIK DIZAYN (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    .main-header {
        text-align: center;
        padding: 40px 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 30px;
    }
    .main-header h1 {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
        color: #f8fafc;
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1.1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: none;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1e293b;
        border: 1px solid #334155;
    }
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: transparent;
    }
    .stTextInput input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class='main-header'>
        <h1>Adolat AI</h1>
        <p>O'zbekiston Respublikasi Qonunchilik Tahlili Tizimi</p>
    </div>
""", unsafe_allow_html=True)

# --- YANGI MODEL SOZLAMALARI (XATO TUZATILDI) ---
@st.cache_resource
def get_ai_client():
    try:
        # 2026-yil standarti: Yangi genai Client
        return genai.Client(api_key=API_KEY)
    except Exception as e:
        st.error(f"Ulanishda xato: {e}")
        return None

client = get_ai_client()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Emblem_of_Uzbekistan.png", width=100)
    st.markdown("### 🏛 Huquqiy Baza")
    st.info("Ushbu tizim Lex.uz va milliy qonunchilik bazasi asosida ishlaydi.")
    st.markdown("---")
    if st.button("🔄 Suhbatni yangilash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIKASI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Huquqiy savolingizni kiriting..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Bugungi sana va instruksiya
            today = datetime.date.today().strftime("%Y-yil %d-avgust")
            system_instruction = f"""
            Bugungi sana: {today}. Sen O'zbekistonning professional yuristisan.
            VAZIFANG: Foydalanuvchi savoliga faqat AMALDAGI (kuchga ega) qonunlar asosida javob berish.
            1. Javob berishdan oldin qonunning yiliga qara. Agar yangi tahriri bo'lsa, eskisini umuman ishlatma.
            2. Lex.uz dagi amaldagi statusga tayan.
            3. Javobingda aniq moddalarni keltir.
            """
            
            full_prompt = f"{system_instruction}\n\nSavol: {prompt}"

            # --- YOZISH EFFEKTI (STREAMING) ---
            def stream_response():
                # Gemini 2.0 orqali stream olish
                response_stream = client.models.generate_content_stream(
                    model='gemini-2.0-flash',
                    contents=full_prompt,
                    config={'tools': [{'google_search': {}}]} # Qidiruv funksiyasi qo'shildi
                )
                for chunk in response_stream:
                    yield chunk.text

            # Streamlit'ning write_stream funksiyasi orqali yozish ko'rsatiladi
            full_response = st.write_stream(stream_response())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            st.error("Tizimda vaqtincha nosozlik. Iltimos, qayta urinib ko'ring.")
            print(f"Xatolik: {e}")

