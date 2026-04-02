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

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Emma & Lucas 💍",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Nunito:wght@300;400;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #fdf6f0 !important;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #fdf6f0 0%, #fce8e8 40%, #f5e6f0 100%) !important;
    min-height: 100vh;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ── Hero Section ── */
.hero {
    text-align: center;
    padding: 60px 20px 40px;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: -80px; left: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,182,193,0.35) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 8s ease-in-out infinite;
}

.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; right: -60px;
    width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(216,191,216,0.3) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 10s ease-in-out infinite reverse;
}

@keyframes float {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-20px) scale(1.05); }
}

.crown-deco {
    font-size: 2rem;
    letter-spacing: 8px;
    margin-bottom: 16px;
    opacity: 0.6;
    animation: fadeIn 1.2s ease;
}

.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(3rem, 8vw, 6rem);
    font-weight: 300;
    color: #7a4f6d;
    line-height: 1.1;
    margin: 0;
    animation: slideUp 1s ease;
    letter-spacing: 2px;
}

.hero-title span {
    font-style: italic;
    color: #c47a9e;
}

.hero-subtitle {
    font-family: 'Nunito', sans-serif;
    font-size: clamp(0.95rem, 2.5vw, 1.15rem);
    font-weight: 300;
    color: #a07090;
    margin: 16px 0 8px;
    letter-spacing: 4px;
    text-transform: uppercase;
    animation: slideUp 1.3s ease;
}

.hero-date {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.4rem;
    font-style: italic;
    color: #c47a9e;
    opacity: 0.85;
    animation: slideUp 1.5s ease;
}

.divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 28px auto;
    max-width: 400px;
}

.divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, transparent, #e8b4c8, transparent);
}

.divider-icon { font-size: 1.2rem; color: #e8b4c8; }

/* ── Upload Section ── */
.section-card {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,182,193,0.3);
    border-radius: 24px;
    padding: 40px;
    margin: 0 auto 40px;
    max-width: 700px;
    box-shadow: 0 8px 40px rgba(196,122,158,0.1);
    animation: fadeIn 1.5s ease;
}

.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 400;
    color: #7a4f6d;
    text-align: center;
    margin-bottom: 8px;
}

.section-desc {
    font-family: 'Nunito', sans-serif;
    font-size: 0.95rem;
    color: #a07090;
    text-align: center;
    margin-bottom: 24px;
    font-weight: 300;
}

/* ── Streamlit Uploader Override ── */
[data-testid="stFileUploader"] {
    background: rgba(252,232,232,0.4);
    border: 2px dashed rgba(228,154,180,0.5);
    border-radius: 16px;
    padding: 20px;
}

[data-testid="stFileUploader"] label {
    font-family: 'Nunito', sans-serif !important;
    color: #a07090 !important;
}

/* ── Button Overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #e8a4c0 0%, #c47a9e 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 40px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(196,122,158,0.35) !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(196,122,158,0.5) !important;
}

/* ── Text Input ── */
.stTextInput > div > div > input {
    border: 1px solid rgba(228,154,180,0.4) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.8) !important;
    font-family: 'Nunito', sans-serif !important;
    color: #7a4f6d !important;
    padding: 12px 16px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #c47a9e !important;
    box-shadow: 0 0 0 2px rgba(196,122,158,0.2) !important;
}

/* ── Success / Error Messages ── */
.success-msg {
    background: rgba(200,230,201,0.5);
    border: 1px solid rgba(130,190,130,0.4);
    border-radius: 12px;
    padding: 14px 20px;
    font-family: 'Nunito', sans-serif;
    color: #4a7c4a;
    text-align: center;
    font-size: 0.95rem;
    margin-top: 12px;
}

.error-msg {
    background: rgba(255,205,210,0.5);
    border: 1px solid rgba(230,130,130,0.4);
    border-radius: 12px;
    padding: 14px 20px;
    font-family: 'Nunito', sans-serif;
    color: #9a3a3a;
    text-align: center;
    font-size: 0.95rem;
    margin-top: 12px;
}

/* ── Gallery ── */
.gallery-section {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px 60px;
    animation: fadeIn 2s ease;
}

.gallery-header {
    text-align: center;
    margin-bottom: 32px;
}

.photo-count {
    display: inline-block;
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(228,154,180,0.3);
    border-radius: 50px;
    padding: 6px 20px;
    font-family: 'Nunito', sans-serif;
    font-size: 0.85rem;
    color: #a07090;
    margin-top: 8px;
}

.photo-card {
    background: rgba(255,255,255,0.7);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(196,122,158,0.12);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid rgba(255,182,193,0.2);
    margin-bottom: 16px;
}

.photo-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 35px rgba(196,122,158,0.22);
}

.photo-meta {
    padding: 12px 16px;
    font-family: 'Nunito', sans-serif;
    font-size: 0.82rem;
    color: #b090a0;
    text-align: center;
    border-top: 1px solid rgba(228,154,180,0.15);
}

.photo-meta strong {
    color: #8a5f7a;
    display: block;
    font-size: 0.9rem;
}

/* ── Footer ── */
.custom-footer {
    text-align: center;
    padding: 30px 20px;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    font-style: italic;
    color: #c47a9e;
    opacity: 0.7;
}

/* ── Animations ── */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .section-card { margin: 0 16px 32px; padding: 28px 20px; }
    .gallery-section { padding: 0 12px 40px; }
}
</style>
""", unsafe_allow_html=True)


# ─── GOOGLE DRIVE HELPERS ───────────────────────────────────────────────────────

@st.cache_resource
def get_drive_service():
    """Initialise le service Google Drive depuis les secrets Streamlit."""
    try:
        # Note : On s'assure d'utiliser la structure de secrets TOML classique
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error(f"Erreur d'authentification : {e}")
        return None

def upload_to_drive(service, file_bytes: bytes, filename: str, author: str, folder_id: str):
    """Upload une image sur Google Drive avec métadonnées."""
    metadata = {
        "name": f"{author}_{filename}",
        "parents": [folder_id],
        "description": f"Partagé par {author} — {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    }
    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype="image/jpeg",
        resumable=False
    )
    file = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,createdTime"
    ).execute()

    # Rendre le fichier public en lecture (Indispensable pour voir les miniatures)
    service.permissions().create(
        fileId=file["id"],
        body={"type": "anyone", "role": "reader"}
    ).execute()
    return file

@st.cache_data(ttl=30) # Met en cache pendant 30 secondes pour éviter de surcharger l'API
def list_photos(_service, folder_id: str):
    """Liste toutes les photos du dossier Drive."""
    results = _service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false",
        fields="files(id,name,createdTime,description,thumbnailLink)",
        orderBy="createdTime desc",
        pageSize=100
    ).execute()
    return results.get("files", [])

def parse_author(filename: str) -> str:
    """Extrait le prénom de l'auteur depuis le nom de fichier."""
    parts = filename.split("_", 1)
    return parts[0] if len(parts) > 1 else "Invité·e"


# ─── HERO ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="crown-deco">✦ ✦ ✦</div>
    <h1 class="hero-title">Emma <span>&</span> Lucas</h1>
    <p class="hero-subtitle">Nos fiançailles</p>
    <p class="hero-date">Le 14 juin 2025 · Paris</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="divider">
    <div class="divider-line"></div>
    <span class="divider-icon">💍</span>
    <div class="divider-line"></div>
</div>
""", unsafe_allow_html=True)


# ─── DRIVE CONNECTION ────────────────────────────────────────────────────────────

service = get_drive_service()
# On récupère l'ID du dossier via la clé "drive" comme défini dans ton TOML précédent
FOLDER_ID = st.secrets["drive"]["folder_id"] if "drive" in st.secrets else ""

if not service or not FOLDER_ID:
    st.markdown("""
    <div class="section-card" style="text-align:center;">
        <p style="font-family:'Nunito',sans-serif; color:#9a3a3a; font-size:1rem;">
            ⚙️ <strong>Configuration requise</strong><br><br>
            Le service Google Drive ou l'ID du dossier n'est pas configuré.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─── UPLOAD SECTION ──────────────────────────────────────────────────────────────

st.markdown("""
<div style="max-width:700px; margin:0 auto; padding:0 20px;">
<div class="section-card">
    <h2 class="section-title">📸 Partage tes photos</h2>
    <p class="section-desc">Immortalise ce moment magique en partageant tes plus belles photos avec nous ✨</p>
</div>
</div>
""", unsafe_allow_html=True)

with st.container():
    col_left, col_center, col_right = st.columns([1, 6, 1])
    with col_center:
        author_name = st.text_input(
            "Ton prénom 💌",
            placeholder="Ex : Sophie, Marc, Tantine Denise…",
            key="author"
        )
        uploaded_files = st.file_uploader(
            "Sélectionne tes photos 🌸",
            type=["jpg", "jpeg", "png", "webp", "heic"],
            accept_multiple_files=True,
            key="uploader"
        )

        if st.button("✨ Envoyer mes photos"):
            if not author_name.strip():
                st.markdown('<div class="error-msg">Oops ! Indique ton prénom pour signer tes photos 💕</div>', unsafe_allow_html=True)
            elif not uploaded_files:
                st.markdown('<div class="error-msg">Sélectionne au moins une photo à partager 🌸</div>', unsafe_allow_html=True)
            elif not service:
                st.markdown('<div class="error-msg">Le service Drive n\'est pas configuré. 🙏</div>', unsafe_allow_html=True)
            else:
                progress = st.progress(0)
                count_ok = 0
                for i, f in enumerate(uploaded_files):
                    try:
                        img = Image.open(f)
                        # Resize si trop grand pour alléger
                        max_size = 1800
                        if max(img.size) > max_size:
                            img.thumbnail((max_size, max_size), Image.LANCZOS)
                        buf = io.BytesIO()
                        img.convert("RGB").save(buf, format="JPEG", quality=88)
                        upload_to_drive(
                            service,
                            buf.getvalue(),
                            f.name,
                            author_name.strip(),
                            FOLDER_ID
                        )
                        count_ok += 1
                    except Exception as e:
                        st.error(f"Erreur sur {f.name} : {e}")
                    progress.progress((i + 1) / len(uploaded_files))

                progress.empty()
                if count_ok:
                    st.markdown(f'<div class="success-msg">🎉 {count_ok} photo{"s" if count_ok > 1 else ""} partagée{"s" if count_ok > 1 else ""} avec succès, merci {author_name.strip()} ! 💖</div>', unsafe_allow_html=True)
                    list_photos.clear() # Force le rafraichissement de la galerie
                    time.sleep(1.5)
                    st.rerun()


# ─── GALLERY ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="divider" style="max-width:400px; margin:20px auto 32px;">
    <div class="divider-line"></div>
    <span class="divider-icon">🌸</span>
    <div class="divider-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="gallery-section">
    <div class="gallery-header">
        <h2 class="section-title" style="margin:0;">Notre album partagé</h2>
        <p class="section-desc" style="margin:8px 0 0;">Tous vos souvenirs rassemblés en un seul endroit 💫</p>
    </div>
""", unsafe_allow_html=True)

if service and FOLDER_ID:
    with st.spinner("Chargement des photos… 🌸"):
        try:
            photos = list_photos(service, FOLDER_ID)
        except Exception as e:
            photos = []
            st.error(f"Impossible de charger les photos : {e}")

    if not photos:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px;">
            <div style="font-size:3rem; margin-bottom:16px;">📷</div>
            <p style="font-family:'Nunito',sans-serif; color:#a07090; font-size:1rem;">
                Aucune photo pour l'instant… Sois le premier à partager un souvenir ! 💕
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center;"><span class="photo-count">📸 {len(photos)} souvenir{"s" if len(photos) > 1 else ""} partagé{"s" if len(photos) > 1 else ""}</span></div><br>', unsafe_allow_html=True)

        cols_per_row = 3
        for row_start in range(0, len(photos), cols_per_row):
            row_photos = photos[row_start:row_start + cols_per_row]
            cols = st.columns(cols_per_row)
            for col, photo in zip(cols, row_photos):
                with col:
                    # Utilisation directe du lien miniature de Google Drive (10x plus rapide !)
                    # On remplace =s220 (taille par défaut) par =s600 pour une belle qualité
                    thumb_url = photo.get("thumbnailLink", "").replace("=s220", "=s600")
                    
                    author = parse_author(photo["name"])
                    date_str = ""
                    if "createdTime" in photo:
                        dt = datetime.fromisoformat(photo["createdTime"].replace("Z", "+00:00"))
                        date_str = dt.strftime("%d/%m/%Y · %H:%M")

                    if thumb_url:
                        st.markdown(f'<div class="photo-card">', unsafe_allow_html=True)
                        st.image(thumb_url, use_container_width=True)
                        st.markdown(f"""
                        <div class="photo-meta">
                            <strong>✨ {author}</strong>
                            {date_str}
                        </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("*Photo en cours de traitement par Google...*")
else:
    st.markdown("""
    <div style="text-align:center; padding:40px;">
        <p style="font-family:'Nunito',sans-serif; color:#a07090; font-size:0.9rem;">
            La galerie sera disponible une fois le service configuré 🌸
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True) # Fermeture de gallery-section

# ─── FOOTER ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="divider" style="max-width:300px; margin:20px auto;">
    <div class="divider-line"></div>
    <span class="divider-icon">✦</span>
    <div class="divider-line"></div>
</div>
<div class="custom-footer">
    Avec tout notre amour — Emma & Lucas 💍
</div>
""", unsafe_allow_html=True)
