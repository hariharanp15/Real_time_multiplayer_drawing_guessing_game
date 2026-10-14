from datetime import datetime
from pydantic import BaseModel, Field


class CreateRoom(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)
    total_rounds: int = Field(default=3, ge=1, le=10)
    round_seconds: int = Field(default=75, ge=20, le=180)


class JoinRoom(BaseModel):
    display_name: str = Field(min_length=1, max_length=40)


class RoomOut(BaseModel):
    room_code: str
    status: str
    current_round: int
    total_rounds: int
    created_at: datetime


class PlayerOut(BaseModel):
    id: int
    display_name: str
    score: int
    joined_at: datetime
    left_at: datetime | None


class PlayerStats(BaseModel):
    player_id: int
    display_name: str
    score: int
    correct_guesses: int
