"""In-memory authoritative state for active games; database remains the completed-game record."""
import asyncio, random, string
from datetime import datetime
from typing import Any
from fastapi import WebSocket
from sqlalchemy.orm import Session
from . import models
from .config import settings

WORDS = [
    "ocean", "volcano", "guitar", "rocket", "elephant", "castle", "rainbow", "bicycle", "pizza", "robot",
    "astronaut", "butterfly", "cactus", "camera", "candle", "carrot", "cat", "chicken", "cloud", "coffee",
    "compass", "crown", "dinosaur", "dragon", "drum", "eagle", "fireworks", "fish", "flower", "football",
    "forest", "frog", "glasses", "hammer", "helicopter", "ice cream", "island", "jellyfish", "keyboard", "kite",
    "ladder", "lemon", "lightning", "lion", "lollipop", "magnet", "map", "mermaid", "microphone", "moon",
    "mountain", "mushroom", "octopus", "panda", "parachute", "parrot", "penguin", "piano", "pirate", "planet",
    "popcorn", "pumpkin", "puzzle", "rabbit", "race car", "sailboat", "sandcastle", "satellite", "shark", "shoe",
    "skateboard", "snowman", "spaceship", "spider", "star", "sun", "sunglasses", "telescope", "tent", "tiger",
    "toothbrush", "tornado", "train", "treehouse", "trophy", "turtle", "umbrella", "unicorn", "violin", "walrus",
    "waterfall", "whale", "windmill", "wizard", "zebra", "airplane", "anchor", "balloon", "book", "bridge",
]


class GameManager:
    def __init__(self):
        self.connections: dict[str, dict[int, WebSocket]] = {}
        self.ready: dict[str, set[int]] = {}
        self.correct: dict[str, set[int]] = {}
        self.active_round: dict[str, models.GameRound] = {}
        self.canvas: dict[str, list[dict[str, Any]]] = {}
        self.word_decks: dict[str, list[str]] = {}
        self.timers: dict[str, asyncio.Task] = {}
        self.lock = asyncio.Lock()

    async def connect(self, code: str, player_id: int, ws: WebSocket):
        await ws.accept()
        self.connections.setdefault(code, {})[player_id] = ws
        # A reconnecting client rebuilds the canvas from operations, never an image.
        await ws.send_json({"event": "canvas_state", "data": {"strokes": self.canvas.get(code, [])}})

    def disconnect(self, code: str, player_id: int, websocket: WebSocket) -> bool:
        """Remove only the socket that is still the player's active connection.

        Browsers (and React Strict Mode in development) can replace a socket
        before its old disconnect callback runs. That older callback must not
        mark the newly reconnected player as having left the room.
        """
        connections = self.connections.get(code, {})
        if connections.get(player_id) is not websocket:
            return False
        connections.pop(player_id, None)
        return True

    async def send(self, code: str, event: str, data: dict[str, Any], player_id: int | None = None):
        targets = {player_id: self.connections.get(code, {}).get(player_id)} if player_id else self.connections.get(code, {})
        for _, ws in list(targets.items()):
            if ws:
                try: await ws.send_json({"event": event, "data": data})
                except Exception: pass

    def players(self, db: Session, code: str):
        room = db.query(models.GameRoom).filter_by(room_code=code).first()
        return db.query(models.Player).filter_by(room_id=room.id, left_at=None).order_by(models.Player.joined_at).all()

    async def broadcast_lobby(self, db: Session, code: str):
        room = db.query(models.GameRoom).filter_by(room_code=code).first()
        players = self.players(db, code)
        await self.send(code, "lobby_update", {"room": room_payload(room), "players": players_payload(players), "ready": list(self.ready.get(code, set()))})

    async def start_game(self, db: Session, code: str, requested_by: int):
        room = db.query(models.GameRoom).filter_by(room_code=code).first()
        players = self.players(db, code)
        everyone_ready = {p.id for p in players}.issubset(self.ready.get(code, set()))
        if requested_by != room.admin_player_id: return "Only the room admin can start the game"
        if len(players) < 2: return "At least two players are required"
        if room.status != "lobby": return "This game has already started"
        if not everyone_ready: return "Every player must be ready before starting"
        room.status, room.started_at = "playing", datetime.utcnow(); db.commit()
        await self.start_round(db, code)
        return None

    async def complete_game(self, db: Session, code: str, reason: str):
        round_ = self.active_round.pop(code, None)
        task = self.timers.pop(code, None)
        if task and task is not asyncio.current_task(): task.cancel()
        room = db.query(models.GameRoom).filter_by(room_code=code).first()
        if not room or room.status == "completed": return
        if round_:
            persisted = db.get(models.GameRound, round_.id)
            if persisted and not persisted.ended_at: persisted.ended_at = datetime.utcnow()
        room.status, room.ended_at = "completed", datetime.utcnow()
        db.commit()
        await self.send(code, "game_completed", {"reason": reason, "leaderboard": players_payload(self.players(db, code))})

    async def start_round(self, db: Session, code: str):
        room = db.query(models.GameRoom).filter_by(room_code=code).first()
        players = self.players(db, code)
        if not players: return
        room.current_round += 1
        drawer = players[(room.current_round - 1) % len(players)]
        deck = self.word_decks.setdefault(code, [])
        if not deck:
            deck.extend(WORDS)
            random.shuffle(deck)
        round_ = models.GameRound(room_id=room.id, round_number=room.current_round, drawer_player_id=drawer.id, word=deck.pop())
        db.add(round_); db.commit(); db.refresh(round_)
        self.active_round[code], self.correct[code] = round_, set()
        self.canvas[code] = []
        await self.send(code, "round_started", {"round": room.current_round, "totalRounds": room.total_rounds, "drawerId": drawer.id, "seconds": room.round_seconds, "wordLength": len(round_.word)})
        await self.send(code, "secret_word", {"word": round_.word}, drawer.id)
        self.timers[code] = asyncio.create_task(self._countdown(code, round_.id, room.round_seconds))

    async def _countdown(self, code: str, round_id: int, seconds: int):
        for remaining in range(seconds, -1, -1):
            await self.send(code, "timer", {"remaining": remaining})
            await asyncio.sleep(1)
            if self.active_round.get(code) is None or self.active_round[code].id != round_id: return
        # A fresh database session is deliberately isolated from websocket handlers.
        from .database import SessionLocal
        db = SessionLocal()
        try: await self.end_round(db, code, "time")
        finally: db.close()

    async def end_round(self, db: Session, code: str, reason: str):
        round_ = self.active_round.pop(code, None)
        if not round_: return
        task = self.timers.pop(code, None)
        if task and task is not asyncio.current_task(): task.cancel()
        persisted = db.get(models.GameRound, round_.id); persisted.ended_at = datetime.utcnow()
        room = db.get(models.GameRoom, persisted.room_id); db.commit()
        await self.send(code, "round_ended", {"word": persisted.word, "reason": reason, "scores": players_payload(self.players(db, code))})
        await asyncio.sleep(3)
        if room.current_round >= room.total_rounds:
            await self.complete_game(db, code, "all_rounds_finished")
        else:
            await self.send(code, "canvas_clear", {})
            await self.start_round(db, code)

    async def guess(self, db: Session, code: str, player_id: int, text: str):
        round_ = self.active_round.get(code)
        if not round_ or not text.strip(): return
        if player_id == round_.drawer_player_id or player_id in self.correct.get(code, set()): return
        correct = text.strip().casefold() == round_.word.casefold()
        db.add(models.Guess(round_id=round_.id, player_id=player_id, guess_text=text.strip(), is_correct=correct))
        if correct:
            self.correct[code].add(player_id)
            player = db.get(models.Player, player_id)
            elapsed = int((datetime.utcnow() - round_.started_at).total_seconds())
            room = db.get(models.GameRoom, round_.room_id)
            time_bonus = max(0, room.round_seconds - elapsed)
            player.score += 100 + time_bonus + (round_.round_number * 10)
            await self.send(code, "correct_guess", {"playerId": player_id, "name": player.display_name, "scores": []})
        db.commit()
        await self.send(code, "chat_guess", {"playerId": player_id, "text": "guessed correctly!" if correct else text.strip(), "correct": correct})
        if correct: await self.send(code, "score_update", {"players": players_payload(self.players(db, code))})


def room_payload(room): return {"code": room.room_code, "status": room.status, "currentRound": room.current_round, "totalRounds": room.total_rounds, "roundSeconds": room.round_seconds, "adminPlayerId": room.admin_player_id}
def players_payload(players): return [{"id": p.id, "name": p.display_name, "score": p.score} for p in players]
def room_code(): return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
manager = GameManager()
