import streamlit as st
from google import genai
import datetime

# --- SAHIFA ---
st.set_page_config(page_title="Adolat AI", page_icon="⚖️", layout="wide")

# --- API ---
API_KEY = "AIzaSyBJq338ZJDPpf3Lor54-nC5hvD1xxr5XgI"

# --- MUKAMMAL DIZAYN ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0f1e; color: #f1f5f9; }
    .stChatMessage { border-radius: 15px !important; border: 1px solid #1e293b !important; }
    .main-header { text-align: center; padding: 20px; border-bottom: 2px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-header'><h1>Adolat AI</h1><p>Faqat amaldagi qonunchilik tahlili</p></div>", unsafe_allow_html=True)

# --- MODELNI SOZLASH ---
@st.cache_resource
def load_client():
    try:
        return genai.Client(api_key=API_KEY)
    except:
        return None

client = load_client()

# --- ASOSIY MANTIQ (Yangi/Eski qonunlarni ajratish) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Huquqiy savolingizni yozing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if client:
            try:
                # BU YERDA AIga BUGUNGI SANANI VA QONUNLARNI SARALASH BUYRUG'INI BERAMIZ
                bugun = datetime.date.today().strftime("%Y-yil %d-%B")
                
                system_instruction = f"""
                Bugungi sana: {bugun}. Sen O'zbekiston Respublikasining bosh yuristisan.
                SENING ASOSIY QOIDANG:
                1. O'zbekistonning barcha qonun hujjatlarini faqat eng oxirgi (yangi) tahriri bilan tahlil qil.
                2. Agar qonunning eski (o'z kuchini yo'qotgan) varianti bo'lsa, uni mutlaqo inkor et.
                3. Masalan: 2023-yildagi yangi Konstitutsiya tahriri turganda, 1992-yilgisini ishlatma.
                4. Yangi Mehnat kodeksi (2022/2023) turganda, eskisiga tayanma.
                5. Javobingda qonun qabul qilingan sanani va moddasini aniq ko'rsat.
                6. Agar savolga oid qonun o'zgargan bo'lsa, foydalanuvchini bundan ogohlantir.
                """
                
                # YOZISH EFFEKTI (STREAM)
                def response_generator():
                    stream = client.models.generate_content_stream(
                        model='gemini-2.0-flash',
                        contents=f"{system_instruction}\n\nSavol: {prompt}"
                    )
                    for chunk in stream:
                        yield chunk.text

                # Natijani yozish effekti bilan chiqarish
                full_text = st.write_stream(response_generator())
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
            except Exception as e:
                st.error("Tizim javob bera olmadi. API limitini yoki ulanishni tekshiring.")
