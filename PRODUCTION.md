# Production Deployment Guide

To move this system from a local prototype to a real-world tool used by remote teams, you need to handle three main areas: **Global Discovery**, **Firewall Traversal**, and **Security**.

## 1. Global Signaling Server
The `signaling_server.py` must be accessible from the public internet.

- **Option A (Self-Hosted):** Deploy to a VPS (DigitalOcean, AWS EC2, Linode).
  - Open port `8888`.
  - Use a process manager like `pm2` or `systemd` to keep it running.
  - **Important:** Change `signaling_url` in `src/network.py` from `localhost` to your server's public IP or Domain.
- **Option B (Managed):** Use a service like **Heroku** or **Render** that supports WebSockets.

## 2. Firewall & NAT Traversal (STUN/TURN)
In the real world, many corporate networks or home routers block direct P2P connections. You need "traversal" servers.

- **STUN Servers:** These help peers find their public IP. You can use free ones from Google:
  - `stun:stun.l.google.com:19302`
- **TURN Servers:** If P2P is blocked, a TURN server "relays" the data. 
  - **Action:** Install and host **Coturn** on your VPS, or use a managed service like **Twilio Network Traversal** or **OpenRelay**.
  - **Implementation:** Update `RTCPeerConnection` in `src/network.py` to include these server configurations.

## 3. Security (Essential for Production)
- **WSS (Secure WebSockets):** Encrypt the signaling traffic. Use a reverse proxy like **Nginx** with Let's Encrypt SSL certificates.
- **Room Authentication:** Add a password/token requirement to `signaling_server.py` so strangers cannot guess a Room ID and join your team.
- **Encryption:** WebRTC traffic is encrypted by default (DTLS/SRTP), but the signaling channel must also be secured to prevent "Man-in-the-Middle" attacks.

## 4. Performance Optimization
- **Hardware Encoding:** For the lowest latency, modify `src/streaming.py` to use hardware-accelerated encoders (NVENC for NVIDIA, VideoToolbox for Mac) instead of raw software frames.
- **Regional Servers:** If your team is global, host signaling servers in multiple regions (e.g., US-East, EU-West) to minimize the initial connection delay.

---

### Immediate Next Step for Testing:
If you want to test with a friend *right now* without a server:
1. Use **ngrok** to tunnel your local signaling server:
   ```bash
   ngrok http 8888
   ```
2. Give your friend the `wss://...` address provided by ngrok.
