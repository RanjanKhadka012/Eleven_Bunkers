# 🏚️ AI-Driven Survival Game — Django Backend

A cooperative survival game backend built with **Django REST Framework**.  
Players join, receive hidden character cards, discuss and vote across rounds,  
and the group must assemble the best bunker team to beat the scenario threshold.

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [Quick Start](#quick-start)
3. [Architecture Overview](#architecture-overview)
4. [Game Flow](#game-flow)
5. [API Reference](#api-reference)
6. [Scenarios](#scenarios)
7. [Adding Custom Scenarios](#adding-custom-scenarios)
8. [Code Examples](#code-examples)

---

## Project Structure

```
survival_game/
├── manage.py
├── requirements.txt
│
├── survival_game/              # Django project package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── scenarios/                  # Scenario definitions (pure data, no Django deps)
│   ├── __init__.py
│   └── data.py                 ← ADD YOUR SCENARIOS HERE
│
└── game/                       # Main Django app
    ├── models.py               # GameState + Player models
    ├── game_logic.py           # Pure game logic (GameManager class)
    ├── serializers.py          # DRF request/response serializers
    ├── views.py                # API views (thin — delegate to GameManager)
    ├── urls.py                 # URL routing
    └── migrations/
        └── 0001_initial.py
```

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Run the development server
python manage.py runserver
```

The API is now live at `http://127.0.0.1:8000/`.

---

## Architecture Overview

```
HTTP Request
     │
     ▼
  views.py          ← thin layer: validate input, call GameManager, return Response
     │
     ▼
game_logic.py        ← all game rules live here (GameManager class)
     │
     ├── models.py   ← Django ORM: GameState + Player (SQLite by default)
     └── scenarios/  ← pure Python dicts: no DB dependency
```

**Key design decisions:**

| Decision | Rationale |
|---|---|
| `GameManager` in `game_logic.py` | Keeps all rules in one testable place, decoupled from HTTP |
| Scenario data as Python dicts | Easy to edit; no migrations needed when adding scenarios |
| JSON fields for attributes & votes | Schema-free; attributes can evolve without DB changes |
| Singleton GameState (pk=1) | One active game at a time; `reset=true` on `/join` starts fresh |

---

## Game Flow

```
1. Host sends  POST /join  { "reset": true, "scenario_name": "Nuclear Winter" }
   → Game is wiped and reinitialised. Host receives their player_id.

2. All other players send  POST /join
   → Each gets a unique player_id + hidden character card (???)

3. For each round (5 total):
   a. Host calls  GET /start-round
      → One attribute is revealed for every player (age → health → profession → skill → personality)
   b. Players discuss the revealed info
   c. Any player votes:  POST /vote  { "voter_id": "...", "target_id": "..." }
      → Votes accumulate across all rounds

4. After round 5:
   GET /bunker-result
   → Top voted players (up to bunker_capacity) enter the bunker
   → Their full attributes are scored against scenario weights
   → Returns "success" or "failure" based on threshold

5. At any time:
   GET /game-state
   → Full snapshot: all players, revealed attrs, vote counts, round number
```

---

## API Reference

### `POST /join`

Register a player. The **first player** (host) should pass `"reset": true` to initialise the game.

**Request body** (all fields optional):
```json
{
  "scenario_name": "Nuclear Winter",
  "reset": true
}
```

**Response 201:**
```json
{
  "player_id": "e3a2b1c4-1234-5678-abcd-ef0123456789",
  "message": "Player joined successfully.",
  "total_players": 1,
  "bunker_capacity": 1,
  "scenario": "Nuclear Winter",
  "hidden_attributes": {
    "age": "???",
    "health": "???",
    "profession": "???",
    "skill": "???",
    "personality": "???"
  }
}
```

> **Bunker capacity** = `ceil(total_players × 0.5)` — recalculated on every join.

---

### `GET /start-round`

Advance the game one round. Reveals the next attribute for **all** players simultaneously.

| Round | Revealed Attribute |
|---|---|
| 1 | `age` |
| 2 | `health` |
| 3 | `profession` |
| 4 | `skill` |
| 5 | `personality` |

**Response 200:**
```json
{
  "round_number": 1,
  "revealed_attribute": "age",
  "players": [
    { "player_id": "e3a2b1c4-...", "revealed_value": 35 },
    { "player_id": "f4b3c2d1-...", "revealed_value": 50 },
    { "player_id": "a1b2c3d4-...", "revealed_value": 25 }
  ]
}
```

**Error 400** if all rounds are already complete.

---

### `POST /vote`

Cast a vote for a player to enter the bunker.

**Request body:**
```json
{
  "voter_id":  "e3a2b1c4-...",
  "target_id": "f4b3c2d1-..."
}
```

**Response 200:**
```json
{
  "voter":              "e3a2b1c4-...",
  "target":             "f4b3c2d1-...",
  "target_total_votes": 3,
  "round":              2,
  "message":            "Vote recorded."
}
```

**Error 400** on self-vote, unknown player ID, or voting before round 1.

---

### `GET /bunker-result`

Finalise the game. Selects top-voted players as survivors, scores them, and returns the outcome.

**Response 200:**
```json
{
  "survivors": ["f4b3c2d1-...", "e3a2b1c4-..."],
  "total_points": 235,
  "threshold": 150,
  "outcome": "success",
  "breakdown": [
    {
      "player_id": "f4b3c2d1-...",
      "score": 49,
      "attributes": {
        "age": 30,
        "health": "Healthy",
        "profession": "Doctor",
        "skill": "Surgery",
        "personality": "Calm"
      }
    },
    {
      "player_id": "e3a2b1c4-...",
      "score": 38,
      "attributes": {
        "age": 45,
        "health": "Moderate",
        "profession": "Engineer",
        "skill": "Repair",
        "personality": "Loyal"
      }
    }
  ]
}
```

**Error 400** if not all rounds are complete.

---

### `GET /game-state`

Full snapshot of the active game. Use this to power your frontend display.

**Response 200:**
```json
{
  "game_id": 1,
  "scenario": "Nuclear Winter",
  "total_players": 6,
  "bunker_capacity": 3,
  "round_number": 3,
  "max_rounds": 5,
  "attribute_order": ["age", "health", "profession", "skill", "personality"],
  "outcome": "pending",
  "total_points": 0,
  "threshold": 150,
  "survivors": [],
  "players": [
    {
      "player_id": "abc-123-...",
      "revealed_attrs": {
        "age": 30,
        "health": "Healthy",
        "profession": "Doctor"
      },
      "votes_received": 4,
      "vote_log": [
        { "round": 1, "voters": ["def-456", "ghi-789"] },
        { "round": 2, "voters": ["jkl-012"] },
        { "round": 3, "voters": ["mno-345"] }
      ]
    }
  ]
}
```

---

## Scenarios

Five scenarios are included out of the box:

| Scenario | Threshold | Best Attributes | Special Rule |
|---|---|---|---|
| **Nuclear Winter** | 150 pts | Young, Healthy, Doctor/Engineer, Surgery | No Doctor → −20 pts |
| **Pandemic Outbreak** | 160 pts | Healthy, Doctor/Scientist, Surgery/Research | Weak player → −15 pts unless voted out Round 1 |
| **Climate Collapse** | 140 pts | Farmer/Engineer, Farming/Repair, Loyal | No Farmer → −25 pts |
| **Alien Invasion** | 155 pts | Young, Soldier/Scientist, Defense/Research | No Soldiers → auto-fail |
| **Resource Scarcity** | 145 pts | Farmer/Doctor, Farming/Surgery, Calm/Loyal | Weak survivor → −5 pts each |

---

## Adding Custom Scenarios

Open `scenarios/data.py` and append an entry to the `SCENARIOS` list:

```python
{
    "name": "Solar Flare EMP",
    "description": "All electronics are dead. Mechanical skills rule.",
    "attribute_weights": {
        "age": {
            25: 9,  30: 10,  35: 10,  40: 8,
            45: 6,  50: 5,   55: 3,   60: 2,  65: 1,
        },
        "health": {
            "Healthy": 10,  "Moderate": 5,  "Weak": 1,
        },
        "profession": {
            "Engineer": 10,  "Farmer": 9,   "Soldier": 7,
            "Doctor":    7,  "Teacher": 5,  "Scientist": 4,
        },
        "skill": {
            "Repair":   10,  "Farming":  9,  "Defense":    7,
            "Surgery":   6,  "Research": 4,  "Leadership": 5,
        },
        "personality": {
            "Calm": 10,  "Loyal": 9,  "Neutral": 6,
            "Panic-prone": 2,  "Aggressive": 3,
        },
    },
    "threshold": 145,
    "special_rules": "No special rules.",
}
```

No migrations or code changes needed — the backend loads all scenarios at startup.

To select it, pass `"scenario_name": "Solar Flare EMP"` in the first `POST /join` call with `"reset": true`.

---

## Code Examples

### Random Attribute Assignment (from `game_logic.py`)
```python
ATTRIBUTE_POOL = {
    "age":         [25, 30, 35, 40, 45, 50, 55, 60, 65],
    "health":      ["Healthy", "Moderate", "Weak"],
    "profession":  ["Doctor", "Engineer", "Farmer", "Soldier", "Scientist", "Teacher"],
    "skill":       ["Surgery", "Repair", "Farming", "Defense", "Research", "Leadership"],
    "personality": ["Calm", "Neutral", "Panic-prone", "Aggressive", "Loyal"],
}

def _assign_random_attributes() -> dict:
    return {key: random.choice(values) for key, values in ATTRIBUTE_POOL.items()}
# → {"age": 35, "health": "Healthy", "profession": "Doctor",
#    "skill": "Surgery", "personality": "Calm"}
```

### Round-by-Round Reveal (from `GameManager.start_round`)
```python
ATTRIBUTE_REVEAL_ORDER = ["age", "health", "profession", "skill", "personality"]

# round_number advances 1 → 2 → 3 → 4 → 5
attr_to_reveal = game.attribute_order[game.round_number - 1]
# Round 1 → "age", Round 2 → "health", etc.

for player in players:
    player.revealed_attrs["age"] = player.attributes["age"]
    player.save()
```

### Voting Process (from `Player.add_vote`)
```python
def add_vote(self, voter_id: str, round_number: int) -> None:
    self.votes_received += 1          # cumulative tally
    log_entry = next(
        (e for e in self.vote_log if e["round"] == round_number), None
    )
    if log_entry:
        log_entry["voters"].append(voter_id)   # add to existing round
    else:
        self.vote_log.append({"round": round_number, "voters": [voter_id]})
    self.save()
```

### Multi-Attribute Scoring (from `game_logic._calculate_player_score`)
```python
# Scenario weights (Nuclear Winter excerpt):
weights = {
    "age":      {30: 9},
    "health":   {"Healthy": 10},
    "profession": {"Doctor": 10},
    "skill":    {"Surgery": 10},
    "personality": {"Calm": 10},
}

# Player: age=30, health="Healthy", profession="Doctor",
#         skill="Surgery", personality="Calm"
score = 9 + 10 + 10 + 10 + 10  # = 49

# Threshold comparison:
total_points = sum(score for each survivor)
outcome = "success" if total_points >= threshold else "failure"
```
