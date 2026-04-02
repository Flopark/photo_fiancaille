# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 15:04:00 2026

@author: march
"""
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


