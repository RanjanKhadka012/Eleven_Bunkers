# Eleven Bunkers

Eleven Bunkers is a multiplayer social survival game built with a React frontend and a small Express backend. Players join a lobby, receive hidden bunker-survival cards, reveal one category per round, debate, vote people out, and see whether the final survivor group can keep humanity alive.

## Current Stack

- Frontend: React 19 + Vite
- Backend: Express
- Optional AI/TTS: ElevenLabs for narration, Anthropic for endgame summaries
- Data storage: in-memory lobbies on the backend

## What The App Does Today

- Creates shareable 6-character lobby codes
- Supports 1-12 players
- Lets the host start a game and control round pacing
- Deals random cards across 8 reveal categories
- Runs a round loop of reveal -> discussion -> voting
- Auto-resolves eliminations once all active players vote
- Calculates final survival score against a catastrophe/bunker threshold
- Plays host narration through ElevenLabs when API keys are configured
- Falls back to built-in endgame narration if AI summary generation is unavailable

## Project Structure

```text
Eleven_Bunkers/
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- lib/
|   |   |-- scenarios/
|   |   `-- styles/
|   |-- package.json
|   `-- vite.config.js
|-- backend/
|   |-- api/
|   |-- package.json
|   |-- server.js
|   `-- .env.example
|-- package.json
`-- ReadMe.md
```

## Local Development

### Prerequisites

- Node.js 18+
- npm

### Install

```bash
npm install
```

### Configure the backend

Copy the backend env file:

```bash
copy backend\.env.example backend\.env
```

The frontend proxy expects the backend on port `5001` by default, so keep `PORT=5001` in `backend/.env` unless you also change `VITE_BACKEND_PORT`.

### Run the backend

```bash
npm run dev:backend
```

### Run the frontend

In a second terminal:

```bash
npm run dev:frontend
```

Then open `http://localhost:3000`.

## Environment Variables

Backend env lives in `backend/.env`.

Required for core local dev:

```env
PORT=5001
```

Optional backend integrations:

```env
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
CLAUDE_API_KEY=
CLAUDE_MODEL=claude-3-5-haiku-latest
ALLOWED_ORIGINS=*
```

Optional frontend env values:

```env
VITE_BACKEND_PORT=5001
VITE_LOBBY_ENDPOINT=
VITE_TTS_ENDPOINT=
VITE_ELEVENLABS_VOICE_ID=
```

Notes:

- `VITE_LOBBY_ENDPOINT` and `VITE_TTS_ENDPOINT` let the frontend point at a deployed backend instead of the local proxy.
- If ElevenLabs keys are missing, narration requests will fail instead of generating audio.
- If `CLAUDE_API_KEY` is missing, endgame summaries fall back to a deterministic local summary.

## Scripts

From the workspace root:

- `npm run dev:frontend` starts Vite
- `npm run build:frontend` builds the frontend
- `npm run preview:frontend` previews the frontend build
- `npm run dev:backend` starts the Express API

## API Overview

Local backend base URL: `http://localhost:5001`

- `POST /api/lobbies` creates a lobby
- `GET /api/lobbies/:code` fetches a lobby
- `PUT /api/lobbies/:code` updates lobby state
- `POST /api/tts` proxies ElevenLabs text-to-speech
- `POST /api/outcome-summary` generates or falls back to a final narration
- `GET /health` returns backend health

## Gameplay Rules In Code

- Every player starts with `profession` revealed
- Each round, active players reveal one additional category
- Discussion lasts 90 seconds by default
- The host can pause discussion, resume it, or skip directly to voting
- Voting resolves only when every active player has voted
- Survivor targets scale with player count
- Final threshold is based on survivors needed plus weighted catastrophe and bunker modifiers

Game data and scoring live primarily in `frontend/src/lib/gameData.js` and `frontend/src/lib/gameEngine.js`.

## Important Limitations

- Lobby state is stored in memory, so all lobbies are lost when the backend restarts
- There is no database-backed persistence or authentication yet
- The repo still contains older Django-related files (`requirements.txt`, `db.sqlite3`, some Python folders), but the current runnable app uses the Express backend in `backend/server.js`

## Build

```bash
npm run build:frontend
```

## Troubleshooting

- If the frontend cannot reach the backend locally, check that `backend/.env` uses `PORT=5001` or set `VITE_BACKEND_PORT` to match your backend port.
- If lobby creation works in production but not locally, make sure the frontend is using the local `/api` proxy instead of a remote `VITE_LOBBY_ENDPOINT`.
- If narration buttons fail, confirm `ELEVENLABS_API_KEY` is set in `backend/.env`.
- If outcome narration is shorter or more generic than expected, the app is probably using the local fallback because `CLAUDE_API_KEY` is missing or the request failed.
