import json
import os
import queue
import secrets
import string
import threading
from urllib.parse import quote, urlsplit

import pygame
import websocket


WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 220, 80)
BLUE = (40, 160, 255)
RED = (255, 60, 60)
GRAY = (160, 160, 160)


def _draw_centered(screen, font, text, y, color=WHITE):
    surface = font.render(text, True, color)
    screen.blit(surface, (WIDTH // 2 - surface.get_width() // 2, y))


def prompt_online_settings(screen):
    font = pygame.font.SysFont("comicsansms", 25)
    small_font = pygame.font.SysFont("comicsansms", 19)
    fields = [
        os.environ.get("SNAKE_SERVER_URL", "ws://127.0.0.1:8000"),
        "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
    ]
    active = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return None
            if event.key == pygame.K_TAB:
                active = 1 - active
            elif event.key == pygame.K_RETURN:
                if active == 0:
                    active = 1
                else:
                    url = fields[0].strip().rstrip("/")
                    room_code = fields[1].strip().upper()
                    parsed_url = urlsplit(url)
                    if parsed_url.scheme in ("http", "https"):
                        scheme = "ws" if parsed_url.scheme == "http" else "wss"
                        url = f"{scheme}://{parsed_url.netloc}{parsed_url.path}".rstrip("/")
                    parsed_url = urlsplit(url)
                    if (
                        parsed_url.scheme not in ("ws", "wss")
                        or not parsed_url.netloc
                        or not 1 <= len(room_code) <= 16
                        or not room_code.isalnum()
                    ):
                        continue
                    return url, room_code
            elif event.key == pygame.K_BACKSPACE:
                fields[active] = fields[active][:-1]
            elif event.unicode.isprintable():
                maximum = 200 if active == 0 else 16
                if len(fields[active]) < maximum:
                    fields[active] += event.unicode

        screen.fill(BLACK)
        _draw_centered(screen, font, "SNAKE ONLINE", 100, GREEN)
        _draw_centered(screen, small_font, "Server URL", 200, GRAY)
        server_box = pygame.Rect(120, 230, 560, 48)
        pygame.draw.rect(screen, GREEN if active == 0 else WHITE, server_box, 2)
        screen.blit(font.render(fields[0], True, WHITE), (server_box.x + 10, server_box.y + 5))

        _draw_centered(screen, small_font, "Room code (share this with your opponent)", 305, GRAY)
        room_box = pygame.Rect(250, 335, 300, 48)
        pygame.draw.rect(screen, GREEN if active == 1 else WHITE, room_box, 2)
        screen.blit(font.render(fields[1], True, WHITE), (room_box.x + 10, room_box.y + 5))

        _draw_centered(screen, small_font, "TAB: switch field   ENTER: connect   ESC: back", 430, GRAY)
        _draw_centered(screen, small_font, "The first player creates the room; the second joins it.", 465, GRAY)
        pygame.display.flip()
        clock.tick(30)


def _receive_messages(connection, messages):
    try:
        while True:
            messages.put(json.loads(connection.recv()))
    except websocket.WebSocketConnectionClosedException:
        messages.put({"type": "error", "message": "Disconnected from server"})
    except Exception as exc:
        messages.put({"type": "error", "message": f"Connection error: {exc}"})


def _draw_game(screen, font, small_font, state, player_id, room_code):
    screen.fill(BLACK)
    _draw_centered(screen, font, f"ONLINE - ROOM {room_code}", 8, GREEN)

    if state is None:
        _draw_centered(screen, font, "Connecting to room...", HEIGHT // 2)
    else:
        players = state.get("players", [])
        if not state.get("started"):
            _draw_centered(screen, font, "Waiting for second player...", HEIGHT // 2, WHITE)
        else:
            for player in players:
                color = GREEN if player.get("id") == player_id else BLUE
                for x, y in player.get("body", []):
                    pygame.draw.rect(screen, color, (x, y, 20, 20))
            food = state.get("food")
            if food:
                pygame.draw.rect(screen, RED, (food[0], food[1], 20, 20))
            scores = "   ".join(
                f"{player.get('name', 'Player')}: {player.get('score', 0)}"
                for player in players
            )
            _draw_centered(screen, small_font, scores, 42, WHITE)

        message = state.get("message", "")
        if message:
            _draw_centered(screen, font, message, HEIGHT // 2 + 25, WHITE)
        if state.get("finished"):
            _draw_centered(screen, small_font, "Press ENTER or ESC to return to menu", HEIGHT - 45, GRAY)

    pygame.display.flip()


def run_online_game(screen, player_name, server_url, room_code):
    font = pygame.font.SysFont("comicsansms", 30)
    small_font = pygame.font.SysFont("comicsansms", 22)
    url = (
        f"{server_url.rstrip('/')}/ws/{quote(room_code, safe='')}"
        f"/{quote(player_name, safe='')}"
    )
    try:
        connection = websocket.create_connection(url, timeout=5)
        connection.settimeout(None)
    except (OSError, websocket.WebSocketException) as exc:
        screen.fill(BLACK)
        _draw_centered(screen, font, "Could not connect to server", 220, RED)
        _draw_centered(screen, small_font, str(exc)[:80], 275, WHITE)
        _draw_centered(screen, small_font, "Press any key to return", 340, GRAY)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    waiting = False
            pygame.time.wait(25)
        return

    messages = queue.Queue()
    receiver = threading.Thread(
        target=_receive_messages, args=(connection, messages), daemon=True
    )
    receiver.start()

    player_id = None
    state = None
    running = True
    game_over = False
    clock = pygame.time.Clock()
    directions = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
    }

    try:
        while running:
            while not messages.empty():
                message = messages.get_nowait()
                if message.get("type") == "welcome":
                    player_id = message.get("id")
                elif message.get("type") == "state":
                    state = message
                    game_over = bool(state.get("finished"))
                elif message.get("type") == "error":
                    state = {
                        "started": False,
                        "finished": True,
                        "message": message.get("message", "Server error"),
                        "players": [],
                    }
                    game_over = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if game_over and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in directions and not game_over:
                        try:
                            connection.send(json.dumps({"direction": directions[event.key]}))
                        except websocket.WebSocketException:
                            running = False

            _draw_game(screen, font, small_font, state, player_id, room_code)
            clock.tick(30)
    finally:
        connection.close()
