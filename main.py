from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AXO Signaling Server")

# room_id -> [list of websockets]
ROOMS: dict[str, list[WebSocket]] = {}

@app.get("/")
async def root():
    return {"status": "AXO Signaling Active", "rooms": list(ROOMS.keys())}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    if room_id not in ROOMS:
        ROOMS[room_id] = []
    ROOMS[room_id].append(websocket)
    logging.info(f"Peer joined AXO room: {room_id}")
    
    # Notify others that a peer joined
    for client in ROOMS[room_id]:
        if client != websocket:
            try:
                await client.send_json({"type": "peer_joined"})
            except:
                pass

    try:
        while True:
            data = await websocket.receive_json()
            # Relay signals (offer, answer, ice)
            for client in ROOMS[room_id]:
                if client != websocket:
                    try:
                        await client.send_json(data)
                    except:
                        continue
    except WebSocketDisconnect:
        ROOMS[room_id].remove(websocket)
        logging.info(f"Peer left AXO room: {room_id}")
