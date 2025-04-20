from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi import Query

from fastapi.responses import HTMLResponse

import json
import re
from pathlib import Path
from typing import List, Dict, Any

app = FastAPI()

# Пути к файлам
BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / "scrape" / "games.json"
LARGE_DATA_FILE = BASE_DIR / "scrape" / "games_large.json"
FRONTEND_DIR = BASE_DIR.parent / "frontend"


# Отдача статики (фронтенд)

def load_games_data() -> List[Dict[str, Any]]:
    """Загружает данные об играх из JSON файла"""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=500, detail="Games data file not found")
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_large_games_data() -> List[Dict[str, Any]]:
    """Загружает данные об играх из JSON файла"""
    if not LARGE_DATA_FILE.exists():
        raise HTTPException(status_code=500, detail="Games data file not found")
    
    with open(LARGE_DATA_FILE, "r", encoding="utf-8") as f:
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
    games = load_large_games_data()
    words = {}
    
    for game in games:
        name = game["name"]
        # Разбиваем название на слова и считаем частоту
        for word in name.split():
            word = re.sub(r'[^a-zA-Zа-яА-Я]', '', word).capitalize()
            if len(word) > 2 and word != "The":  # Игнорируем короткие слова
                words[word] = words.get(word, 0) + 1
    
    # Преобразуем в формат для wordcloud
    wordcloud_data = [{"text": word, "value": count} for word, count in words.items()]
    return wordcloud_data

@app.get("/api/genres")
async def get_genre_distribution(year: int = Query(None, description="Filter games by release year")):
    """Генерирует данные для circular packing по жанрам, опционально фильтруя по году"""
    games = load_games_data()
    genres = {}

    for game in games:
        if year and "releaseDate" in game:
            try:
                game_year = int(game["releaseDate"][-4:])
            except:
                continue
            if game_year != year:
                continue

        for genre in game.get("genres", []):
            genres[genre] = genres.get(genre, 0) + 1

    sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "name": "genres",
        "children": [{"name": genre, "value": count} for genre, count in sorted_genres]
    }

@app.get("/api/audience-overlap")
def get_audience_overlap():
    """Генерирует данные для пересечения аудитории"""
    data = load_games_data()  # Здесь берём список всех игр
    for game in data:
        if game.get("audienceOverlap"):
            center_game = {
                "id": game["steamId"],
                "name": game["name"]
            }
            overlap_nodes = [
                {
                    "id": g["steamId"],
                    "name": g["name"]
                } for g in game["audienceOverlap"]
            ]
            links = [
                {
                    "source": game["steamId"],
                    "target": g["steamId"],
                    "value": g["link"]
                } for g in game["audienceOverlap"]
            ]
            nodes = [center_game] + overlap_nodes
            return {"nodes": nodes, "links": links}
        
    return {"nodes": [], "links": []}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
