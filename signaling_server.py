import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)

# room_id -> [list of clients]
ROOMS = {}

async def handler(websocket, path):
    room_id = None
    client_id = str(id(websocket))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "join":
                room_id = data.get("room_id")
                if room_id not in ROOMS:
                    ROOMS[room_id] = []
                ROOMS[room_id].append(websocket)
                logging.info(f"Client {client_id} joined room: {room_id}")
                
                # Notify others in the room
                notification = json.dumps({"type": "peer_joined", "peer_id": client_id})
                for client in ROOMS[room_id]:
                    if client != websocket:
                        await client.send(notification)
            
            elif msg_type in ["offer", "answer", "ice"]:
                # Relay to others in the same room
                target_room = ROOMS.get(room_id, [])
                payload = json.dumps(data)
                for client in target_room:
                    if client != websocket:
                        await client.send(payload)
                        
    finally:
        if room_id in ROOMS and websocket in ROOMS[room_id]:
            ROOMS[room_id].remove(websocket)
            logging.info(f"Client {client_id} left room: {room_id}")

async def main():
    print("[*] Signaling Server starting on ws://localhost:8888")
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
