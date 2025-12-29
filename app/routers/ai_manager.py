from fastapi import APIRouter
from app.services.ai_manager_summary import generate_manager_summary
from app.services.github_analyzer import analyze_github   # 🔥 EKLENDİ

router = APIRouter(
    prefix="/ai/manager",
    tags=["AI Manager"]
)

@router.post("/developer-summary")
def developer_summary(payload: dict):
    """
    Manager için geliştirici AI özeti
    """

    github_username = payload.get("githubUsername")
    about_text = payload.get("aboutText", "")
    job_post = payload.get("jobPost", {})

    # 🔒 ZORUNLU KONTROL
    if not github_username:
        return {
            "summary": "GitHub kullanıcı adı gönderilmediği için analiz yapılamadı."
        }

    # 1️⃣ ÖNCE GITHUB ANALİZ
    github_analysis = analyze_github(github_username)

    # 2️⃣ GITHUB ANALİZİ BAŞARISIZSA
    if not github_analysis or not github_analysis.get("ok"):
        return {
            "summary": github_analysis.get(
                "error",
                "GitHub analizi alınamadığı için AI değerlendirmesi yapılamadı."
            )
        }

    # 3️⃣ SONRA AI YORUM
    summary = generate_manager_summary(
        github_analysis=github_analysis,
        about_text=about_text,
        job_post=job_post
    )

    return {
        "summary": summary
    }
