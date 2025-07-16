#!/usr/bin/env python3
"""
Unit tests for Risk Game Multiplayer Server
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import uuid

from server import (
    app, manager, game_manager, handle_message, handle_attack,
    Player, GameState, ConnectionManager, GameManager
)

class TestConnectionManager:
    def test_init(self):
        cm = ConnectionManager()
        assert cm.active_connections == {}
    
    @pytest.mark.asyncio
    async def test_connect(self):
        cm = ConnectionManager()
        mock_websocket = AsyncMock()
        client_id = "test_client"
        
        await cm.connect(mock_websocket, client_id)
        
        mock_websocket.accept.assert_called_once()
        assert cm.active_connections[client_id] == mock_websocket
    
    def test_disconnect(self):
        cm = ConnectionManager()
        client_id = "test_client"
        cm.active_connections[client_id] = Mock()
        
        cm.disconnect(client_id)
        
        assert client_id not in cm.active_connections
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        cm = ConnectionManager()
        mock_websocket = AsyncMock()
        client_id = "test_client"
        cm.active_connections[client_id] = mock_websocket
        
        message = {"type": "test", "data": "hello"}
        await cm.send_personal_message(message, client_id)
        
        mock_websocket.send_text.assert_called_once_with(json.dumps(message))
    
    @pytest.mark.asyncio
    async def test_broadcast(self):
        cm = ConnectionManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        cm.active_connections["client1"] = mock_ws1
        cm.active_connections["client2"] = mock_ws2
        
        message = {"type": "broadcast", "data": "hello all"}
        await cm.broadcast(message, exclude_client="client1")
        
        mock_ws1.send_text.assert_not_called()
        mock_ws2.send_text.assert_called_once_with(json.dumps(message))

class TestPlayer:
    def test_player_creation(self):
        player = Player(
            id="test_id",
            name="Test Player",
            country="Test Country",
            color="#FF0000",
            army=20,
            reserve=10,
            areas=["area1", "area2"],
            bonus=2,
            alive=True
        )
        
        assert player.id == "test_id"
        assert player.name == "Test Player"
        assert player.country == "Test Country"
        assert player.color == "#FF0000"
        assert player.army == 20
        assert player.reserve == 10
        assert player.areas == ["area1", "area2"]
        assert player.bonus == 2
        assert player.alive is True

class TestGameManager:
    def test_create_game(self):
        gm = GameManager()
        game_id = gm.create_game(max_players=4)
        
        assert len(game_id) == 8
        assert game_id in gm.games
        game = gm.games[game_id]
        assert game.max_players == 4
        assert game.started is False
        assert len(game.countries) == 42
    
    def test_join_game_success(self):
        gm = GameManager()
        game_id = gm.create_game()
        player = Player(
            id="player1",
            name="Test Player",
            country="Test Country",
            color="#FF0000",
            army=20,
            reserve=10,
            areas=[],
            bonus=2,
            alive=True
        )
        
        result = gm.join_game(game_id, player)
        
        assert result is True
        assert player.id in gm.games[game_id].players
        assert gm.player_to_game[player.id] == game_id
    
    def test_join_game_failure_nonexistent(self):
        gm = GameManager()
        player = Player(
            id="player1",
            name="Test Player",
            country="Test Country",
            color="#FF0000",
            army=20,
            reserve=10,
            areas=[],
            bonus=2,
            alive=True
        )
        
        result = gm.join_game("nonexistent", player)
        
        assert result is False
    
    def test_join_game_failure_full(self):
        gm = GameManager()
        game_id = gm.create_game(max_players=1)
        
        # First player should succeed
        player1 = Player(
            id="player1",
            name="Player 1",
            country="Country 1",
            color="#FF0000",
            army=20,
            reserve=10,
            areas=[],
            bonus=2,
            alive=True
        )
        result1 = gm.join_game(game_id, player1)
        assert result1 is True
        
        # Second player should fail
        player2 = Player(
            id="player2",
            name="Player 2",
            country="Country 2",
            color="#00FF00",
            army=20,
            reserve=10,
            areas=[],
            bonus=2,
            alive=True
        )
        result2 = gm.join_game(game_id, player2)
        assert result2 is False
    
    def test_start_game_success(self):
        gm = GameManager()
        game_id = gm.create_game()
        
        # Add two players
        for i in range(2):
            player = Player(
                id=f"player{i}",
                name=f"Player {i}",
                country=f"Country {i}",
                color=f"#FF000{i}",
                army=20,
                reserve=10,
                areas=[],
                bonus=2,
                alive=True
            )
            gm.join_game(game_id, player)
        
        result = gm.start_game(game_id)
        
        assert result is True
        game = gm.games[game_id]
        assert game.started is True
        assert game.stage == "fortify"
        assert game.current_player_id in game.players
        
        # Check territory distribution
        total_assigned = sum(len(player.areas) for player in game.players.values())
        assert total_assigned == 42
    
    def test_start_game_failure_not_enough_players(self):
        gm = GameManager()
        game_id = gm.create_game()
        
        # Add only one player
        player = Player(
            id="player1",
            name="Player 1",
            country="Country 1",
            color="#FF0000",
            army=20,
            reserve=10,
            areas=[],
            bonus=2,
            alive=True
        )
        gm.join_game(game_id, player)
        
        result = gm.start_game(game_id)
        
        assert result is False
    
    def test_leave_game(self):
        gm = GameManager()
        game_id = gm.create_game()
        player = Player(
            id="player1",
            name="Player 1",
            country="Country 1",
            color="#FF0000",
            army=20,
            reserve=10,
            areas=[],
            bonus=2,
            alive=True
        )
        gm.join_game(game_id, player)
        
        gm.leave_game(player.id)
        
        assert player.id not in gm.games[game_id].players
        assert player.id not in gm.player_to_game
    
    def test_leave_game_removes_empty_game(self):
        gm = GameManager()
        game_id = gm.create_game()
        player = Player(
            id="player1",
            name="Player 1",
            country="Country 1",
            color="#FF0000",
            army=20,
            reserve=10,
            areas=[],
            bonus=2,
            alive=True
        )
        gm.join_game(game_id, player)
        
        gm.leave_game(player.id)
        
        assert game_id not in gm.games

class TestAttackLogic:
    def test_handle_attack_invalid_countries(self):
        game = GameState(
            id="test_game",
            players={},
            countries=[],
            stage="battle",
            turn=1,
            current_player_id="player1",
            max_players=6,
            created_at=None,
            started=True
        )
        
        result = handle_attack(game, "nonexistent1", "nonexistent2", "player1")
        
        assert result["success"] is False
        assert "Invalid countries" in result["message"]
    
    def test_handle_attack_not_enough_armies(self):
        countries = [
            {"name": "country1", "army": 1, "owner": "Player1"},
            {"name": "country2", "army": 5, "owner": "Player2"}
        ]
        game = GameState(
            id="test_game",
            players={},
            countries=countries,
            stage="battle",
            turn=1,
            current_player_id="player1",
            max_players=6,
            created_at=None,
            started=True
        )
        
        result = handle_attack(game, "country1", "country2", "player1")
        
        assert result["success"] is False
        assert "Not enough armies" in result["message"]
    
    def test_handle_attack_attacker_wins(self):
        # Mock random to always favor attacker
        import random
        original_random = random.random
        random.random = lambda: 0.1  # Always < 0.4, so attacker wins
        
        try:
            players = {
                "player1": Player(
                    id="player1",
                    name="Player1",
                    country="Country1",
                    color="#FF0000",
                    army=20,
                    reserve=10,
                    areas=["country1"],
                    bonus=2,
                    alive=True
                ),
                "player2": Player(
                    id="player2",
                    name="Player2",
                    country="Country2",
                    color="#00FF00",
                    army=20,
                    reserve=10,
                    areas=["country2"],
                    bonus=2,
                    alive=True
                )
            }
            
            countries = [
                {"name": "country1", "army": 5, "owner": "Player1", "color": "#FF0000"},
                {"name": "country2", "army": 3, "owner": "Player2", "color": "#00FF00"}
            ]
            
            game = GameState(
                id="test_game",
                players=players,
                countries=countries,
                stage="battle",
                turn=1,
                current_player_id="player1",
                max_players=6,
                created_at=None,
                started=True
            )
            
            result = handle_attack(game, "country1", "country2", "player1")
            
            assert result["success"] is True
            assert result["winner"] == "attacker"
            assert "conquered" in result["message"]
            
            # Check territory transfer
            country2 = next(c for c in game.countries if c["name"] == "country2")
            assert country2["owner"] == "Player1"
            assert country2["color"] == "#FF0000"
            
        finally:
            random.random = original_random

class TestAPIEndpoints:
    def test_create_game_endpoint(self):
        client = TestClient(app)
        response = client.post("/api/games", json={"max_players": 4})
        
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert len(data["game_id"]) == 8
    
    def test_get_game_info_success(self):
        client = TestClient(app)
        
        # First create a game
        create_response = client.post("/api/games")
        game_id = create_response.json()["game_id"]
        
        # Then get game info
        response = client.get(f"/api/games/{game_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == game_id
        assert data["players"] == 0
        assert data["max_players"] == 6
        assert data["started"] is False
        assert data["stage"] == "waiting"
    
    def test_get_game_info_not_found(self):
        client = TestClient(app)
        response = client.get("/api/games/nonexistent")
        
        assert response.status_code == 404
        assert "Game not found" in response.json()["detail"]

@pytest.mark.asyncio
class TestWebSocketHandling:
    async def test_handle_join_game_message(self):
        # Setup
        game_manager.games.clear()
        game_manager.player_to_game.clear()
        
        game_id = game_manager.create_game()
        client_id = "test_client"
        
        # Mock the manager
        original_send = manager.send_personal_message
        original_broadcast = manager.broadcast
        manager.send_personal_message = AsyncMock()
        manager.broadcast = AsyncMock()
        
        try:
            message = {
                "type": "join_game",
                "name": "Test Player",
                "country": "Test Country"
            }
            
            await handle_message(client_id, game_id, message)
            
            # Verify player was added
            assert client_id in game_manager.games[game_id].players
            player = game_manager.games[game_id].players[client_id]
            assert player.name == "Test Player"
            assert player.country == "Test Country"
            
            # Verify messages were sent
            manager.send_personal_message.assert_called_once()
            manager.broadcast.assert_called_once()
            
        finally:
            manager.send_personal_message = original_send
            manager.broadcast = original_broadcast
    
    async def test_handle_start_game_message(self):
        # Setup
        game_manager.games.clear()
        game_manager.player_to_game.clear()
        
        game_id = game_manager.create_game()
        
        # Add two players
        for i in range(2):
            player = Player(
                id=f"player{i}",
                name=f"Player {i}",
                country=f"Country {i}",
                color="#FF0000",
                army=20,
                reserve=10,
                areas=[],
                bonus=2,
                alive=True
            )
            game_manager.join_game(game_id, player)
        
        # Mock the manager
        original_broadcast = manager.broadcast
        manager.broadcast = AsyncMock()
        
        try:
            message = {"type": "start_game"}
            
            await handle_message("player0", game_id, message)
            
            # Verify game was started
            game = game_manager.games[game_id]
            assert game.started is True
            
            # Verify broadcast was called
            manager.broadcast.assert_called_once()
            
        finally:
            manager.broadcast = original_broadcast

if __name__ == "__main__":
    pytest.main([__file__, "-v"])