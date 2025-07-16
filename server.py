#!/usr/bin/env python3
"""
Risk Game Multiplayer Server
WebSocket-based real-time multiplayer backend for Risk game
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Player:
    id: str
    name: str
    country: str
    color: str
    army: int
    reserve: int
    areas: List[str]
    bonus: int
    alive: bool
    websocket: Optional[WebSocket] = None

@dataclass
class GameState:
    id: str
    players: Dict[str, Player]
    countries: List[Dict]
    stage: str  # "waiting", "fortify", "battle", "ai_turn"
    turn: int
    current_player_id: str
    max_players: int
    created_at: datetime
    started: bool
    
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
            
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                
    async def broadcast(self, message: dict, exclude_client: str = None):
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.player_to_game: Dict[str, str] = {}
        
    def create_game(self, max_players: int = 6) -> str:
        game_id = str(uuid.uuid4())[:8]
        
        # Default countries data
        countries = [
            {"name": "indonesia", "continent": "oceania", "owner": "none", "color": "white", "army": 0, "neighbours": ["siam", "western_australia", "new_guinea"]},
            {"name": "new_guinea", "continent": "oceania", "owner": "none", "color": "white", "army": 0, "neighbours": ["indonesia", "eastern_australia", "western_australia"]},
            {"name": "eastern_australia", "continent": "oceania", "owner": "none", "color": "white", "army": 0, "neighbours": ["western_australia", "new_guinea"]},
            {"name": "western_australia", "continent": "oceania", "owner": "none", "color": "white", "army": 0, "neighbours": ["eastern_australia", "new_guinea", "indonesia"]},
            {"name": "ural", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["ukraine", "siberia", "afghanistan", "china"]},
            {"name": "siberia", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["ural", "mongolia", "yakutsk", "irkutsk", "china"]},
            {"name": "afghanistan", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["ukraine", "ural", "middle_east", "china", "india"]},
            {"name": "irkutsk", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["yakutsk", "siberia", "kamchatka", "mongolia"]},
            {"name": "yakutsk", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["irkutsk", "siberia", "kamchatka"]},
            {"name": "kamchatka", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["alaska", "yakutsk", "japan", "irkutsk", "mongolia"]},
            {"name": "middle_east", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["ukraine", "afghanistan", "india", "egypt", "east_africa", "southern_europe"]},
            {"name": "india", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["middle_east", "siam", "afghanistan", "china"]},
            {"name": "siam", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["indonesia", "india", "china"]},
            {"name": "china", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["ural", "siberia", "afghanistan", "mongolia", "siam", "india"]},
            {"name": "mongolia", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["irkutsk", "siberia", "kamchatka", "china", "japan"]},
            {"name": "japan", "continent": "asia", "owner": "none", "color": "white", "army": 0, "neighbours": ["kamchatka", "mongolia"]},
            {"name": "egypt", "continent": "africa", "owner": "none", "color": "white", "army": 0, "neighbours": ["middle_east", "southern_europe", "north_africa", "east_africa"]},
            {"name": "north_africa", "continent": "africa", "owner": "none", "color": "white", "army": 0, "neighbours": ["egypt", "southern_europe", "western_europe", "east_africa", "congo", "brazil"]},
            {"name": "east_africa", "continent": "africa", "owner": "none", "color": "white", "army": 0, "neighbours": ["middle_east", "egypt", "north_africa", "congo", "madagascar", "south_africa"]},
            {"name": "congo", "continent": "africa", "owner": "none", "color": "white", "army": 0, "neighbours": ["south_africa", "north_africa", "east_africa"]},
            {"name": "south_africa", "continent": "africa", "owner": "none", "color": "white", "army": 0, "neighbours": ["congo", "madagascar", "east_africa"]},
            {"name": "madagascar", "continent": "africa", "owner": "none", "color": "white", "army": 0, "neighbours": ["south_africa", "east_africa"]},
            {"name": "brazil", "continent": "South America", "owner": "none", "color": "white", "army": 0, "neighbours": ["peru", "argentina", "north_africa", "venezuela"]},
            {"name": "peru", "continent": "South America", "owner": "none", "color": "white", "army": 0, "neighbours": ["brazil", "argentina", "venezuela"]},
            {"name": "argentina", "continent": "South America", "owner": "none", "color": "white", "army": 0, "neighbours": ["brazil", "peru"]},
            {"name": "venezuela", "continent": "South America", "owner": "none", "color": "white", "army": 0, "neighbours": ["brazil", "peru", "central_america"]},
            {"name": "iceland", "continent": "europe", "owner": "none", "color": "white", "army": 0, "neighbours": ["greenland", "uk", "scandinavia"]},
            {"name": "scandinavia", "continent": "europe", "owner": "none", "color": "white", "army": 0, "neighbours": ["iceland", "uk", "ukraine", "northern_europe"]},
            {"name": "northern_europe", "continent": "europe", "owner": "none", "color": "white", "army": 0, "neighbours": ["ukraine", "uk", "scandinavia", "southern_europe", "western_europe"]},
            {"name": "western_europe", "continent": "europe", "owner": "none", "color": "white", "army": 0, "neighbours": ["north_africa", "uk", "northern_europe", "southern_europe"]},
            {"name": "southern_europe", "continent": "europe", "owner": "none", "color": "white", "army": 0, "neighbours": ["north_africa", "egypt", "northern_europe", "western_europe", "middle_east", "ukraine"]},
            {"name": "uk", "continent": "europe", "owner": "none", "color": "white", "army": 0, "neighbours": ["western_europe", "iceland", "northern_europe", "scandinavia"]},
            {"name": "ukraine", "continent": "europe", "owner": "none", "color": "white", "army": 0, "neighbours": ["scandinavia", "ural", "northern_europe", "southern_europe", "afghanistan", "middle_east"]},
            {"name": "greenland", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["iceland", "quebec", "ontario", "northwest_territory"]},
            {"name": "central_america", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["venezuela", "eastern_us", "western_us"]},
            {"name": "eastern_us", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["central_america", "quebec", "ontario", "western_us"]},
            {"name": "western_us", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["eastern_us", "central_america", "ontario", "alberta"]},
            {"name": "alaska", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["kamchatka", "alberta", "northwest_territory"]},
            {"name": "alberta", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["alaska", "western_us", "ontario", "northwest_territory"]},
            {"name": "ontario", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["greenland", "quebec", "alberta", "western_us", "eastern_us", "northwest_territory"]},
            {"name": "quebec", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["greenland", "eastern_us", "ontario"]},
            {"name": "northwest_territory", "continent": "North America", "owner": "none", "color": "white", "army": 0, "neighbours": ["greenland", "alaska", "alberta", "ontario"]}
        ]
        
        game_state = GameState(
            id=game_id,
            players={},
            countries=countries,
            stage="waiting",
            turn=1,
            current_player_id="",
            max_players=max_players,
            created_at=datetime.now(),
            started=False
        )
        
        self.games[game_id] = game_state
        logger.info(f"Created game {game_id}")
        return game_id
        
    def join_game(self, game_id: str, player: Player) -> bool:
        if game_id not in self.games:
            return False
            
        game = self.games[game_id]
        if len(game.players) >= game.max_players or game.started:
            return False
            
        game.players[player.id] = player
        self.player_to_game[player.id] = game_id
        
        logger.info(f"Player {player.name} joined game {game_id}")
        return True
        
    def leave_game(self, player_id: str):
        if player_id in self.player_to_game:
            game_id = self.player_to_game[player_id]
            if game_id in self.games:
                game = self.games[game_id]
                if player_id in game.players:
                    del game.players[player_id]
                    logger.info(f"Player {player_id} left game {game_id}")
                    
                # Remove empty games
                if len(game.players) == 0:
                    del self.games[game_id]
                    logger.info(f"Deleted empty game {game_id}")
                    
            del self.player_to_game[player_id]
            
    def start_game(self, game_id: str) -> bool:
        if game_id not in self.games:
            return False
            
        game = self.games[game_id]
        if len(game.players) < 2 or game.started:
            return False
            
        game.started = True
        game.stage = "fortify"
        
        # Assign colors and initial setup
        colors = ["#030f63", "#d6040e", "#d86b04", "#0eb7ae", "#104704", "#c6c617"]
        player_list = list(game.players.values())
        
        for i, player in enumerate(player_list):
            player.color = colors[i % len(colors)]
            player.army = 20
            player.reserve = 20
            player.bonus = 2
            player.alive = True
            
        # Set first player
        game.current_player_id = player_list[0].id
        
        # Distribute territories randomly
        areas = [country["name"] for country in game.countries]
        random.shuffle(areas)
        
        for i, area in enumerate(areas):
            player_index = i % len(player_list)
            player = player_list[player_index]
            
            # Find country and assign to player
            for country in game.countries:
                if country["name"] == area:
                    country["owner"] = player.name
                    country["color"] = player.color
                    country["army"] = random.randint(1, 3)
                    player.areas.append(area)
                    break
                    
        logger.info(f"Started game {game_id} with {len(game.players)} players")
        return True
        
    def get_game(self, game_id: str) -> Optional[GameState]:
        return self.games.get(game_id)
        
    def get_player_game(self, player_id: str) -> Optional[GameState]:
        if player_id in self.player_to_game:
            game_id = self.player_to_game[player_id]
            return self.games.get(game_id)
        return None

# Initialize managers
manager = ConnectionManager()
game_manager = GameManager()

# FastAPI app
app = FastAPI(title="Risk Game Server")

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.post("/api/games")
async def create_game(max_players: int = 6):
    game_id = game_manager.create_game(max_players)
    return {"game_id": game_id}

@app.get("/api/games/{game_id}")
async def get_game_info(game_id: str):
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {
        "id": game.id,
        "players": len(game.players),
        "max_players": game.max_players,
        "started": game.started,
        "stage": game.stage
    }

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    client_id = str(uuid.uuid4())
    
    try:
        await manager.connect(websocket, client_id)
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_message(client_id, game_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        game_manager.leave_game(client_id)
        
        # Notify other players
        await manager.broadcast({
            "type": "player_left",
            "player_id": client_id
        }, exclude_client=client_id)

async def handle_message(client_id: str, game_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    
    msg_type = message.get("type")
    
    if msg_type == "join_game":
        player = Player(
            id=client_id,
            name=message.get("name", "Player"),
            country=message.get("country", "Unknown"),
            color="#030f63",
            army=20,
            reserve=20,
            areas=[],
            bonus=2,
            alive=True
        )
        
        if game_manager.join_game(game_id, player):
            game = game_manager.get_game(game_id)
            
            # Send game state to new player
            await manager.send_personal_message({
                "type": "game_joined",
                "game": asdict(game) if game else None
            }, client_id)
            
            # Notify other players
            await manager.broadcast({
                "type": "player_joined",
                "player": asdict(player)
            }, exclude_client=client_id)
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": "Could not join game"
            }, client_id)
            
    elif msg_type == "start_game":
        if game_manager.start_game(game_id):
            game = game_manager.get_game(game_id)
            await manager.broadcast({
                "type": "game_started",
                "game": asdict(game) if game else None
            })
            
    elif msg_type == "place_army":
        game = game_manager.get_player_game(client_id)
        if game and game.current_player_id == client_id:
            country_name = message.get("country")
            amount = message.get("amount", 1)
            
            # Handle army placement logic
            player = game.players[client_id]
            
            if player.reserve >= amount:
                for country in game.countries:
                    if country["name"] == country_name and country["owner"] == player.name:
                        country["army"] += amount
                        player.reserve -= amount
                        break
                        
                # Broadcast updated game state
                await manager.broadcast({
                    "type": "army_placed",
                    "game": asdict(game)
                })
                
    elif msg_type == "attack":
        game = game_manager.get_player_game(client_id)
        if game and game.current_player_id == client_id:
            attacker_country = message.get("from")
            defender_country = message.get("to")
            
            # Handle attack logic (simplified)
            attack_result = handle_attack(game, attacker_country, defender_country, client_id)
            
            await manager.broadcast({
                "type": "attack_result",
                "result": attack_result,
                "game": asdict(game)
            })
            
    elif msg_type == "end_turn":
        game = game_manager.get_player_game(client_id)
        if game and game.current_player_id == client_id:
            # Move to next player
            player_ids = list(game.players.keys())
            current_index = player_ids.index(client_id)
            next_index = (current_index + 1) % len(player_ids)
            game.current_player_id = player_ids[next_index]
            
            await manager.broadcast({
                "type": "turn_ended",
                "game": asdict(game)
            })

def handle_attack(game: GameState, attacker_name: str, defender_name: str, player_id: str) -> dict:
    """Handle attack between two countries"""
    
    attacker_country = None
    defender_country = None
    
    for country in game.countries:
        if country["name"] == attacker_name:
            attacker_country = country
        elif country["name"] == defender_name:
            defender_country = country
            
    if not attacker_country or not defender_country:
        return {"success": False, "message": "Invalid countries"}
        
    if attacker_country["army"] <= 1:
        return {"success": False, "message": "Not enough armies to attack"}
        
    # Simple battle logic
    attacker_wins = random.random() > 0.4  # 60% chance for attacker
    
    if attacker_wins:
        # Attacker wins - transfer territory
        old_owner = defender_country["owner"]
        defender_country["owner"] = attacker_country["owner"]
        defender_country["color"] = attacker_country["color"]
        
        # Update player areas
        for player in game.players.values():
            if player.name == old_owner and defender_name in player.areas:
                player.areas.remove(defender_name)
            elif player.name == attacker_country["owner"]:
                player.areas.append(defender_name)
                
        # Distribute armies
        total_armies = attacker_country["army"] + defender_country["army"]
        attacker_country["army"] = max(1, total_armies // 2)
        defender_country["army"] = total_armies - attacker_country["army"]
        
        return {
            "success": True,
            "winner": "attacker",
            "message": f"{attacker_name} conquered {defender_name}"
        }
    else:
        # Defender wins
        attacker_country["army"] = max(0, attacker_country["army"] - 2)
        defender_country["army"] = max(1, defender_country["army"])
        
        return {
            "success": True,
            "winner": "defender", 
            "message": f"{defender_name} defended successfully"
        }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )