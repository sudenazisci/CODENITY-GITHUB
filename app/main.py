from fastapi import FastAPI
from app.routers.github import router as github_router
from app.routers.ai_manager import router as ai_manager_router

app = FastAPI(title="Codenity GitHub Analyzer")

# Router SADECE 1 KEZ eklenir
app.include_router(github_router)
app.include_router(ai_manager_router) 

@app.get("/")
def root():
    return {"status": "Codenity Backend Running"}
