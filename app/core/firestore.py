import os
import firebase_admin
from firebase_admin import credentials, firestore

# Service account JSON dosyasının yolu
SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_KEY_PATH",
    "serviceAccountKey.json"  # proje kökünde
)

# Firebase app sadece 1 kere initialize edilir
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
