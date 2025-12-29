import requests
from collections import Counter
from datetime import datetime

from app.core.config import GITHUB_HEADERS
from app.services.github_cache import get_cached_analysis, save_analysis
from app.services.github_persist import save_user_github_analysis


def analyze_github(username: str, user_id: str | None = None):
    """
    - Önce cache kontrol eder
    - Cache varsa onu döner
    - Yoksa GitHub API'den analiz eder
    - Sonucu cache'e kaydeder
    - user_id varsa kalıcı olarak Firestore'a yazar

    GARANTİ:
    - Asla None dönmez
    - Her zaman dict döner
    - ok: True / False standardı vardır
    """

    # 1️⃣ CACHE KONTROL
    cached = get_cached_analysis(username)
    if cached:
        cached["ok"] = True
        cached["cached"] = True

        if user_id:
            save_user_github_analysis(user_id, username, cached)

        return cached

    # 2️⃣ GITHUB USER BİLGİSİ
    user_res = requests.get(
        f"https://api.github.com/users/{username}",
        headers=GITHUB_HEADERS
    )

    if user_res.status_code != 200:
        return {
            "ok": False,
            "error": "GitHub kullanıcısı bulunamadı"
        }

    user = user_res.json()

    # 3️⃣ REPO BİLGİLERİ (GÜVENLİ)
    repos_res = requests.get(
        f"https://api.github.com/users/{username}/repos?per_page=100",
        headers=GITHUB_HEADERS
    )

    if repos_res.status_code != 200:
        return {
            "ok": False,
            "error": "GitHub repo bilgileri alınamadı"
        }

    repos = repos_res.json()

    languages = []
    stars = 0
    active_repos = 0

    for repo in repos:
        if repo.get("language"):
            languages.append(repo["language"])

        stars += repo.get("stargazers_count", 0)

        updated_at = repo.get("updated_at")
        if updated_at:
            updated = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
            if (datetime.utcnow() - updated).days <= 90:
                active_repos += 1

    # 4️⃣ SKOR HESAPLAMA
    score = (
        user.get("public_repos", 0) * 2 +
        user.get("followers", 0) * 3 +
        stars * 1.5 +
        active_repos * 5
    )

    top_languages = [
        lang for lang, _ in Counter(languages).most_common(10)
    ]

    # 5️⃣ ANALİZ SONUCU (STANDART FORMAT)
    analysis = {
        "ok": True,
        "username": username,
        "score": round(score, 1),
        "repo_count": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "stars": stars,
        "active_repos": active_repos,
        "languages": top_languages,
        "analyzed_at": datetime.utcnow().isoformat(),
        "cached": False
    }

    # 6️⃣ CACHE'E KAYDET
    save_analysis(username, analysis)

    # 7️⃣ USER'A KALICI OLARAK BAĞLA
    if user_id:
        save_user_github_analysis(user_id, username, analysis)

    return analysis
