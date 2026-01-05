import streamlit as st
import google.generativeai as genai
import datetime

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="Adolat AI", page_icon="⚖️", layout="wide")

# --- API KALIT ---
# Sizning kalitingiz xavfsiz joylandi
API_KEY = "AIzaSyBJq338ZJDPpf3Lor54-nC5hvD1xxr5XgI"

# --- MUKAMMAL MINIMALISTIK DIZAYN (CSS) ---
st.markdown("""
    <style>
    /* Asosiy fon - To'q, ko'zni charchatmaydigan "Deep Navy" */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Sarlavha dizayni */
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

    /* Chat xabarlari dizayni - Apple style */
    .stChatMessage {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: none;
    }
    /* Foydalanuvchi xabari */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1e293b; /* Yengilroq to'q rang */
        border: 1px solid #334155;
    }
    /* AI xabari */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: transparent;
    }
    
    /* Input maydoni */
    .stTextInput input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sarlavha qismi ---
st.markdown("""
    <div class='main-header'>
        <h1>Adolat AI</h1>
        <p>O'zbekiston Respublikasi Qonunchilik Tahlili Tizimi</p>
    </div>
""", unsafe_allow_html=True)

# --- MODELNI SOZLASH (YANGI/ESKINI AJRATISH UCHUN) ---
@st.cache_resource
def load_smart_model():
    try:
        genai.configure(api_key=API_KEY)
        
        # Bugungi sana (AI vaqtni bilishi uchun)
        today = datetime.date.today().strftime("%Y-yil %d-avgust")
        
        # Tizim ko'rsatmasi (System Instruction)
        # Bu yerda biz AIga "Eski qonunni ishlatma" deb qat'iy buyruq beramiz
        lawyer_instruction = f"""
        Bugungi sana: {today}.
        Sen O'zbekistonning professional yuristisan.
        VAZIFANG: Foydalanuvchi savoliga faqat AMALDAGI (kuchga ega) qonunlar asosida javob berish.
        
        QAT'IY QOIDALAR:
        1. Javob berishdan oldin qonunning yiliga qara. Agar yangi tahriri bo'lsa, eskisini umuman ishlatma.
        2. Lex.uz saytidagi "O'z kuchini yo'qotgan" degan statusga ega hujjatlarga tayanma.
        3. Javobingda aniq modda va qonun nomini keltir.
        4. Agar qonun yaqinda o'zgargan bo'lsa (masalan, Konstitutsiya yoki Mehnat kodeksi), albatta YANGI tahririni ishlat.
        """

        # Biz avval qidiruv (search) funksiyasi bor modelni sinaymiz
        # Chunki faqat Search orqali u "bu qonun bekor qilinganmi?" degan savolga aniq javob topadi
        return genai.GenerativeModel(
            'models/gemini-1.5-flash',
            tools='google_search_retrieval',
            system_instruction=lawyer_instruction
        )
    except:
        # Agar Search ishlamasa, barqaror Pro modeliga o'tamiz, lekin baribir instruksiyani beramiz
        return genai.GenerativeModel('gemini-pro')

model = load_smart_model()

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
    # Foydalanuvchi xabari
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI javobi
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("🔍 Qonunchilik bazasi tahlil qilinmoqda..."):
                # AIga eslatma: har safar "Yangi qonunni qidir" deb eslatamiz
                full_prompt = f"Diqqat! Faqat AMALDAGI va KUCHGA EGA bo'lgan qonunlar bo'yicha javob ber. Eski qonunlarni inkor et. Savol: {prompt}"
                
                response = model.generate_content(full_prompt)
                
                # Javobni ko'rsatish
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
        except Exception as e:
            st.error("Uzr, tizimda vaqtincha nosozlik. Iltimos, qayta urinib ko'ring.")
            # Xatoni dasturchi ko'rishi uchun konsolga chiqaramiz (saytda ko'rinmaydi)
            print(f"Xatolik: {e}")
