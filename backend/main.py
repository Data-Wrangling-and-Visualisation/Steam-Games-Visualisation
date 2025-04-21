from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi import Query

from fastapi.responses import HTMLResponse

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import math
from collections import Counter

app = FastAPI()

BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / 'scrape' / "games.json"
LARGE_DATA_FILE = BASE_DIR / 'scrape' / "games_large.json"
FRONTEND_DIR = BASE_DIR.parent / 'frontend'

def load_games_data() -> List[Dict[str, Any]]:
    """Loads game data from a JSON file"""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=500, detail="Games data file not found")
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_large_games_data() -> List[Dict[str, Any]]:
    """Loads game data from a JSON file"""
    if not LARGE_DATA_FILE.exists():
        raise HTTPException(status_code=500, detail="Games data file not found")
    
    with open(LARGE_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/games")
async def get_games():
    """Returns the data of a specific gameReturns a list of all games"""
    return load_games_data()

@app.get("/api/games/{steam_id}")
async def get_game(steam_id: str):
    """Returns the data of a specific game"""
    games = load_games_data()
    for game in games:
        if game["steamId"] == steam_id:
            return game
    raise HTTPException(status_code=404, detail="Game not found")

@app.get("/api/wordcloud")
async def get_wordcloud_data():
    """Generates data for wordcloud from game titles"""
    games = load_large_games_data()
    words = {}
    
    for game in games:
        name = game["name"]
        
        for word in name.split():
            word = re.sub(r'[^a-zA-Zа-яА-Я]', '', word).capitalize()
            if len(word) > 2 and word != "The": 
                words[word] = words.get(word, 0) + 1
    
    wordcloud_data = [{"text": word, "value": count} for word, count in words.items()]
    return wordcloud_data

@app.get("/api/genres")
async def get_genre_distribution(year: int = Query(None, description="Filter games by release year")):
    """Generates data for circular packing by genre, optionally filtering by year"""
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
    
@app.get("/api/tags")
async def get_tag_distribution(year: int = Query(None, description="Filter games by release year")):
    """Get tag distribution data for circular packing"""
    games = load_games_data()
    tags = {}

    for game in games:
        if year and "releaseDate" in game:
            try:
                game_year = int(game["releaseDate"][-4:])
            except:
                continue
            if game_year != year:
                continue

        for genre in game.get("tags", []):
            tags[genre] = tags.get(genre, 0) + 1

    sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "name": "tags",
        "children": [{"name": tag, "value": count} for tag, count in sorted_tags]
    }

@app.get("/api/tags/{steam_id}")
async def get_game_genre_distribution(steam_id: str):
    """Generates data for circular packing by genres of a particular game"""
    games = load_games_data()
    game = None
    
    for g in games:
        if g["steamId"] == steam_id:
            game = g
            break
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    data = {
        "name": "tags",
        "children": [{"name": tag, "value": 1} for tag in game.get("tags", [])]
    }
    
    return data

@app.get("/api/audience-overlap")
def get_audience_overlap(percentage: int = Query(100, ge=10, le=100, description="Percentage of games to display")):
    """Generates data to intersect the audience of all games with the ability to select a percentage of games"""
    games = load_games_data()
    
    games_with_overlap = [game for game in games if game.get("audienceOverlap")]
    
    games_count = len(games_with_overlap)
    display_count = math.ceil(games_count * percentage / 100)
    
    sorted_games = sorted(
        games_with_overlap, 
        key=lambda g: len(g.get("audienceOverlap", [])), 
        reverse=True
    )[:display_count]
    
    nodes = []
    links = []
    node_ids = set() 
    
    for game in sorted_games:
        if not game.get("audienceOverlap"):
            continue
        if game["steamId"] not in node_ids:
            nodes.append({
                "id": game["steamId"],
                "name": game["name"]
            })
            node_ids.add(game["steamId"])
        
        for overlap_game in game["audienceOverlap"]:
            if overlap_game["steamId"] not in node_ids:
                nodes.append({
                    "id": overlap_game["steamId"],
                    "name": overlap_game["name"]
                })
                node_ids.add(overlap_game["steamId"])
            
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
    """Generates data to intersect the audience of a particular game"""
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

@app.get("/api/treemap/languages")
async def get_languages_treemap():
    """Generate treemap data for languages distribution in games"""
    games = load_games_data()
    languages_counter = Counter()
    
    for game in games:
        for language in game.get("languages", []):
            languages_counter[language] += 1
    
    treemap_data = {
        "name": "languages",
        "children": [
            {"name": language, "value": count} 
            for language, count in languages_counter.most_common(50)  # Limit to top 50
        ]
    }
    
    return treemap_data

@app.get("/api/treemap/publishers")
async def get_publishers_treemap():
    """Generate treemap data for publishers distribution in games"""
    games = load_games_data()
    publishers_counter = Counter()
    
    for game in games:
        for publisher in game.get("publishers", []):
            publishers_counter[publisher] += 1
    
    treemap_data = {
        "name": "publishers",
        "children": [
            {"name": publisher, "value": count} 
            for publisher, count in publishers_counter.most_common(50)  # Limit to top 50
        ]
    }
    
    return treemap_data

@app.get("/api/treemap/revenue")
async def get_revenue_treemap():
    """Generate treemap data for games by revenue"""
    games = load_games_data()
    
    games_with_revenue = []
    for game in games:
        revenue = 0
        if game.get("history") and len(game["history"]) > 0:
            sorted_history = sorted(game["history"], key=lambda x: x.get("timeStamp", 0), reverse=True)
            revenue = sorted_history[0].get("revenue", 0)
        
        if revenue > 0:
            games_with_revenue.append({
                "name": game["name"],
                "value": revenue
            })
    
    games_with_revenue.sort(key=lambda x: x["value"], reverse=True)
    top_games = games_with_revenue[:50]
    
    treemap_data = {
        "name": "revenue",
        "children": top_games
    }
    
    return treemap_data

@app.get("/api/treemap/players")
async def get_players_treemap():
    """Generate treemap data for games by player count"""
    games = load_games_data()
    
    games_with_players = []
    for game in games:
        players = 0
        if game.get("history") and len(game["history"]) > 0:
            sorted_history = sorted(game["history"], key=lambda x: x.get("timeStamp", 0), reverse=True)
            players = sorted_history[0].get("players", 0)
        
        if players > 0:
            games_with_players.append({
                "name": game["name"],
                "value": players
            })
    
    games_with_players.sort(key=lambda x: x["value"], reverse=True)
    top_games = games_with_players[:50]
    
    treemap_data = {
        "name": "players",
        "children": top_games
    }
    
    return treemap_data

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
