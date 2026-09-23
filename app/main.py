import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import achievement, auth, copilot, data, datasets, files, filters, product_runs, products, profile, reports, skills, upload_jobs, workspaces, newsletter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(
    title="PharmaLens AI API", 
    version="1.0.0",
    redirect_slashes=True
)

# Production CORS is environment-driven. Development defaults live in Settings.
settings.validate_production()
allowed_origins = settings.cors_origin_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Location", "Upload-Offset", "Upload-Length", "Tus-Resumable",
        "Tus-Version", "Tus-Extension", "Tus-Max-Size", "X-Signature",
        "Content-Type", "Authorization",
    ],
)

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(profile.router)
app.include_router(files.router)
app.include_router(datasets.router)
app.include_router(filters.router)
app.include_router(products.router)
app.include_router(product_runs.router)
app.include_router(copilot.router)
app.include_router(reports.router)
app.include_router(data.router)
app.include_router(achievement.router)
app.include_router(upload_jobs.router)
app.include_router(skills.router)
app.include_router(newsletter.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "env": settings.env}
