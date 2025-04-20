from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi import Query

from fastapi.responses import HTMLResponse

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import math

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

@app.get("/api/genres/{steam_id}")
async def get_game_genre_distribution(steam_id: str):
    """Генерирует данные для circular packing по жанрам конкретной игры"""
    games = load_games_data()
    game = None
    
    for g in games:
        if g["steamId"] == steam_id:
            game = g
            break
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Создаем структуру для circular packing только для жанров выбранной игры
    data = {
        "name": "genres",
        "children": [{"name": genre, "value": 1} for genre in game.get("genres", [])]
    }
    
    return data

@app.get("/api/audience-overlap")
def get_audience_overlap(percentage: int = Query(100, ge=10, le=100, description="Percentage of games to display")):
    """Генерирует данные для пересечения аудитории всех игр с возможностью выбора процента игр"""
    games = load_games_data()  # Загружаем список всех игр
    
    # Фильтруем только игры с данными о пересечении аудитории
    games_with_overlap = [game for game in games if game.get("audienceOverlap")]
    
    # Вычисляем количество игр для отображения на основе выбранного процента
    games_count = len(games_with_overlap)
    display_count = math.ceil(games_count * percentage / 100)
    
    # Берем только нужное количество игр (сортируем по количеству связей для отображения наиболее связанных)
    sorted_games = sorted(
        games_with_overlap, 
        key=lambda g: len(g.get("audienceOverlap", [])), 
        reverse=True
    )[:display_count]
    
    # Создаем списки для узлов и связей
    nodes = []
    links = []
    node_ids = set()  # Для отслеживания уже добавленных узлов
    
    # Проходим по отфильтрованным играм и собираем данные о пересечении аудитории
    for game in sorted_games:
        if not game.get("audienceOverlap"):
            continue
            
        # Добавляем текущую игру как узел, если её ещё нет
        if game["steamId"] not in node_ids:
            nodes.append({
                "id": game["steamId"],
                "name": game["name"]
            })
            node_ids.add(game["steamId"])
        
        # Добавляем связанные игры и связи
        for overlap_game in game["audienceOverlap"]:
            # Добавляем связанную игру как узел, если её ещё нет
            if overlap_game["steamId"] not in node_ids:
                nodes.append({
                    "id": overlap_game["steamId"],
                    "name": overlap_game["name"]
                })
                node_ids.add(overlap_game["steamId"])
            
            # Добавляем связь между играми
            links.append({
                "source": game["steamId"],
                "target": overlap_game["steamId"],
                "value": overlap_game["link"]
            })
    
    return {
        "nodes": nodes, 
        "links": links,
        "totalGames": games_count,
        "displayedGames": len(sorted_games),
        "percentage": percentage
    }

@app.get("/api/audience-overlap/{steam_id}")
def get_game_audience_overlap(steam_id: str):
    """Генерирует данные для пересечения аудитории конкретной игры"""
    games = load_games_data()
    game = None
    
    for g in games:
        if g["steamId"] == steam_id:
            game = g
            break
    
    if not game or not game.get("audienceOverlap"):
        raise HTTPException(status_code=404, detail="Game or audience overlap data not found")
    
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

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
