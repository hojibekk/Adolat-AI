import streamlit as st
import google.generativeai as genai
import time

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="Adolat AI Portal", page_icon="⚖️", layout="wide")

# --- PROFESSIONAL CSS DIZAYN ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        color: white;
    }
    .main-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 30px;
    }
    .user-msg {
        background: #3b82f6;
        padding: 15px;
        border-radius: 15px 15px 0px 15px;
        margin: 10px 0;
    }
    .ai-msg {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px 15px 15px 0px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-header'><h1>🏛 Adolat AI: Milliy Huquqiy Portal</h1><p>O'zbekiston Respublikasi qonunchiligi bo'yicha aqlli yordamchi</p></div>", unsafe_allow_html=True)


# --- API KALIT ---
API_KEY = "AIzaSyBJq338ZJDPpf3Lor54-nC5hvD1xxr5XgI"

# --- MODELNI AVTOMATIK ANIQLASH (XATONI YO'QOTISH UCHUN) ---
@st.cache_resource
def load_working_model():
    try:
        genai.configure(api_key=API_KEY)
        # Ishlaydigan modellarni qidirish
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Ustuvorlik bo'yicha modellarni tanlash
        if 'models/gemini-1.5-pro' in available_models:
            return genai.GenerativeModel('models/gemini-1.5-pro')
        elif 'models/gemini-1.5-flash' in available_models:
            return genai.GenerativeModel('models/gemini-1.5-flash')
        elif 'models/gemini-pro' in available_models:
            return genai.GenerativeModel('models/gemini-pro')
        else:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        return f"Xatolik: {e}"

model = load_working_model()

# --- INTERFEYS ---
st.markdown("<h1 class='main-title'>ADOLAT AI</h1>", unsafe_allow_html=True)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Emblem_of_Uzbekistan.png", width=120)
st.sidebar.title("Navigatsiya")
st.sidebar.info("Tizim: O'zbekiston huquqiy bazasini tahlil qiluvchi neyrotarmoq.")

# Xabarlar tarixi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tarixni chiqarish
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Foydalanuvchi yozishi
if prompt := st.chat_input("Savolingizni yozing "):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if isinstance(model, str): # Agar load_working_model xato qaytargan bo'lsa
            st.error(f"API ulanishida muammo bor: {model}")
        else:
            try:
                with st.spinner(" Rasmiy manbalar tahlil qilinmoqda..."):
                    # Professional ko'rsatma
                    full_instruction = f"Sen O'zbekiston Respublikasining yuqori malakali yuristi va huquqshunosisan. Savolga O'zbekistonning eng yangi qonunlari asosida, moddalarni ko'rsatib javob ber: {prompt}"
                    
                    response = model.generate_content(full_instruction)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI javob berishda qiynaldi: {e}")
                st.warning("Ehtimol, API kalit limitiga yetgan yoki internetda muammo bor.")

st.sidebar.markdown("---")
st.sidebar.write("© 2026 Barcha huquqlar himoyalangan.")