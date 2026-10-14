from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..database import SessionLocal
from .. import models
from ..game import manager

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/rooms/{code}/{player_id}")
async def game_socket(ws: WebSocket, code: str, player_id: int):
    code = code.upper(); db = SessionLocal()
    player = db.get(models.Player, player_id)
    room = db.query(models.GameRoom).filter_by(room_code=code).first()
    if not player or not room or player.room_id != room.id:
        await ws.close(code=4404); db.close(); return
    # The URL contains the durable player id, allowing a browser refresh to rejoin.
    player.left_at = None; db.commit()
    await manager.connect(code, player_id, ws)
    await manager.broadcast_lobby(db, code)
    try:
        while True:
            message = await ws.receive_json(); event, data = message.get("event"), message.get("data", {})
            if event == "ready":
                manager.ready.setdefault(code, set()).symmetric_difference_update({player_id}); await manager.broadcast_lobby(db, code)
            elif event == "start_game":
                error = await manager.start_game(db, code, player_id)
                if error: await manager.send(code, "error", {"message": error}, player_id)
            elif event == "end_game":
                if room.admin_player_id != player_id:
                    await manager.send(code, "error", {"message": "Only the room admin can end the game"}, player_id)
                else:
                    await manager.complete_game(db, code, "ended_by_admin")
            elif event == "stroke" and manager.active_round.get(code) and manager.active_round[code].drawer_player_id == player_id:
                stroke = {**data, "senderId": player_id}
                manager.canvas.setdefault(code, []).append(stroke)
                await manager.send(code, "stroke", stroke)
            elif event == "canvas_clear" and manager.active_round.get(code) and manager.active_round[code].drawer_player_id == player_id:
                manager.canvas[code] = []
                await manager.send(code, "canvas_clear", {})
            elif event == "guess": await manager.guess(db, code, player_id, str(data.get("text", "")))
            elif event == "leave": break
    except WebSocketDisconnect: pass
    finally:
        # Ignore a stale socket closing after this player already reconnected.
        if not manager.disconnect(code, player_id, ws):
            db.close()
            return
        player.left_at = datetime.utcnow(); db.commit()
        await manager.send(code, "player_left", {"playerId": player_id})
        active = manager.active_round.get(code)
        if active and active.drawer_player_id == player_id: await manager.end_round(db, code, "drawer_disconnected")
        await manager.broadcast_lobby(db, code); db.close()
