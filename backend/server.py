"""Authoritative multiplayer Snake server.

Run from the repository root with:
    python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000
"""

import asyncio
import logging
import random
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from backend.database import (
    creat_player_table,
    creat_result_table,
    get_leaderboard,
    save_game,
)

logger = logging.getLogger(__name__)

WIDTH, HEIGHT, CELL_SIZE = 800, 600, 20
TICK_SECONDS = 0.12
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
rooms = {}
rooms_lock = asyncio.Lock()


def initialize_database():
    creat_player_table()
    creat_result_table()


def _leaderboard(limit):
    return [
        {"name": name, "score": score}
        for name, score in get_leaderboard(limit)
    ]


@asynccontextmanager
async def lifespan(_app):
    await asyncio.to_thread(initialize_database)
    yield
    tasks = [room.task for room in rooms.values() if room.task is not None]
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(title="Snake Online", lifespan=lifespan)


class Room:
    def __init__(self, code):
        self.code = code
        self.players = {}
        self.food = None
        self.started = False
        self.finished = False
        self.task = None
        self.lock = asyncio.Lock()
        self.final_scores = None

    def spawn_food(self):
        occupied = {
            tuple(segment)
            for player in self.players.values()
            for segment in player["body"]
        }
        available = [
            [x, y]
            for x in range(0, WIDTH, CELL_SIZE)
            for y in range(0, HEIGHT, CELL_SIZE)
            if (x, y) not in occupied
        ]
        self.food = random.choice(available) if available else None

    def snapshot(self, message=""):
        return {
            "type": "state",
            "room": self.code,
            "started": self.started,
            "finished": self.finished,
            "message": message,
            "food": self.food,
            "players": [
                {
                    "id": player_id,
                    "name": player["name"],
                    "body": player["body"],
                    "score": player["score"],
                    "alive": player["alive"],
                }
                for player_id, player in self.players.items()
            ],
        }

    async def broadcast(self, data):
        for player in list(self.players.values()):
            try:
                await player["ws"].send_json(data)
            except (OSError, RuntimeError, WebSocketDisconnect):
                continue

    def tick(self):
        next_heads = {}
        eating = {}
        for player_id, player in self.players.items():
            if not player["alive"]:
                continue
            player["direction"] = player["pending"]
            dx, dy = DIRECTIONS[player["direction"]]
            head_x, head_y = player["body"][0]
            next_heads[player_id] = [
                head_x + dx * CELL_SIZE,
                head_y + dy * CELL_SIZE,
            ]
            eating[player_id] = next_heads[player_id] == self.food

        dead = set()
        for player_id, head in next_heads.items():
            x, y = head
            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                dead.add(player_id)
                continue

            for other_id, other in self.players.items():
                body = other["body"]
                occupied = body if eating.get(other_id, False) or not other["alive"] else body[:-1]
                if head in occupied:
                    dead.add(player_id)

        for player_id, head in next_heads.items():
            if any(
                other_id != player_id and other_head == head
                for other_id, other_head in next_heads.items()
            ):
                dead.add(player_id)

        player_ids = list(next_heads)
        if len(player_ids) == 2:
            first_id, second_id = player_ids
            first_head = next_heads[first_id]
            second_head = next_heads[second_id]
            if (
                first_head == self.players[second_id]["body"][0]
                and second_head == self.players[first_id]["body"][0]
            ):
                dead.update(player_ids)

        ate_food = False
        for player_id, head in next_heads.items():
            player = self.players[player_id]
            if player_id in dead:
                player["alive"] = False
                continue
            player["body"].insert(0, head)
            if eating[player_id]:
                player["score"] += 10
                ate_food = True
            else:
                player["body"].pop()

        if ate_food:
            self.spawn_food()
        if self.food is None or not any(player["alive"] for player in self.players.values()):
            self.finished = True
        if self.finished:
            self.final_scores = [
                (player["name"], player["score"])
                for player in self.players.values()
            ]

    async def persist_results(self):
        scores = self.final_scores
        if scores is None:
            scores = [
                (player["name"], player["score"])
                for player in list(self.players.values())
            ]
        for player_name, score in scores:
            try:
                await asyncio.to_thread(save_game, player_name, score)
            except Exception:
                logger.exception("Could not save result for %s", player_name)
                await self.broadcast(
                    {"type": "error", "message": "Could not save match results"}
                )

    async def game_loop(self):
        while not self.finished:
            await asyncio.sleep(TICK_SECONDS)
            async with self.lock:
                self.tick()
                state = self.snapshot("Game over" if self.finished else "")
            await self.broadcast(state)

        await self.persist_results()
        await self.broadcast(self.snapshot("Game over"))


@app.get("/")
async def health():
    return {"status": "ok", "service": "Snake Online"}


@app.get("/leaderboard")
async def leaderboard(limit: int = 10):
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 100")
    try:
        return await asyncio.to_thread(_leaderboard, limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@app.websocket("/ws/{room_code}/{player_name}")
async def websocket_game(websocket: WebSocket, room_code: str, player_name: str):
    room_code = room_code.strip().upper()
    player_name = player_name.strip()
    if (
        not 1 <= len(room_code) <= 16
        or not room_code.isalnum()
        or not 1 <= len(player_name) <= 20
    ):
        await websocket.close(code=1008, reason="Invalid room or player name")
        return

    await websocket.accept()
    async with rooms_lock:
        room = rooms.setdefault(room_code, Room(room_code))

    player_id = str(uuid.uuid4())
    async with room.lock:
        if (
            room.started
            or room.finished
            or len(room.players) >= 2
            or any(
                player["name"].casefold() == player_name.casefold()
                for player in room.players.values()
            )
        ):
            await websocket.send_json(
                {"type": "error", "message": "Room is full, started, or name is in use"}
            )
            await websocket.close(code=1008, reason="Room unavailable")
            return

        index = len(room.players)
        if index == 0:
            body, direction = [[100, 100], [80, 100], [60, 100]], "RIGHT"
        else:
            body, direction = [[700, 500], [720, 500], [740, 500]], "LEFT"
        room.players[player_id] = {
            "ws": websocket,
            "name": player_name,
            "body": body,
            "direction": direction,
            "pending": direction,
            "score": 0,
            "alive": True,
        }
        await websocket.send_json(
            {"type": "welcome", "id": player_id, "room": room_code}
        )
        if len(room.players) == 2:
            room.started = True
            room.spawn_food()
            room.task = asyncio.create_task(room.game_loop())
        state = room.snapshot(
            "Waiting for second player" if not room.started else "Match started"
        )
    await room.broadcast(state)

    try:
        while True:
            try:
                message = await websocket.receive_json()
            except ValueError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid message"}
                )
                continue
            direction = message.get("direction") if isinstance(message, dict) else None
            if direction not in DIRECTIONS:
                continue
            async with room.lock:
                player = room.players.get(player_id)
                if (
                    player is not None
                    and player["alive"]
                    and not room.finished
                    and direction != OPPOSITE[player["direction"]]
                ):
                    player["pending"] = direction
    except WebSocketDisconnect:
        pass
    finally:
        async with room.lock:
            should_persist = room.started and not room.finished
            if should_persist:
                room.finished = True
                room.final_scores = [
                    (player["name"], player["score"])
                    for player in room.players.values()
                ]
                if room.task is not None:
                    room.task.cancel()
                await room.broadcast(room.snapshot("A player disconnected"))
            room.players.pop(player_id, None)

        if should_persist:
            await room.persist_results()
        if not room.players:
            async with rooms_lock:
                if rooms.get(room_code) is room:
                    rooms.pop(room_code, None)
