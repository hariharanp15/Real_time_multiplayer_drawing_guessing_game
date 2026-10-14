from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..schemas import CreateRoom, JoinRoom
from ..game import room_code

router = APIRouter(prefix="/api/rooms", tags=["rooms"])

@router.get("")
def list_rooms(status: str = Query("lobby", pattern="^(lobby|playing|completed)$"), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Discover rooms by lifecycle state without exposing any in-progress words."""
    rooms = db.query(models.GameRoom).filter_by(status=status).order_by(models.GameRoom.created_at.desc()).limit(limit).all()
    return [{"roomCode": room.room_code, "status": room.status, "currentRound": room.current_round, "totalRounds": room.total_rounds, "roundSeconds": room.round_seconds, "playerCount": db.query(models.Player).filter_by(room_id=room.id, left_at=None).count(), "createdAt": room.created_at} for room in rooms]

@router.post("")
def create_room(body: CreateRoom, db: Session = Depends(get_db)):
    code = room_code()
    while db.query(models.GameRoom).filter_by(room_code=code).first(): code = room_code()
    room = models.GameRoom(room_code=code, total_rounds=body.total_rounds, round_seconds=body.round_seconds)
    db.add(room); db.flush()
    host = models.Player(room_id=room.id, display_name=body.display_name.strip())
    db.add(host); db.flush(); room.admin_player_id = host.id; db.commit(); db.refresh(host)
    return {"roomCode": code, "playerId": host.id}

@router.post("/{code}/join")
def join_room(code: str, body: JoinRoom, db: Session = Depends(get_db)):
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    if not room or room.status != "lobby": raise HTTPException(404, "Room is unavailable once play has begun")
    player = models.Player(room_id=room.id, display_name=body.display_name.strip())
    db.add(player); db.commit(); db.refresh(player)
    return {"roomCode": room.room_code, "playerId": player.id}

@router.get("/{code}")
def room_info(code: str, db: Session = Depends(get_db)):
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    if not room: raise HTTPException(404, "Room not found")
    players = db.query(models.Player).filter_by(room_id=room.id).all()
    return {"roomCode": room.room_code, "status": room.status, "currentRound": room.current_round, "totalRounds": room.total_rounds, "roundSeconds": room.round_seconds, "adminPlayerId": room.admin_player_id, "players": [{"id": p.id, "name": p.display_name, "score": p.score} for p in players]}

@router.get("/{code}/players")
def room_players(code: str, active_only: bool = False, db: Session = Depends(get_db)):
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    if not room: raise HTTPException(404, "Room not found")
    query = db.query(models.Player).filter_by(room_id=room.id)
    if active_only: query = query.filter(models.Player.left_at.is_(None))
    players = query.order_by(models.Player.score.desc(), models.Player.joined_at).all()
    return [{"id": player.id, "displayName": player.display_name, "score": player.score, "isAdmin": player.id == room.admin_player_id, "joinedAt": player.joined_at, "leftAt": player.left_at} for player in players]

@router.get("/{code}/rounds")
def room_rounds(code: str, db: Session = Depends(get_db)):
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    if not room: raise HTTPException(404, "Room not found")
    rounds = db.query(models.GameRound).filter_by(room_id=room.id).order_by(models.GameRound.round_number).all()
    # The word is disclosed only after a round/game has finished.
    return [{"round": round_.round_number, "drawerPlayerId": round_.drawer_player_id, "word": round_.word if round_.ended_at else None, "startedAt": round_.started_at, "endedAt": round_.ended_at} for round_ in rounds]

@router.get("/{code}/summary")
def room_summary(code: str, db: Session = Depends(get_db)):
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    if not room: raise HTTPException(404, "Room not found")
    players = db.query(models.Player).filter_by(room_id=room.id).order_by(models.Player.score.desc()).all()
    rounds = db.query(models.GameRound).filter_by(room_id=room.id).order_by(models.GameRound.round_number).all()
    return {"roomCode": room.room_code, "status": room.status, "startedAt": room.started_at, "endedAt": room.ended_at, "settings": {"totalRounds": room.total_rounds, "roundSeconds": room.round_seconds}, "winner": {"id": players[0].id, "name": players[0].display_name, "score": players[0].score} if room.status == "completed" and players else None, "players": [{"id": player.id, "name": player.display_name, "score": player.score} for player in players], "roundsPlayed": len(rounds)}

@router.post("/{code}/players/{player_id}/leave")
def leave_room(code: str, player_id: int, db: Session = Depends(get_db)):
    """REST fallback for clients that cannot deliver the WebSocket leave event."""
    room = db.query(models.GameRoom).filter_by(room_code=code.upper()).first()
    player = db.get(models.Player, player_id)
    if not room or not player or player.room_id != room.id: raise HTTPException(404, "Player or room not found")
    player.left_at = datetime.utcnow(); db.commit()
    return {"ok": True, "playerId": player_id, "leftAt": player.left_at}
