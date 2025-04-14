from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
from pathlib import Path
from typing import List, Dict, Any

app = FastAPI()

# Пути к файлам
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "scrape" / "games.json"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Отдача статики (фронтенд)

def load_games_data() -> List[Dict[str, Any]]:
    """Загружает данные об играх из JSON файла"""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=500, detail="Games data file not found")
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/games")
async def get_games():
    """Возвращает список всех игр"""
    return load_games_data()

@app.get("/api/games/{steam_id}")
async def get_game(steam_id: str):
    """Возвращает данные конкретной игры"""
    games = load_games_data()
    for game in games:
        if game["steamId"] == steam_id:
            return game
    raise HTTPException(status_code=404, detail="Game not found")

@app.get("/api/wordcloud")
async def get_wordcloud_data():
    """Генерирует данные для wordcloud из названий игр"""
    games = load_games_data()
    words = {}
    
    for game in games:
        name = game["name"]
        # Разбиваем название на слова и считаем частоту
        for word in name.split():
            word = word.strip(".,!?\"':;()[]{}")
            if len(word) > 2:  # Игнорируем короткие слова
                words[word] = words.get(word, 0) + 1
    
    # Преобразуем в формат для wordcloud
    wordcloud_data = [{"text": word, "value": count} for word, count in words.items()]
    return wordcloud_data

@app.get("/api/genres")
async def get_genres_data():
    """Генерирует данные для circular packing по жанрам"""
    games = load_games_data()
    genres = {}
    
    for game in games:
        for genre in game.get("genres", []):
            genres[genre] = genres.get(genre, 0) + 1
    
    # Сортируем по убыванию частоты
    sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    
    # Создаем структуру для circular packing
    data = {
        "name": "genres",
        "children": [{"name": genre, "value": count} for genre, count in sorted_genres]
    }
    
    return data

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)