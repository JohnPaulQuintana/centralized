from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.routes import views, auth, sheets
from app.routes.team import monitoring

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount static assets and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include route modules
app.include_router(views.router)
app.include_router(auth.router)
app.include_router(sheets.router)

# Include monitoring routes
app.include_router(monitoring.router)
