"""
game/views.py
-------------
DRF API views for the AI-driven Survival Game.

Endpoints:
  POST /join          – Register a player; optionally reset the game first.
  GET  /start-round   – Reveal the next attribute for all players.
  POST /vote          – Cast a vote for a player.
  GET  /bunker-result – Compute survivors and score them.
  GET  /game-state    – Return the full current game state.

Error handling:
  - 400 Bad Request  : Invalid input, rule violations, out-of-order calls.
  - 404 Not Found    : Referenced player IDs don't exist.
  - 500 Server Error : Unexpected failures (caught generically for safety).
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .game_logic import GameManager, ATTRIBUTE_POOL
from .serializers import (
    JoinRequestSerializer,
    VoteRequestSerializer,
    PlayerJoinSerializer,
    RoundResultSerializer,
    VoteResultSerializer,
    BunkerResultSerializer,
    GameStateSerializer,
)

# Single shared manager instance (stateless object; all state lives in DB)
_manager = GameManager()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _error(message: str, code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    """Return a standardised error response."""
    return Response({"error": message}, status=code)


# ---------------------------------------------------------------------------
# POST /join
# ---------------------------------------------------------------------------

@api_view(["POST"])
def join(request: Request) -> Response:
    """
    Register a player in the active (or newly created) game.

    Request body (all optional):
        {
            "scenario_name": "Nuclear Winter",   // default if omitted
            "reset": false                        // set true to start fresh game
        }

    Response 201:
        {
            "player_id": "e3a2b1c4-...",
            "message": "Player joined successfully.",
            "total_players": 4,
            "bunker_capacity": 2,
            "scenario": "Nuclear Winter",
            "hidden_attributes": {
                "age": "???",
                "health": "???",
                "profession": "???",
                "skill": "???",
                "personality": "???"
            }
        }

    Notes:
        • All attributes are assigned randomly at join but remain hidden
          (the client receives '???' placeholders so they know the categories).
        • The first player to join should set reset=true to initialise the game.
    """
    serializer = JoinRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return _error(str(serializer.errors))

    scenario_name = serializer.validated_data["scenario_name"]
    should_reset  = serializer.validated_data["reset"]

    try:
        if should_reset:
            _manager.reset(scenario_name=scenario_name)

        player = _manager.register_player()
        game   = player.game

    except (ValueError, RuntimeError) as exc:
        return _error(str(exc))

    # Build hidden attribute placeholders
    hidden_attrs = {key: "???" for key in ATTRIBUTE_POOL}

    response_data = {
        "player_id":        player.player_id,
        "message":          "Player joined successfully.",
        "total_players":    game.total_players,
        "bunker_capacity":  game.bunker_capacity,
        "scenario":         game.scenario_name,
        "hidden_attributes": hidden_attrs,
    }

    return Response(
        PlayerJoinSerializer(response_data).data,
        status=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# GET /start-round
# ---------------------------------------------------------------------------

@api_view(["GET"])
def start_round(request: Request) -> Response:
    """
    Advance the game by one round and reveal the next attribute for all players.

    Response 200:
        {
            "round_number": 1,
            "revealed_attribute": "age",
            "players": [
                {"player_id": "abc...", "revealed_value": 35},
                {"player_id": "def...", "revealed_value": 50},
                ...
            ]
        }

    Rounds map to attributes in this order:
        Round 1 → age
        Round 2 → health
        Round 3 → profession
        Round 4 → skill
        Round 5 → personality

    Returns 400 once all rounds are complete (call /bunker-result instead).
    """
    try:
        result = _manager.start_round()
    except (ValueError, RuntimeError) as exc:
        return _error(str(exc))

    return Response(RoundResultSerializer(result).data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# POST /vote
# ---------------------------------------------------------------------------

@api_view(["POST"])
def vote(request: Request) -> Response:
    """
    Record a vote from one player in favour of another for bunker admission.

    Request body:
        {
            "voter_id":  "abc-123-...",
            "target_id": "def-456-..."
        }

    Response 200:
        {
            "voter":              "abc-123-...",
            "target":             "def-456-...",
            "target_total_votes": 3,
            "round":              2,
            "message":            "Vote recorded."
        }

    Rules:
        • A player cannot vote for themselves (400).
        • Both IDs must belong to the active game (400).
        • Voting before the first round starts returns 400.
        • Multiple votes from the same player are allowed (no cap enforced here;
          adjust record_vote() in game_logic.py if a "one vote per round" rule
          is desired).
    """
    serializer = VoteRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return _error(str(serializer.errors))

    voter_id  = serializer.validated_data["voter_id"]
    target_id = serializer.validated_data["target_id"]

    try:
        result = _manager.record_vote(voter_id, target_id)
    except ValueError as exc:
        return _error(str(exc))
    except RuntimeError as exc:
        return _error(str(exc), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    result["message"] = "Vote recorded."
    return Response(VoteResultSerializer(result).data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# GET /bunker-result
# ---------------------------------------------------------------------------

@api_view(["GET"])
def bunker_result(request: Request) -> Response:
    """
    Finalise the game: select survivors, score them, and return the outcome.

    This endpoint is idempotent — calling it multiple times returns the same
    result once survivors are computed (it will rerun scoring each call).

    Response 200:
        {
            "survivors": ["abc-123", "def-456", ...],
            "total_points": 235,
            "threshold": 150,
            "outcome": "success",
            "breakdown": [
                {
                    "player_id": "abc-123",
                    "score": 47,
                    "attributes": {
                        "age": 30,
                        "health": "Healthy",
                        "profession": "Doctor",
                        "skill": "Surgery",
                        "personality": "Calm"
                    }
                },
                ...
            ]
        }

    Returns 400 if not all rounds have been completed yet.
    """
    try:
        # Step 1: Determine who enters the bunker (top voted players)
        _manager.compute_bunker()

        # Step 2: Score survivors against the scenario threshold
        result = _manager.score_survivors()

    except (ValueError, RuntimeError) as exc:
        return _error(str(exc))

    return Response(BunkerResultSerializer(result).data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# GET /game-state
# ---------------------------------------------------------------------------

@api_view(["GET"])
def game_state(request: Request) -> Response:
    """
    Return a full snapshot of the current game for display or debugging.

    Response 200:
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
                    "player_id": "abc-123",
                    "revealed_attrs": {"age": 30, "health": "Healthy", "profession": "Doctor"},
                    "votes_received": 4,
                    "vote_log": [
                        {"round": 1, "voters": ["def-456", "ghi-789"]},
                        {"round": 2, "voters": ["jkl-012"]},
                        {"round": 3, "voters": ["mno-345"]}
                    ]
                },
                ...
            ]
        }

    Returns 500 if no game has been initialised.
    """
    try:
        state = _manager.get_state()
    except RuntimeError as exc:
        return _error(str(exc), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(GameStateSerializer(state).data, status=status.HTTP_200_OK)
