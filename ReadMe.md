# 🎮 Bunker - Social Survival Game

A React + Vite frontend with an Express backend proxy for ElevenLabs text-to-speech and lightweight lobby syncing.

## 🏗️ Project Structure

```
Eleven_Bunkers/
├── backend/                  # Express backend (TTS proxy + in-memory lobbies)
│   ├── server.js             # Express app
│   ├── api/tts.js            # ElevenLabs proxy
│   └── package.json
├── frontend/                 # React (Vite) app
│   ├── src/
│   │   ├── components/       # Screens (Home, Lobby, Game, Host)
│   │   ├── lib/              # game engine, tts client, lobby client
│   │   └── styles/
│   └── package.json
└── railway.json              # Railway service config (backend)
```

## 🚀 Quick Start (local)

Backend
```bash
cd backend
npm install
ELEVENLABS_API_KEY=your_key ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM PORT=5000 npm start
```

Frontend
```bash
cd frontend
npm install
# For local proxy to backend on 5000
VITE_BACKEND_PORT=5000 npm run dev
```

## 🌐 Deployment

Backend (Railway)
- Path: `backend`
- Install: `npm install`
- Start: `npm run start`
- Env: `PORT=${PORT}`, `ELEVENLABS_API_KEY`, optional `ELEVENLABS_VOICE_ID`, optional `CORS_ORIGINS`.

Frontend (Vercel)
- Root: `frontend`
- Build: `npm run build`
- Install: `npm install`
- Output: `dist`
- Env: `VITE_TTS_ENDPOINT=https://<your-backend>/api/tts`, `VITE_LOBBY_ENDPOINT=https://<your-backend>/api/lobbies`, `VITE_ELEVENLABS_VOICE_ID=<voice>`.

## 🔐 Environment Variables

Backend (.env or Railway vars)
- `ELEVENLABS_API_KEY` (required)
- `ELEVENLABS_VOICE_ID` (optional, default 21m00Tcm4TlvDq8ikWAM)
- `PORT` (use platform-provided)
- `CORS_ORIGINS` (optional allowlist; defaults to all)

Frontend (Vercel vars)
- `VITE_TTS_ENDPOINT` full URL to backend `/api/tts`
- `VITE_LOBBY_ENDPOINT` full URL to backend `/api/lobbies`
- `VITE_ELEVENLABS_VOICE_ID` default voice id
- `VITE_BACKEND_PORT` (local dev only, for proxy)

## 📡 Backend Routes
- `POST /api/tts` – ElevenLabs TTS proxy (returns audio/mpeg)
- `POST /api/lobbies` – create lobby (in-memory)
- `GET /api/lobbies/:code` – fetch lobby
- `PUT /api/lobbies/:code` – update lobby
- `GET /health` – health check

## 🎯 Current Features
- Host/join lobbies (now shared via backend API instead of localStorage)
- Card reveal, discussion timer pause/resume/skip (host controls)
- Voting and elimination flow with in-memory lobby state
- ElevenLabs narration (opening/outcome/elimination) via backend proxy

## ⚠️ Notes
- Lobbies are in-memory on the backend; they reset on restart/redeploy. Add a database if persistence is needed.
- Set the backend env `ELEVENLABS_API_KEY`—frontend should never include the key.

## 📞 Support
- Issues: open a GitHub issue in this repo.

**Enjoy the game!**
