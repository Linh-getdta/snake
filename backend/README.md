# Snake Online Backend

## Install

From the repository root:

```powershell
python -m pip install -r requirements.txt
```

## Run

Start the server from the repository root:

```powershell
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

Start the Pygame client in another terminal:

```powershell
python -m client.main
```

Choose **2 - Choi online**, enter the server URL and a room code, then share
both values with one opponent. The first player opens the room and the second
player joins it. Use `ws://127.0.0.1:8000` for a server on the same computer.
For another computer, use the server computer's reachable LAN or public
address and allow inbound TCP port 8000 in its firewall.

The server controls movement and collisions and stores online scores in
`backend/snake.db`. The leaderboard endpoint is
`http://127.0.0.1:8000/leaderboard`; `/` is the health endpoint.
