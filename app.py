import streamlit as st
import google.generativeai as genai
import re  # Library untuk manipulasi teks
import os # Tambahkan library os

# --- 1. KONFIGURASI API KEY ---
API_KEY = os.environ.get("GEMINI_API_KEY") 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. MENGATUR PERSONA AI (System Prompt) ---
instruksi_sistem = """
Kamu adalah Asisten AI Customer Service yang ramah, profesional, dan gaul untuk tempat Servis Laptop milik "Jejak Tekno".
Aturanmu:
1. Selalu gunakan bahasa Indonesia yang luwes, sopan, tapi tidak kaku (boleh pakai emoji).
2. Jika pengguna menyebutkan masalah laptop, berikan sedikit empati atau analisis singkat tentang kemungkinan penyebabnya sebelum menyuruh mereka datang.
3. Jangan pernah memberikan harga pasti, selalu berikan kisaran atau bilang "perlu dicek langsung oleh teknisi Jejak Tekno".
4. Jika mereka ingin booking, konfirmasi merk laptop dan keluhannya, lalu suruh bawa ke toko.
"""

# --- 3. UI & CSS (TAMPILAN DM INSTAGRAM) ---
st.set_page_config(page_title="Jejak Tekno Care", layout="wide")

# Menanamkan CSS Kustom ke dalam Streamlit
st.markdown("""
<style>
/* Menghilangkan margin atas agar lebih rapi */
.block-container {
    padding-top: 2rem;
}

/* Layout Kontainer Baris Chat */
.chat-row {
    display: flex;
    margin-bottom: 15px;
    width: 100%;
}
.row-user {
    justify-content: flex-end; /* Dorong ke Kanan */
}
.row-bot {
    justify-content: flex-start; /* Dorong ke Kiri */
}

/* Desain Gelembung Chat (Bubble) */
.chat-bubble {
    padding: 12px 16px;
    border-radius: 22px;
    max-width: 70%;
    font-size: 15px;
    line-height: 1.5;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.bubble-user {
    background-color: #0084ff; /* Biru khas Messenger/IG */
    color: white;
    border-bottom-right-radius: 4px; /* Sudut lancip di kanan bawah */
}
.bubble-bot {
    background-color: #efefef; /* Abu-abu terang */
    color: black;
    border-bottom-left-radius: 4px; /* Sudut lancip di kiri bawah */
}
</style>
""", unsafe_allow_html=True)

# Fungsi khusus untuk merender HTML chat
def render_chat_ig(role, text):
    # 1. Hapus tag [Info Sistem...] agar tidak bocor ke UI User
    text_bersih = re.sub(r'\[Info Sistem:.*?\]\.\n\n', '', text)
    
    # 2. Konversi format tebal (bold) dari AI agar terbaca di HTML
    text_bersih = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text_bersih)
    
    # 3. Ubah enter/baris baru menjadi tag <br> HTML
    text_bersih = text_bersih.replace('\n', '<br>')
    
    # 4. Tampilkan ke layar berdasarkan siapa yang bicara
    if role == "user":
        st.markdown(f'<div class="chat-row row-user"><div class="chat-bubble bubble-user">{text_bersih}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-row row-bot"><div class="chat-bubble bubble-bot">{text_bersih}</div></div>', unsafe_allow_html=True)

# --- 4. SIDEBAR & HEADER ---
with st.sidebar:
    st.header("📋 Form Diagnosa Awal")
    st.write("Bantu kami mengenali laptopmu:")
    pilihan_laptop = st.selectbox("Jenis/Merk Laptop:", ["Belum Pasti", "Asus", "Lenovo", "Acer", "HP", "Macbook", "Dell", "Lainnya"])
    pilihan_keluhan = st.selectbox("Kategori Keluhan:", ["Belum Pasti", "Layar/LCD", "Mati Total", "Keyboard", "Software/OS", "Lemot", "Baterai"])

st.title("💬 Live Chat - Jejak Tekno")
st.caption("Admin AI kami sedang online dan siap membantu perbaikan laptopmu.")
st.markdown("---")

# --- 5. LOGIKA MEMORI & TAMPILAN CHAT ---
# Menyimpan riwayat chat (Memory AI)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[
        {"role": "user", "parts": [instruksi_sistem]},
        {"role": "model", "parts": ["Baik, saya mengerti. Saya adalah asisten CS Jejak Tekno. Saya siap membantu pelanggan."]}
    ])

# Render riwayat chat yang sudah ada dengan gaya IG
for message in st.session_state.chat_session.history[2:]:
    role = "assistant" if message.role == "model" else "user"
    render_chat_ig(role, message.parts[0].text)

# Input Chat Baru
if prompt := st.chat_input("Ketik pesanmu di sini..."):
    
    # Tampilkan bubble chat biru milik user secara instan
    render_chat_ig("user", prompt)
    
    # Merakit konteks tersembunyi
    konteks_tambahan = ""
    if pilihan_laptop != "Belum Pasti" or pilihan_keluhan != "Belum Pasti":
        konteks_tambahan = f"[Info Sistem: Pengguna menggunakan laptop {pilihan_laptop} dengan indikasi masalah {pilihan_keluhan}].\n\n"
    
    pesan_final_ke_ai = konteks_tambahan + prompt

    # Mengirim ke AI dengan animasi loading
    with st.spinner("AI sedang mengetik balasan..."):
        response = st.session_state.chat_session.send_message(pesan_final_ke_ai)
    
    # Tampilkan bubble chat abu-abu milik AI
    render_chat_ig("assistant", response.text)