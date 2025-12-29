import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_manager_summary(
    github_analysis: dict,
    about_text: str,
    job_post: dict
):
    """
    Manager için geliştirici AI özeti üretir (OpenRouter)
    ÇIKTI: SADECE TÜRKÇE
    """

    # 🛡️ Güvenlik – None gelirse patlamasın
    github_analysis = github_analysis or {}
    job_post = job_post or {}
    about_text = about_text or "Başvuru metni paylaşılmamış."

    prompt = f"""
Sen deneyimli bir teknik proje yöneticisi asistanısın.
Adın Cody.

Aşağıdaki verileri kullanarak **proje yöneticisi için Türkçe bir geliştirici değerlendirmesi yaz**.

❗ KURALLAR (ÇOK ÖNEMLİ):
- SADECE TÜRKÇE yaz
- 4–6 cümle uzunluğunda olsun
- Teknik detaya boğma
- CV dili kullanma
- Abartma yapma
- Veri yoksa uydurma
- GitHub verileri ile başvuru metni çelişiyorsa bunu NAZİKÇE belirt

---

📊 GitHub Analizi:
- Genel Skor: {github_analysis.get("score")}
- Toplam Repo: {github_analysis.get("repo_count")}
- Son 90 Gün Aktif Repo: {github_analysis.get("active_repos")}
- Yıldız Sayısı: {github_analysis.get("stars")}
- Takipçi Sayısı: {github_analysis.get("followers")}
- Kullanılan Diller: {", ".join(github_analysis.get("languages", []))}

👤 Geliştirici Başvuru Metni:
\"\"\"
{about_text}
\"\"\"

📌 Proje Bilgileri:
- Gerekli Teknolojiler: {job_post.get("requiredTech")}
- Proje Türü: {job_post.get("projectType")}
- Süre: {job_post.get("duration")}

---

🎯 ÇIKTI:
Proje yöneticisinin hızlı karar vermesine yardımcı olacak,
net, profesyonel ve Türkçe bir değerlendirme yaz.
"""

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://codenity.app",
            "X-Title": "Codenity AI Manager Summary"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are Cody, an AI assistant that MUST respond only in Turkish."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        },
        timeout=30
    )

    if response.status_code != 200:
        return "AI analizi şu anda üretilemedi. Lütfen daha sonra tekrar deneyin."

    return response.json()["choices"][0]["message"]["content"]
