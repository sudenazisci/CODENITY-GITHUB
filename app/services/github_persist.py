from datetime import datetime
from app.core.firestore import db

def save_user_github_analysis(user_id: str, username: str, analysis: dict):
    db.collection("user_github_analysis").document(user_id).set({
        "githubUsername": username,
        "score": analysis["score"],
        "totalProjects": analysis["repo_count"],
        "activeProjects": analysis["active_repos"],
        "stars": analysis["stars"],
        "followers": analysis["followers"],
       "languages": analysis["languages"],
        "analyzedAt": datetime.utcnow(),
        "source": "github",
        "version": "v1"
    }, merge=True)
