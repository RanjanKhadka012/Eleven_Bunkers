# Bunker Game Backend - Complete Setup Guide

## Overview
The Bunker Game Backend is a Django REST API that manages the complete game logic for the Bunker social survival game. It handles player management, card dealing, scoring, voting, and text-to-speech integration with ElevenLabs.

## Backend Requirements

### 1. **Game Session Management**
- Create and manage game sessions
- Handle player joining/leaving
- Track game phases (Setup → Reveal → Voting → Final Scoring)
- Calculate thresholds based on catastrophe and bunker modifiers
- Determine survival outcome

### 2. **Player Management**
- Create player hands with 8 card assignments
- Track card reveals
- Manage player elimination
- Calculate individual and group scores

### 3. **Card System**
- **Card Types:** Profession, Skill, Biological, Health, Hobby, Phobia, Baggage, Additional Info
- **Special Condition Cards:** 2 per player (doesn't count toward scoring)
- **Point System:** Full scoring per rulebook (-8 to +12 points)
- **Random Assignment:** Cards randomly distributed to players

### 4. **Scoring System**
- Individual card scoring (all 8 card types)
- Group total calculation
- Threshold determination based on:
  - Base: `survivors_needed × 18`
  - Catastrophe modifier
  - Bunker modifier
- Win condition: `final_score >= final_threshold`

### 5. **Voting & Elimination**
- Multi-round voting system
- Vote tracking and aggregation
- Player elimination management
- Vote round history

### 6. **Text-to-Speech Integration**
- ElevenLabs API integration
- Card narration generation
- Player summary voice generation
- Game announcement narration
- Multiple voice options available

## Installation & Setup

### Prerequisites
- Python 3.13+
- pip
- Virtual environment (venv)

### Step 1: Navigate to backend directory
```bash
cd backend
```

### Step 2: Activate virtual environment
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create .env file
```bash
cp .env.example .env
```

Update `.env` with your ElevenLabs API key:
```
ELEVENLABS_API_KEY=your_api_key_here
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Step 5: Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Populate game data
```bash
python manage.py populate_bunker_data
```

### Step 7: Create superuser (optional)
```bash
python manage.py createsuperuser
```

### Step 8: Run development server
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Authentication
Most endpoints require authentication. Include JWT token in header:
```
Authorization: Bearer <token>
```

---

## Endpoint Reference

### Card Endpoints

#### Get All Cards
```
GET /api/cards/
Query params: 
  - card_type: profession|skill|biological|health|hobby|phobia|baggage|additional_info
  - page: page number
```

#### Get Card Types
```
GET /api/card-types/
```

---

### Scenario Endpoints

#### Get All Catastrophes
```
GET /api/catastrophes/
- Returns all catastrophe scenarios with point modifiers
```

#### Get All Bunkers
```
GET /api/bunkers/
- Returns all bunker conditions (positive and negative)
```

#### Get Positive Bunkers
```
GET /api/bunkers/positive/
```

#### Get Negative Bunkers
```
GET /api/bunkers/negative/
```

#### Get Special Conditions
```
GET /api/special-conditions/
```

---

### Game Session Endpoints

#### Create Game
```
POST /api/games/
Body:
{
  "game_id": "game_12345",
  "max_players": 8,
  "catastrophe_id": 1,
  "bunker_id": 2
}
Returns: GameSession object
```

#### Get All Games (user's games)
```
GET /api/games/
- Returns games created by or joined by current user
```

#### Get Game Details
```
GET /api/games/{id}/
- Includes all players, their cards, vote history, and logs
```

#### Join Game
```
POST /api/games/{id}/join_game/
- Adds current user to game
- Returns: PlayerHand object
```

#### Start Game
```
POST /api/games/{id}/start_game/
- Only creator can start
- Deals cards to all players
- Changes phase to 'reveal'
```

#### Game Status
```
GET /api/games/{id}/game_status/
Returns: Current game state with player counts, phase, threshold, and scenario info
```

#### Reveal Card
```
POST /api/games/{id}/reveal_card/
Body:
{
  "card_type": "profession"  // or skill, biological, health, hobby, phobia, baggage, additional_info
}
- Marks card as revealed
- Updates game log
```

#### Cast Vote
```
POST /api/games/{id}/cast_vote/
Body:
{
  "voted_for_id": 5  // PlayerHand ID to eliminate
}
- Records vote in current round
- Returns: VoteRound object with all votes
```

#### Eliminate Player
```
POST /api/games/{id}/eliminate_player/
Body:
{
  "player_id": 5,
  "round_number": 1
}
- Marks player as eliminated
- Updates game log
```

#### Final Scoring
```
POST /api/games/{id}/final_scoring/
- Only creator can finalize
- Calculates all player scores
- Determines if humanity survives
- Changes phase to 'final_scoring'
- Returns: Complete game result
```

---

### Text-to-Speech Endpoints

#### Generate Card Narration
```
POST /api/text-to-speech/card_narration/
Body:
{
  "card_id": 1,
  "voice_id": "21m00Tcm4TlvDq8ikWAM"  // Optional, defaults to Rachel
}
Returns: {narration, audio}
```

#### Generate Player Summary
```
POST /api/text-to-speech/player_summary/
Body:
{
  "player_hand_id": 10,
  "voice_id": "21m00Tcm4TlvDq8ikWAM"
}
Returns: {narration, audio}
```

#### Generate Game Announcement
```
POST /api/text-to-speech/game_announcement/
Body:
{
  "game_session_id": 5,
  "voice_id": "21m00Tcm4TlvDq8ikWAM"
}
Returns: {announcement, audio}
```

---

## Data Models

### GameSession
```python
{
  "id": 1,
  "game_id": "game_12345",
  "created_by": UserObject,
  "catastrophe": CatastropheObject,
  "bunker": BunkerObject,
  "current_phase": "reveal",  # setup, reveal, voting, final_scoring, completed
  "status": "active",  # active, completed, failed
  "base_threshold": 72,
  "final_threshold": 85,
  "final_score": 90,
  "max_players": 8,
  "survivors_needed": 4,
  "players": [PlayerHandObject, ...],
  "vote_rounds": [VoteRoundObject, ...],
  "logs": [GameLogObject, ...]
}
```

### PlayerHand
```python
{
  "id": 5,
  "player": UserObject,
  "game_session": 1,
  "profession": CardObject,
  "skill": CardObject,
  "biological": CardObject,
  "health": CardObject,
  "hobby": CardObject,
  "phobia": CardObject,
  "baggage": CardObject,
  "additional_info": CardObject,
  "profession_revealed": true,
  "skill_revealed": false,
  # ... other reveals
  "is_eliminated": false,
  "eliminated_round": null,
  "total_score": 28,
  "special_cards": [PlayerSpecialCardObject, ...],
  "joined_at": "2024-03-28T10:00:00Z"
}
```

### Card
```python
{
  "id": 1,
  "card_type": 1,  # CardType ID
  "card_type_display": "Profession",
  "name": "Emergency Doctor",
  "description": "...",
  "points": 12
}
```

---

## Game Flow Example

### 1. Create Game
```bash
POST /api/games/
{
  "game_id": "bunker_game_001",
  "max_players": 6,
  "catastrophe_id": 1,  # Nuclear War
  "bunker_id": 2  # Medical Facility
}
```
- Calculates `survivors_needed = 4`
- Calculates `final_threshold = 4 * 18 + 10 + (-4) = 78`

### 2. Players Join
```bash
POST /api/games/1/join_game/  # Called by each player
```

### 3. Start Game
```bash
POST /api/games/1/start_game/  # Called by game creator
```
- Cards randomly distributed to each player

### 4. Reveal Rounds
For each card type in order (profession, skill, biological, health, hobby, phobia, baggage, additional_info):
```bash
POST /api/games/1/reveal_card/
{
  "card_type": "profession"
}
```
- Players discuss and argue value
- Use special condition cards

### 5. Voting Rounds
Eliminate players one at a time:
```bash
POST /api/games/1/cast_vote/
{
  "voted_for_id": 5
}
```

```bash
POST /api/games/1/eliminate_player/
{
  "player_id": 5,
  "round_number": 1
}
```

### 6. Final Scoring
```bash
POST /api/games/1/final_scoring/
```
- Player 1: 28 points
- Player 2: 25 points
- Player 4: 30 points
- Player 6: 18 points
- **Total: 101 points >= 78 threshold**
- **Result: Humanity survived!**

---

## Environment Variables

```env
ELEVENLABS_API_KEY=your_api_key_here
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

---

## Database

### SQLite (Development)
Default database: `backend/db.sqlite3`

### Admin Panel
Access at: `http://localhost:8000/admin/`
- Login with superuser credentials
- Manage all game data
- Review player hands, votes, and game logs

---

## Text-to-Speech Voices

Popular voices available from ElevenLabs:
- `21m00Tcm4TlvDq8ikWAM` - Rachel (Default)
- `EXAVITQu4vr4xnSDxMaL` - Bella
- `g0FPU06Z59oA7G7GstNS` - Callum
- `pFZP5JQG7iQjIQuC4Iy3` - Charlie
- And many more available via API

---

## Common Issues

### 1. ElevenLabs API Key Error
**Solution:** Make sure `.env` file has correct API key and reload server

### 2. Database Not Populating
**Solution:** Run `python manage.py populate_bunker_data` after migrations

### 3. CORS Issues with Frontend
**Solution:** Update `CORS_ALLOWED_ORIGINS` in `settings.py`

### 4. Vote Casting Errors
**Solution:** Ensure player hasn't already voted for themselves

---

## Development Commands

### Start Development Server
```bash
python manage.py runserver
```

### Create Admin User
```bash
python manage.py createsuperuser
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Populate Game Data
```bash
python manage.py populate_bunker_data
```

### Access Admin Panel
```
http://localhost:8000/admin/
```

---

## Next Steps

1. **Frontend Integration:** Connect React frontend to these API endpoints
2. **WebSocket Support:** Add real-time game updates using Django Channels
3. **Authentication:** Implement JWT token generation endpoint
4. **Game Timers:** Add phase timing and auto-phase transitions
5. **Spectator Mode:** Allow users to watch games as spectators
6. **Game Statistics:** Track player stats across games
7. **Leaderboards:** Implement player rankings

---

## Notes

- All timestamps are in UTC
- Scores can be negative
- Players can't eliminate themselves
- Cards are randomly selected (no duplicates per game)
- Once a card is revealed, all players see it
- Special condition cards provide strategic depth but don't affect final score

