from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import os

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пути к файлам
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "scrape" / "games_large.json"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Отдача статики (фронтенд)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Загрузка данных
def load_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

# API эндпоинты
@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/api/game")
def get_game_info():
    data = load_data()
    return JSONResponse({
        "steamId": data["steamId"],
        "name": data["name"],
        "price": data["price"],
        "avgPlaytime": data.get("avgPlaytime", 0),
        "reviews": data.get("reviews", 0),
        "isIndie": data.get("isIndie", False),
        "sales": data.get("sales", 0),
        "releaseDate": data["releaseDate"],
        "developers": data["developers"],
        "publishers": data["publishers"]
    })

@app.get("/api/tags")
def get_tags():
    data = load_data()
    return JSONResponse({"tags": data.get("tags", [])})

@app.get("/api/gender-distribution")
def get_gender_distribution():
    data = load_data()
    
    # Проверка на наличие списка пользователей в данных
    users = data.get("users", [])
    
    # Считаем количество каждого пола
    gender_counts = {
        "Male": 0,
        "Female": 0,
        "Other": 0
    }
    
    for user in users:
        gender = user.get("gender")
        if gender == "Male":
            gender_counts["Male"] += 1
        elif gender == "Female":
            gender_counts["Female"] += 1
        else:
            gender_counts["Other"] += 1
    
    # Возвращаем результат в нужном формате
    return JSONResponse([
        {"gender": "Male", "count": gender_counts["Male"]},
        {"gender": "Female", "count": gender_counts["Female"]},
        {"gender": "Other", "count": gender_counts["Other"]}
    ])


@app.get("/api/indie-vs-aaa")
def get_indie_vs_aaa():
    data = load_data()
    is_indie = data.get("isIndie", False)
    return JSONResponse([
        {"type": "Indie", "count": 1 if is_indie else 0},
        {"type": "AAA", "count": 1 if not is_indie else 0}
    ])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)