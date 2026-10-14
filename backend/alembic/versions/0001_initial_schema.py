"""initial game persistence schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("game_rooms", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("room_code", sa.String(8), nullable=False), sa.Column("admin_player_id", sa.Integer()), sa.Column("status", sa.String(20), nullable=False), sa.Column("current_round", sa.Integer(), nullable=False), sa.Column("total_rounds", sa.Integer(), nullable=False), sa.Column("round_seconds", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("started_at", sa.DateTime()), sa.Column("ended_at", sa.DateTime()))
    op.create_index("ix_game_rooms_room_code", "game_rooms", ["room_code"], unique=True)
    op.create_table("players", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("room_id", sa.Integer(), sa.ForeignKey("game_rooms.id"), nullable=False), sa.Column("display_name", sa.String(40), nullable=False), sa.Column("score", sa.Integer(), nullable=False), sa.Column("joined_at", sa.DateTime(), nullable=False), sa.Column("left_at", sa.DateTime()))
    op.create_index("ix_players_room_id", "players", ["room_id"])
    op.create_table("game_rounds", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("room_id", sa.Integer(), sa.ForeignKey("game_rooms.id"), nullable=False), sa.Column("round_number", sa.Integer(), nullable=False), sa.Column("drawer_player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False), sa.Column("word", sa.String(80), nullable=False), sa.Column("started_at", sa.DateTime(), nullable=False), sa.Column("ended_at", sa.DateTime()))
    op.create_index("ix_game_rounds_room_id", "game_rounds", ["room_id"])
    op.create_table("guesses", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("round_id", sa.Integer(), sa.ForeignKey("game_rounds.id"), nullable=False), sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False), sa.Column("guess_text", sa.Text(), nullable=False), sa.Column("is_correct", sa.Boolean(), nullable=False), sa.Column("submitted_at", sa.DateTime(), nullable=False))
    op.create_index("ix_guesses_round_id", "guesses", ["round_id"])


def downgrade() -> None:
    op.drop_table("guesses"); op.drop_table("game_rounds"); op.drop_table("players"); op.drop_table("game_rooms")
