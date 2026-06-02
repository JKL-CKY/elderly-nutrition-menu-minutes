from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from backend import elderly_router, nutrition_router, meeting_router, menu_router
import os

app = FastAPI(title="养老院膳食营养管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(elderly_router)
app.include_router(nutrition_router)
app.include_router(meeting_router)
app.include_router(menu_router)

os.makedirs("frontend/static", exist_ok=True)
os.makedirs("frontend/templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/elderly")
async def elderly_page(request: Request):
    return templates.TemplateResponse("elderly.html", {"request": request})

@app.get("/nutrition")
async def nutrition_page(request: Request):
    return templates.TemplateResponse("nutrition.html", {"request": request})

@app.get("/meeting")
async def meeting_page(request: Request):
    return templates.TemplateResponse("meeting.html", {"request": request})

@app.get("/menu")
async def menu_page(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
