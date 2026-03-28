"""
game/game_logic.py
------------------
Pure game logic, decoupled from HTTP concerns.

Responsibilities:
  1. ATTRIBUTE_POOL      – Central definitions of all possible attribute values.
  2. GameManager         – Class encapsulating all stateful operations:
       • reset()          – Wipe and reinitialise the game with a chosen scenario.
       • register_player()– Create a Player with randomly assigned attributes.
       • start_round()    – Advance round counter and reveal next attribute
                            for every player.
       • record_vote()    – Cast a vote from one player targeting another.
       • compute_bunker() – Rank players by votes → select top N survivors.
       • score_survivors()– Calculate aggregate attribute points vs. threshold.
       • get_state()      – Return a serialisable snapshot of the full game state.

All methods raise ValueError with descriptive messages on invalid operations
so that views can catch them and return clean 400/404 responses.
"""

import math
import random
import uuid

from django.db import transaction

from scenarios import SCENARIOS
from .models import GameState, Player


# ---------------------------------------------------------------------------
# Attribute pool
# ---------------------------------------------------------------------------

ATTRIBUTE_POOL = {
    "age":         [25, 30, 35, 40, 45, 50, 55, 60, 65],
    "health":      ["Healthy", "Moderate", "Weak"],
    "profession":  ["Doctor", "Engineer", "Farmer", "Soldier", "Scientist", "Teacher"],
    "skill":       ["Surgery", "Repair", "Farming", "Defense", "Research", "Leadership"],
    "personality": ["Calm", "Neutral", "Panic-prone", "Aggressive", "Loyal"],
}

# The canonical order in which attributes are revealed, one per round.
ATTRIBUTE_REVEAL_ORDER = ["age", "health", "profession", "skill", "personality"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assign_random_attributes() -> dict:
    """
    Randomly select one value per attribute category.

    Example output:
        {
            "age": 35,
            "health": "Healthy",
            "profession": "Doctor",
            "skill": "Surgery",
            "personality": "Calm"
        }
    """
    return {key: random.choice(values) for key, values in ATTRIBUTE_POOL.items()}


def _get_scenario_by_name(name: str) -> dict:
    """
    Retrieve a scenario dict from the SCENARIOS list by name (case-insensitive).

    Raises:
        ValueError: If no matching scenario is found.
    """
    for scenario in SCENARIOS:
        if scenario["name"].lower() == name.lower():
            return scenario
    available = [s["name"] for s in SCENARIOS]
    raise ValueError(
        f"Scenario '{name}' not found. Available scenarios: {available}"
    )


def _calculate_player_score(player: Player, weights: dict) -> int:
    """
    Sum point values for ALL attributes of a single player using scenario weights.

    Args:
        player:  Player model instance.
        weights: scenario["attribute_weights"] dict mapping
                 attribute_name -> {value -> points}.

    Returns:
        Total integer score for this player.

    Example:
        weights = {"age": {30: 9}, "health": {"Healthy": 10}, ...}
        player.attributes = {"age": 30, "health": "Healthy", ...}
        → score = 9 + 10 + ...
    """
    score = 0
    for attr_name, attr_value in player.attributes.items():
        attr_weights = weights.get(attr_name, {})
        # Integer keys in JSON are stored as strings; try both
        points = attr_weights.get(attr_value, attr_weights.get(str(attr_value), 0))
        score += points
    return score


# ---------------------------------------------------------------------------
# GameManager
# ---------------------------------------------------------------------------

class GameManager:
    """
    Central controller for one game session.

    Typical lifecycle:
        gm = GameManager()
        gm.reset(scenario_name="Nuclear Winter")
        gm.register_player()   # called N times as players join
        gm.start_round()       # called once per round (up to 5 rounds)
        gm.record_vote(voter_id, target_id)   # called for each vote
        gm.compute_bunker()    # called after final round
        gm.score_survivors()   # called after bunker is computed
        gm.get_state()         # read current game snapshot at any time
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def reset(self, scenario_name: str = "Nuclear Winter") -> GameState:
        """
        Wipe all existing Player rows and reset (or create) the singleton
        GameState to a fresh state with the requested scenario.

        Args:
            scenario_name: Must match a scenario name in scenarios/data.py.

        Returns:
            The fresh GameState instance.
        """
        scenario = _get_scenario_by_name(scenario_name)

        with transaction.atomic():
            # Delete all players for any existing game
            Player.objects.all().delete()

            # Re-use id=1 as the single active game record
            game, _ = GameState.objects.update_or_create(
                pk=1,
                defaults={
                    "scenario_name":  scenario["name"],
                    "scenario_data":  scenario,
                    "total_players":  0,
                    "bunker_capacity": 0,
                    "round_number":   0,
                    "attribute_order": ATTRIBUTE_REVEAL_ORDER,
                    "survivors":      [],
                    "total_points":   0,
                    "outcome":        "pending",
                },
            )
        return game

    # ------------------------------------------------------------------
    # Player registration
    # ------------------------------------------------------------------

    def register_player(self) -> Player:
        """
        Add a new player to the active game session.

        - Assigns a fresh UUID as player_id.
        - Randomly assigns one value per attribute from ATTRIBUTE_POOL.
        - Updates total_players and bunker_capacity on GameState.
        - All attributes start hidden (revealed_attrs is empty).

        Returns:
            The newly created Player instance.

        Raises:
            RuntimeError: If no active GameState exists (call reset() first).

        Example:
            player = gm.register_player()
            # player.player_id  → "e3a2b1c4-..."
            # player.attributes → {"age": 30, "health": "Healthy", ...}
            # player.revealed_attrs → {}  (all hidden)
        """
        try:
            game = GameState.objects.get(pk=1)
        except GameState.DoesNotExist:
            raise RuntimeError(
                "No active game found. Call reset() before registering players."
            )

        attributes = _assign_random_attributes()
        player_id = str(uuid.uuid4())

        with transaction.atomic():
            player = Player.objects.create(
                player_id=player_id,
                game=game,
                attributes=attributes,
                revealed_attrs={},
                votes_received=0,
                vote_log=[],
            )

            # Update headcount and recalculate bunker capacity: ceil(n * 0.5)
            game.total_players = Player.objects.filter(game=game).count()
            game.bunker_capacity = math.ceil(game.total_players * 0.5)
            game.save(update_fields=["total_players", "bunker_capacity"])

        return player

    # ------------------------------------------------------------------
    # Round management
    # ------------------------------------------------------------------

    def start_round(self) -> dict:
        """
        Advance the game by one round:
          1. Increment round_number on GameState.
          2. Determine which attribute to reveal this round.
          3. Call player.reveal_attribute() for every player.

        Returns a dict summarising the round:
            {
                "round_number": 2,
                "revealed_attribute": "health",
                "players": [
                    {
                        "player_id": "...",
                        "revealed_value": "Healthy"
                    },
                    ...
                ]
            }

        Raises:
            ValueError: If all attributes have already been revealed,
                        or if no players are in the game.
        """
        game = self._get_active_game()

        if game.round_number >= game.max_rounds:
            raise ValueError(
                f"All {game.max_rounds} rounds have already been played. "
                "Call compute_bunker() to finalise the game."
            )

        players = list(game.players.all())
        if not players:
            raise ValueError("No players have joined yet.")

        # Advance round counter
        game.round_number += 1
        game.save(update_fields=["round_number"])

        # Which attribute is revealed this round?
        attr_to_reveal = game.attribute_order[game.round_number - 1]

        # Reveal that attribute for every player
        reveal_summary = []
        for player in players:
            player.reveal_attribute(attr_to_reveal)
            reveal_summary.append({
                "player_id":      player.player_id,
                "revealed_value": player.attributes.get(attr_to_reveal),
            })

        return {
            "round_number":       game.round_number,
            "revealed_attribute": attr_to_reveal,
            "players":            reveal_summary,
        }

    # ------------------------------------------------------------------
    # Voting
    # ------------------------------------------------------------------

    def record_vote(self, voter_id: str, target_id: str) -> dict:
        """
        Record one vote cast by voter_id for target_id.

        Rules enforced:
          - Both player IDs must exist in the current game.
          - A player cannot vote for themselves.
          - Voting is only allowed while rounds are in progress (round ≥ 1).

        Args:
            voter_id:  player_id of the voter.
            target_id: player_id of the candidate being voted for.

        Returns:
            {"voter": voter_id, "target": target_id,
             "target_total_votes": int, "round": int}

        Raises:
            ValueError: On self-vote, unknown IDs, or invalid round state.

        Example:
            result = gm.record_vote("abc-123", "def-456")
            # result → {"voter": "abc-123", "target": "def-456",
            #            "target_total_votes": 3, "round": 2}
        """
        if voter_id == target_id:
            raise ValueError("A player cannot vote for themselves.")

        game = self._get_active_game()

        if game.round_number == 0:
            raise ValueError("Voting is not allowed before the first round starts.")

        # Validate both players belong to this game
        try:
            voter = Player.objects.get(player_id=voter_id, game=game)  # noqa: F841
        except Player.DoesNotExist:
            raise ValueError(f"Voter '{voter_id}' not found in the active game.")

        try:
            target = Player.objects.get(player_id=target_id, game=game)
        except Player.DoesNotExist:
            raise ValueError(f"Target '{target_id}' not found in the active game.")

        target.add_vote(voter_id=voter_id, round_number=game.round_number)

        return {
            "voter":              voter_id,
            "target":             target_id,
            "target_total_votes": target.votes_received,
            "round":              game.round_number,
        }

    # ------------------------------------------------------------------
    # Bunker admission
    # ------------------------------------------------------------------

    def compute_bunker(self) -> dict:
        """
        Determine which players enter the bunker after all rounds are complete.

        Algorithm:
          1. Rank all players by cumulative votes_received (descending).
          2. Take the top bunker_capacity players as survivors.
          3. Persist survivor IDs on GameState.

        Returns:
            {
                "bunker_capacity": 3,
                "survivors": [
                    {"player_id": "...", "votes": 5, "attributes": {...}},
                    ...
                ]
            }

        Raises:
            ValueError: If not all rounds have been played yet.
        """
        game = self._get_active_game()

        if game.round_number < game.max_rounds:
            raise ValueError(
                f"Only {game.round_number}/{game.max_rounds} rounds have been played. "
                "Complete all rounds before computing the bunker."
            )

        players = list(game.players.order_by("-votes_received"))
        top_players = players[: game.bunker_capacity]

        game.survivors = [p.player_id for p in top_players]
        game.save(update_fields=["survivors"])

        return {
            "bunker_capacity": game.bunker_capacity,
            "survivors": [
                {
                    "player_id":  p.player_id,
                    "votes":      p.votes_received,
                    "attributes": p.attributes,  # full reveal on bunker admission
                }
                for p in top_players
            ],
        }

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score_survivors(self) -> dict:
        """
        Calculate the total attribute score for all bunker survivors and
        compare it to the scenario threshold to determine success or failure.

        Score calculation:
          For each survivor, for each of their 5 attributes, look up the
          point value in scenario["attribute_weights"][attr][value] and sum.

        Outcome logic:
          total_points >= scenario["threshold"]  → "success"
          total_points <  scenario["threshold"]  → "failure"

        Returns:
            {
                "survivors": [...],     # list of survivor player_ids
                "total_points": 312,
                "threshold":    150,
                "outcome":      "success",
                "breakdown": [
                    {
                        "player_id": "...",
                        "score": 47,
                        "attributes": {...}
                    },
                    ...
                ]
            }

        Raises:
            ValueError: If compute_bunker() has not been called yet.

        Example scoring:
            # Scenario: Nuclear Winter
            # weights["age"][30] = 9, weights["health"]["Healthy"] = 10, etc.
            # Player attrs: {age:30, health:"Healthy", profession:"Doctor",
            #                skill:"Surgery", personality:"Calm"}
            # Score: 9 + 10 + 10 + 10 + 10 = 49
        """
        game = self._get_active_game()

        if not game.survivors:
            raise ValueError(
                "No survivors computed yet. Call compute_bunker() first."
            )

        scenario_data  = game.scenario_data
        weights        = scenario_data.get("attribute_weights", {})
        threshold      = scenario_data.get("threshold", 0)

        breakdown      = []
        total_points   = 0

        for player_id in game.survivors:
            try:
                player = Player.objects.get(player_id=player_id, game=game)
            except Player.DoesNotExist:
                continue  # Defensive: skip orphaned IDs

            player_score = _calculate_player_score(player, weights)
            total_points += player_score
            breakdown.append({
                "player_id":  player_id,
                "score":      player_score,
                "attributes": player.attributes,
            })

        outcome = "success" if total_points >= threshold else "failure"

        game.total_points = total_points
        game.outcome = outcome
        game.save(update_fields=["total_points", "outcome"])

        return {
            "survivors":    game.survivors,
            "total_points": total_points,
            "threshold":    threshold,
            "outcome":      outcome,
            "breakdown":    breakdown,
        }

    # ------------------------------------------------------------------
    # Full game state snapshot
    # ------------------------------------------------------------------

    def get_state(self) -> dict:
        """
        Return a complete, serialisable snapshot of the current game state.

        Useful for the /game-state endpoint and debugging.

        Returns a dict containing:
          - scenario info
          - player list (with revealed attributes and vote counts)
          - round number and total rounds
          - survivors and scoring outcome
        """
        game = self._get_active_game()
        players = list(game.players.all())

        return {
            "game_id":         game.pk,
            "scenario":        game.scenario_name,
            "total_players":   game.total_players,
            "bunker_capacity": game.bunker_capacity,
            "round_number":    game.round_number,
            "max_rounds":      game.max_rounds,
            "attribute_order": game.attribute_order,
            "outcome":         game.outcome,
            "total_points":    game.total_points,
            "threshold":       game.scenario_data.get("threshold", 0),
            "survivors":       game.survivors,
            "players": [
                {
                    "player_id":      p.player_id,
                    "revealed_attrs": p.revealed_attrs,
                    "votes_received": p.votes_received,
                    "vote_log":       p.vote_log,
                }
                for p in players
            ],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_active_game() -> GameState:
        """
        Retrieve the singleton active GameState (pk=1).

        Raises:
            RuntimeError: If no game has been initialised yet.
        """
        try:
            return GameState.objects.get(pk=1)
        except GameState.DoesNotExist:
            raise RuntimeError(
                "No active game found. POST /join to start a new game."
            )
