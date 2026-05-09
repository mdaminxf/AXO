import socket
import threading
import json
import time

class LocalDiscovery:
    def __init__(self, room_id, port=9999):
        self.room_id = room_id
        self.port = port
        self.running = False
        self.peers = set() # Set of (ip, port)
        self.on_peer_found = None

    def start(self):
        self.running = True
        # Thread for broadcasting our presence
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        # Thread for listening to other broadcasts
        threading.Thread(target=self._listen_for_peers, daemon=True).start()

    def _broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        msg = json.dumps({"type": "axo_discovery", "room_id": self.room_id}).encode()
        
        while self.running:
            try:
                sock.sendto(msg, ('<broadcast>', self.port))
            except Exception as e:
                print(f"Broadcast error: {e}")
            time.sleep(2) # Broadcast every 2 seconds

    def _listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.port))
        sock.settimeout(1)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                payload = json.loads(data.decode())
                
                if payload.get("type") == "axo_discovery" and payload.get("room_id") == self.room_id:
                    # Ignore our own IP
                    if addr[0] not in [socket.gethostbyname(socket.gethostname())]:
                        if addr[0] not in self.peers:
                            self.peers.add(addr[0])
                            if self.on_peer_found:
                                self.on_peer_found(addr[0])
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")
