"""
game/serializers.py
-------------------
DRF serializers for API request validation and response shaping.

Serializers defined here:
  - JoinRequestSerializer    – Validates POST /join body (optional scenario choice).
  - PlayerJoinSerializer     – Shapes the POST /join response.
  - VoteRequestSerializer    – Validates POST /vote body.
  - RoundResultSerializer    – Shapes GET /start-round response.
  - BunkerResultSerializer   – Shapes GET /bunker-result response.
  - GameStateSerializer      – Shapes GET /game-state response.
"""

from rest_framework import serializers


# ---------------------------------------------------------------------------
# Request serializers (input validation)
# ---------------------------------------------------------------------------

class JoinRequestSerializer(serializers.Serializer):
    """
    Optional body for POST /join.

    If scenario_name is omitted the backend defaults to "Nuclear Winter".
    If reset=True the entire game is wiped before the player joins, which
    is convenient for starting a fresh game from the first player's join call.
    """
    scenario_name = serializers.CharField(
        required=False,
        default="Nuclear Winter",
        help_text="Name of the scenario to play. Ignored unless reset=True.",
    )
    reset = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Set to true to reset the game before joining (host privilege).",
    )


class VoteRequestSerializer(serializers.Serializer):
    """
    Body for POST /vote.

    Both IDs are required; the backend validates they belong to the active game.
    """
    voter_id = serializers.CharField(
        help_text="player_id of the person casting the vote."
    )
    target_id = serializers.CharField(
        help_text="player_id of the player being voted for bunker admission."
    )


# ---------------------------------------------------------------------------
# Response serializers (output shaping)
# ---------------------------------------------------------------------------

class PlayerJoinSerializer(serializers.Serializer):
    """
    Response body for POST /join.

    Attributes are returned as an empty dict to signal they are assigned but
    still hidden. The client only needs the player_id for subsequent calls.
    """
    player_id = serializers.CharField()
    message = serializers.CharField()
    total_players = serializers.IntegerField()
    bunker_capacity = serializers.IntegerField()
    scenario = serializers.CharField()
    # Attributes are hidden at join; we return the keys so the client knows
    # which categories exist, but values are masked.
    hidden_attributes = serializers.DictField(
        child=serializers.CharField(),
        help_text="Attribute names mapped to '???' to indicate they are hidden.",
    )


class RoundRevealPlayerSerializer(serializers.Serializer):
    """Per-player slice inside a round-reveal response."""
    player_id = serializers.CharField()
    revealed_value = serializers.CharField(allow_null=True)


class RoundResultSerializer(serializers.Serializer):
    """Response body for GET /start-round."""
    round_number = serializers.IntegerField()
    revealed_attribute = serializers.CharField()
    players = RoundRevealPlayerSerializer(many=True)


class VoteResultSerializer(serializers.Serializer):
    """Response body for POST /vote."""
    voter = serializers.CharField()
    target = serializers.CharField()
    target_total_votes = serializers.IntegerField()
    round = serializers.IntegerField()
    message = serializers.CharField()


class SurvivorBreakdownSerializer(serializers.Serializer):
    """Per-survivor breakdown inside the bunker result."""
    player_id = serializers.CharField()
    score = serializers.IntegerField()
    attributes = serializers.DictField()


class BunkerSurvivorSerializer(serializers.Serializer):
    """Summary of each survivor (votes + full attributes)."""
    player_id = serializers.CharField()
    votes = serializers.IntegerField()
    attributes = serializers.DictField()


class BunkerResultSerializer(serializers.Serializer):
    """Response body for GET /bunker-result."""
    survivors = serializers.ListField(child=serializers.CharField())
    total_points = serializers.IntegerField()
    threshold = serializers.IntegerField()
    outcome = serializers.CharField()
    breakdown = SurvivorBreakdownSerializer(many=True)


class PlayerStateSerializer(serializers.Serializer):
    """Per-player slice inside the full game state."""
    player_id = serializers.CharField()
    revealed_attrs = serializers.DictField()
    votes_received = serializers.IntegerField()
    vote_log = serializers.ListField()


class GameStateSerializer(serializers.Serializer):
    """Response body for GET /game-state."""
    game_id = serializers.IntegerField()
    scenario = serializers.CharField()
    total_players = serializers.IntegerField()
    bunker_capacity = serializers.IntegerField()
    round_number = serializers.IntegerField()
    max_rounds = serializers.IntegerField()
    attribute_order = serializers.ListField(child=serializers.CharField())
    outcome = serializers.CharField()
    total_points = serializers.IntegerField()
    threshold = serializers.IntegerField()
    survivors = serializers.ListField(child=serializers.CharField())
    players = PlayerStateSerializer(many=True)
