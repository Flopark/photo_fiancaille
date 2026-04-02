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

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Nos Fiançailles", page_icon="💍", layout="centered")

# --- THÈME PASTEL (CSS Personnalisé) ---
st.markdown("""
<style>
    /* Couleur de fond pastel et typographie élégante */
    .stApp {
        background-color: #fdf6f5; /* Rose poudré très clair */
        color: #5d4037; /* Marron doux */
        font-family: 'Georgia', serif;
    }
    h1, h2, h3 {
        color: #d4a373; /* Or/Sable doux */
        text-align: center;
        font-family: 'Georgia', serif;
    }
    /* Stylisation des boutons */
    .stButton>button {
        background-color: #e2cec0;
        color: #5d4037;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #d4a373;
        color: white;
    }
    /* Contour de la zone de dépôt de fichier */
    .stFileUploader>div>div {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("💍 Bienvenue à nos Fiançailles !")
st.markdown("<p style='text-align: center;'>Partagez vos clichés et découvrez les plus beaux moments de cette journée</p>", unsafe_allow_html=True)

# --- CONNEXION GOOGLE DRIVE ---
@st.cache_resource
def get_drive_service():
    # Streamlit récupère les identifiants de manière sécurisée
    creds_dict = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

service = get_drive_service()
FOLDER_ID = st.secrets["drive"]["folder_id"]

# --- SECTION UPLOAD ---
st.markdown("---")
st.header("📸 Ajouter vos photos")
uploaded_files = st.file_uploader("Appuyez ici pour sélectionner vos photos", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

if uploaded_files and st.button("Envoyer les photos ✨"):
    with st.spinner("Envoi en cours vers notre album magique..."):
        for file in uploaded_files:
            file_metadata = {'name': file.name, 'parents': [FOLDER_ID]}
            media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype=file.type, resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        st.success("Merci ! Vos photos ont été ajoutées avec succès. 🎉")

# --- SECTION GALERIE ---
st.markdown("---")
st.header("🖼️ Galerie Souvenirs")
st.markdown("<p style='text-align: center; font-size: 0.9em;'>Appuyez sur le bouton ci-dessous pour voir les photos des autres invités</p>", unsafe_allow_html=True)

if st.button("Charger la galerie 🌸"):
    with st.spinner("Récupération des photos..."):
        # Cherche les 30 dernières photos dans le dossier
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and trashed=false",
            pageSize=30, fields="nextPageToken, files(id, name)",
            orderBy="createdTime desc"
        ).execute()
        items = results.get('files', [])

        if not items:
            st.info("La galerie est encore vide. Soyez le premier à ajouter une photo !")
        else:
            cols = st.columns(2) # Affiche les photos sur 2 colonnes (idéal sur téléphone)
            for i, item in enumerate(items):
                try:
                    request = service.files().get_media(fileId=item['id'])
                    downloaded = io.BytesIO(request.execute())
                    cols[i % 2].image(downloaded, use_container_width=True)
                except Exception as e:
                    pass # Ignore les fichiers qui ne seraient pas des images valides












import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

# ---------------------------------------------------------
# Configuration de la page pour une expérience immersive
# ---------------------------------------------------------
st.set_page_config(page_title="Nos Fiançailles", layout="wide", initial_sidebar_state="collapsed")

# Injection CSS pour cacher les éléments de navigation par défaut et forcer la police
hide_streamlit_style = """
<style>
    [data-testid="stHeader"] {visibility: hidden;}
    {display: none!important;}
    footer {display: none!important;}
  .block-container {padding-top: 2rem;}
    
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700&display=swap');
    
    h1, h2, h3, p, div {
        font-family: 'Playfair Display', serif!important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Titre et message d'accueil
st.title("💍 Galerie de nos Fiançailles")
st.write("Partagez vos plus beaux souvenirs avec nous et découvrez ceux des autres invités!")

# L'identifiant de votre dossier Drive (extrait de l'URL du dossier)
FOLDER_ID = st.secrets.get("FOLDER_ID", "1j0LKuITFba9ai9cFv2Iuiio9LOeC6OtE")

# ---------------------------------------------------------
# 1. Initialisation du client Google Drive (Mise en cache)
# ---------------------------------------------------------
@st.cache_resource
def init_drive_service():
    # Lecture des identifiants JSON sécurisés depuis la mémoire de Streamlit
    creds_info = st.secrets["connections"]["gcp"]
    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=creds)

drive_service = init_drive_service()

# ---------------------------------------------------------
# 2. Moteur de téléversement (Upload) des photos
# ---------------------------------------------------------
def upload_image(uploaded_file):
    # CORRECTION ICI : Ajout des crochets et de la variable FOLDER_ID
    file_metadata = {
        'name': uploaded_file.name,
        'parents': 
    }
    # Les fichiers ne sont jamais sauvegardés sur le disque du serveur, tout se passe en mémoire
    media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type, resumable=True)
    drive_service.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id'
    ).execute()

# Interface pour inviter à uploader des images
uploaded_files = st.file_uploader("Sélectionnez vos photos", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Transfert de vos souvenirs en cours..."):
        for file in uploaded_files:
            upload_image(file)
        st.success("Vos photos ont été ajoutées avec succès à la galerie!")

# ---------------------------------------------------------
# 3. Synchronisation et Récupération des images
# ---------------------------------------------------------
@st.cache_data(ttl=60) # Purge automatique du cache toutes les 60 secondes pour voir les nouveautés
def get_files_list():
    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        pageSize=100,
        fields="files(id, name, mimeType)",
        orderBy="createdTime desc" # Les plus récentes en premier
    ).execute()
    return results.get('files',)

# Téléchargement sécurisé des flux binaires des images
@st.cache_data(show_spinner=False)
def download_image(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read()

# ---------------------------------------------------------
# 4. Affichage de la Galerie en Grille Matricielle
# ---------------------------------------------------------
st.markdown("---")
st.header("📸 Souvenirs de la soirée")

files = get_files_list()

if not files:
    st.info("La galerie est encore vide. Soyez les premiers à déposer une photo!")
else:
    # Création d'une disposition esthétique sur 3 colonnes
    cols = st.columns(3)
    for index, file in enumerate(files):
        # Sécurité : traiter uniquement les fichiers de type image
        if file.get('mimeType', '').startswith('image/'):
            image_bytes = download_image(file['id'])
            
            # Distribution équitable dans les différentes colonnes
            col = cols[index % 3]
            # Affichage de l'image ajustée à la largeur de sa colonne
            col.image(image_bytes, use_column_width=True)


