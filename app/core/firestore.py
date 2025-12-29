import os
import firebase_admin
from firebase_admin import credentials, firestore

db = None

def init_firestore():
    global db

    if firebase_admin._apps:
        db = firestore.client()
        return db

    project_id = os.getenv("FIREBASE_PROJECT_ID")
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY")

    # 🔴 Eğer Render'da Firebase env yoksa, servis çökmesin
    if not project_id or not client_email or not private_key:
        print("⚠️ Firebase env variables not set. Firestore disabled.")
        return None

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": project_id,
        "private_key": private_key.replace("\\n", "\n"),
        "client_email": client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    })

    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db


# 🔥 Uygulama başlarken çağır
db = init_firestore()
