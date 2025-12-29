from datetime import datetime, timedelta, timezone
from app.core.firestore import db

COLLECTION = "github_analysis_cache"
CACHE_HOURS = 24


def _to_utc_aware(dt):
    """
    Firestore'dan gelen datetime:
    - naive olabilir
    - aware olabilir
    Bu fonksiyon her durumda UTC-aware datetime döndürür
    """
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def get_cached_analysis(username: str):
    """
    - Cache var mı kontrol eder
    - Süresi dolmuş mu bakar
    - Eski formatları otomatik temizler
    """

    doc_ref = db.collection(COLLECTION).document(username)
    doc = doc_ref.get()

    if not doc.exists:
        return None

    data = doc.to_dict() or {}

    last_updated = data.get("updated_at")
    if not last_updated:
        return None

    # 🔒 TZ-AWARE GÜVENLİ DÖNÜŞÜM
    try:
        last_updated = _to_utc_aware(last_updated)
    except Exception as e:
        print("❌ Cache datetime parse hatası:", e)
        return None

    now = datetime.now(timezone.utc)

    # ⏱ Cache süresi dolmuş mu?
    if now - last_updated > timedelta(hours=CACHE_HOURS):
        return None

    # 🔥 ESKİ FORMAT TEMİZLEME
    # top_languages = [ ["Python", 8], ["Dart", 5] ]
    if "top_languages" in data:
        data["languages"] = [
            lang[0] if isinstance(lang, (list, tuple)) else lang
            for lang in data["top_languages"]
        ]
        del data["top_languages"]

    # 🔒 Güvenlik: languages her zaman liste
    if "languages" not in data or not isinstance(data["languages"], list):
        data["languages"] = []

    data["cached"] = True
    data["ok"] = True

    return data


def save_analysis(username: str, analysis: dict):
    """
    GitHub analiz sonucunu Firestore cache'e güvenli şekilde yazar
    """

    print("🔥 FIRESTORE'A YAZILAN ANALYSIS:", analysis)

    # 🔒 Language güvenliği
    languages = analysis.get("languages", [])
    if any(isinstance(l, (list, tuple)) for l in languages):
        languages = [l[0] for l in languages]

    now = datetime.now(timezone.utc)

    safe_data = {
        "username": analysis.get("username"),
        "score": analysis.get("score"),
        "repo_count": analysis.get("repo_count"),
        "followers": analysis.get("followers"),
        "stars": analysis.get("stars"),
        "active_repos": analysis.get("active_repos"),
        "languages": languages,
        # analyzed_at her zaman UTC-aware
        "analyzed_at": _to_utc_aware(
            analysis.get("analyzed_at", now)
        ),
        "updated_at": now,
    }

    db.collection(COLLECTION).document(username).set(safe_data)
