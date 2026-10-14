from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter(prefix="/api", tags=["history"])

@router.get("/leaderboard")
def global_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    """All-time player score ranking across persisted games."""
    players = db.query(models.Player).order_by(models.Player.score.desc(), models.Player.joined_at).limit(min(max(limit, 1), 100)).all()
    return [{"rank": index + 1, "playerId": player.id, "displayName": player.display_name, "score": player.score, "roomCode": db.get(models.GameRoom, player.room_id).room_code} for index, player in enumerate(players)]

@router.get("/history")
def completed_games(db: Session = Depends(get_db)):
    rooms = db.query(models.GameRoom).filter_by(status="completed").order_by(models.GameRoom.ended_at.desc()).limit(20).all()
    result = []
    for room in rooms:
        players = db.query(models.Player).filter_by(room_id=room.id).order_by(models.Player.score.desc()).all()
        rounds = db.query(models.GameRound).filter_by(room_id=room.id).order_by(models.GameRound.round_number).all()
        result.append({"roomCode": room.room_code, "startedAt": room.started_at, "endedAt": room.ended_at, "totalRounds": room.total_rounds, "roundSeconds": room.round_seconds, "winner": players[0].display_name if players else None, "players": [{"name": p.display_name, "score": p.score} for p in players], "rounds": [{"number": r.round_number, "word": r.word} for r in rounds]})
    return result

@router.get("/rooms/{code}/history")
def history(code: str, db: Session = Depends(get_db)):
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    if not room: raise HTTPException(404, "Room not found")
    rounds = db.query(models.GameRound).filter_by(room_id=room.id).all()
    return {"roomCode": room.room_code, "status": room.status, "rounds": [{"number": r.round_number, "word": r.word, "startedAt": r.started_at, "endedAt": r.ended_at} for r in rounds]}

@router.get("/rooms/{code}/leaderboard")
def leaderboard(code: str, db: Session = Depends(get_db)):
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    if not room: raise HTTPException(404, "Room not found")
    players = db.query(models.Player).filter_by(room_id=room.id).order_by(models.Player.score.desc()).all()
    return [{"playerId": p.id, "displayName": p.display_name, "score": p.score} for p in players]

@router.get("/players/{player_id}/stats")
def player_stats(player_id: int, db: Session = Depends(get_db)):
    player = db.get(models.Player, player_id)
    if not player: raise HTTPException(404, "Player not found")
    correct = db.query(func.count(models.Guess.id)).filter_by(player_id=player_id, is_correct=True).scalar()
    return {"playerId": player.id, "displayName": player.display_name, "score": player.score, "correctGuesses": correct}

@router.get("/players/{player_id}/games")
def player_games(player_id: int, db: Session = Depends(get_db)):
    player = db.get(models.Player, player_id)
    if not player: raise HTTPException(404, "Player not found")
    room = db.get(models.GameRoom, player.room_id)
    rounds_drawn = db.query(func.count(models.GameRound.id)).filter_by(room_id=room.id, drawer_player_id=player_id).scalar()
    correct = db.query(func.count(models.Guess.id)).filter_by(player_id=player_id, is_correct=True).scalar()
    return [{"roomCode": room.room_code, "status": room.status, "score": player.score, "joinedAt": player.joined_at, "gameStartedAt": room.started_at, "gameEndedAt": room.ended_at, "roundsDrawn": rounds_drawn, "correctGuesses": correct}]
