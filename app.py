# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 15:04:00 2026

@author: march
"""
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from PIL import Image
import time
from datetime import datetime

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Camille & Florian 💍", page_icon="💍", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PASTEL ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Nunito:wght@300;400;600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #fdf6f0 0%, #fce8e8 40%, #f5e6f0 100%) !important;
    min-height: 100vh;
}
[data-testid="stHeader"], footer, #MainMenu, [data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.hero { text-align: center; padding: 60px 20px 40px; }
.crown-deco { font-size: 2rem; letter-spacing: 8px; margin-bottom: 16px; opacity: 0.6; }
.hero-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(3rem, 8vw, 6rem); color: #7a4f6d; margin: 0; }
.hero-title span { font-style: italic; color: #c47a9e; }
.hero-subtitle { font-family: 'Nunito', sans-serif; font-size: clamp(0.95rem, 2.5vw, 1.15rem); color: #a07090; margin: 16px 0 8px; letter-spacing: 4px; text-transform: uppercase; }
.hero-date { font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; font-style: italic; color: #c47a9e; opacity: 0.85; }
.divider { display: flex; align-items: center; justify-content: center; gap: 12px; margin: 28px auto; max-width: 400px; }
.divider-line { flex: 1; height: 1px; background: linear-gradient(to right, transparent, #e8b4c8, transparent); }
.divider-icon { font-size: 1.2rem; color: #e8b4c8; }
.section-card { background: rgba(255,255,255,0.65); border: 1px solid rgba(255,182,193,0.3); border-radius: 24px; padding: 40px; margin: 0 auto 40px; max-width: 700px; box-shadow: 0 8px 40px rgba(196,122,158,0.1); }
.section-title { font-family: 'Cormorant Garamond', serif; font-size: 2rem; color: #7a4f6d; text-align: center; margin-bottom: 8px; }
.section-desc { font-family: 'Nunito', sans-serif; font-size: 0.95rem; color: #a07090; text-align: center; margin-bottom: 24px; }
.stButton > button { background: linear-gradient(135deg, #e8a4c0 0%, #c47a9e 100%) !important; color: white !important; border: none !important; border-radius: 50px !important; padding: 12px 40px !important; font-family: 'Nunito', sans-serif !important; width: 100% !important; }
.gallery-section { max-width: 1200px; margin: 0 auto; padding: 0 20px 60px; }
.photo-card { background: rgba(255,255,255,0.7); border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,182,193,0.2); margin-bottom: 16px; }
.photo-meta { padding: 12px 16px; font-family: 'Nunito', sans-serif; font-size: 0.82rem; color: #b090a0; text-align: center; border-top: 1px solid rgba(228,154,180,0.15); }
.custom-footer { text-align: center; padding: 30px 20px; font-family: 'Cormorant Garamond', serif; font-style: italic; color: #c47a9e; }
.success-msg { background: rgba(200,230,201,0.5); padding: 14px 20px; color: #4a7c4a; text-align: center; border-radius: 12px; margin-top: 12px;}
.error-msg { background: rgba(255,205,210,0.5); padding: 14px 20px; color: #9a3a3a; text-align: center; border-radius: 12px; margin-top: 12px;}
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS GOOGLE DRIVE ---
@st.cache_resource
def get_drive_service():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive"])
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        return None

def upload_to_drive(service, file_bytes, filename, author, folder_id):
    metadata = {"name": f"{author}_{filename}", "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype="image/jpeg", resumable=False)
    file = service.files().create(body=metadata, media_body=media, fields="id").execute()
    service.permissions().create(fileId=file["id"], body={"type": "anyone", "role": "reader"}).execute()
    return file

@st.cache_data(ttl=30)
def list_photos(_service, folder_id):
    results = _service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false",
        fields="files(id,name,createdTime,thumbnailLink)", orderBy="createdTime desc", pageSize=100
    ).execute()
    return results.get("files", [])

# --- INTERFACE ---
st.markdown("""<div class="hero"><div class="crown-deco">✦ ✦ ✦</div><h1 class="hero-title">Camille <span>&</span> Florian </h1><p class="hero-subtitle">Nos fiançailles</p><p class="hero-date">Le 9 mai 2026 · Calais </p></div>""", unsafe_allow_html=True)
st.markdown("""<div class="divider"><div class="divider-line"></div><span class="divider-icon">💍</span><div class="divider-line"></div></div>""", unsafe_allow_html=True)

service = get_drive_service()
FOLDER_ID = st.secrets["drive"]["folder_id"] if "drive" in st.secrets else ""

# --- SECTION UPLOAD ---
st.markdown("""<div style="max-width:700px; margin:0 auto; padding:0 20px;"><div class="section-card"><h2 class="section-title">📸 Partage tes photos</h2><p class="section-desc">Immortalise ce moment magique en partageant tes plus belles photos avec nous ✨</p></div></div>""", unsafe_allow_html=True)

with st.container():
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        author_name = st.text_input("Ton prénom 💌", placeholder="Ex : Sophie, Marc...")
        uploaded_files = st.file_uploader("Sélectionne tes photos 🌸", type=["jpg", "jpeg", "png", "webp", "heic"], accept_multiple_files=True)

        if st.button("✨ Envoyer mes photos"):
            if not author_name.strip():
                st.markdown('<div class="error-msg">Oops ! Indique ton prénom pour signer tes photos 💕</div>', unsafe_allow_html=True)
            elif not uploaded_files:
                st.markdown('<div class="error-msg">Sélectionne au moins une photo à partager 🌸</div>', unsafe_allow_html=True)
            elif not service:
                st.markdown('<div class="error-msg">Erreur de connexion à Google Drive 🙏</div>', unsafe_allow_html=True)
            else:
                progress = st.progress(0)
                count_ok = 0
                for i, f in enumerate(uploaded_files):
                    img = Image.open(f)
                    if max(img.size) > 1800: img.thumbnail((1800, 1800), Image.LANCZOS)
                    buf = io.BytesIO()
                    img.convert("RGB").save(buf, format="JPEG", quality=85)
                    upload_to_drive(service, buf.getvalue(), f.name, author_name.strip(), FOLDER_ID)
                    count_ok += 1
                    progress.progress((i + 1) / len(uploaded_files))
                progress.empty()
                if count_ok:
                    st.markdown(f'<div class="success-msg">🎉 {count_ok} photo(s) partagée(s), merci {author_name.strip()} ! 💖</div>', unsafe_allow_html=True)
                    list_photos.clear()
                    time.sleep(2)
                    st.rerun()

# --- SECTION GALERIE ---
st.markdown("""<div class="divider" style="max-width:400px; margin:20px auto 32px;"><div class="divider-line"></div><span class="divider-icon">🌸</span><div class="divider-line"></div></div>""", unsafe_allow_html=True)
st.markdown("""<div class="gallery-section"><h2 class="section-title">Notre album partagé</h2>""", unsafe_allow_html=True)

if service and FOLDER_ID:
    photos = list_photos(service, FOLDER_ID)
    if not photos:
        st.markdown("<p style='text-align:center;'>Aucune photo pour l'instant... 💕</p>", unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for i, photo in enumerate(photos):
            with cols[i % 3]:
                thumb = photo.get("thumbnailLink", "").replace("=s220", "=s600")
                author = photo["name"].split("_", 1)[0] if "_" in photo["name"] else "Invité"
                if thumb:
                    st.markdown('<div class="photo-card">', unsafe_allow_html=True)
                    st.image(thumb, use_container_width=True)
                    st.markdown(f'<div class="photo-meta"><strong>✨ {author}</strong></div></div>', unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align:center;'>Galerie indisponible (Drive non configuré)</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("""<div class="custom-footer">Avec tout notre amour — Camille & Florian 💍</div>""", unsafe_allow_html=True)

