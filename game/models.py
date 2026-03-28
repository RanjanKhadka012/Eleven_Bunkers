"""
game/models.py
--------------
Data models for the AI-driven Survival Game.

Models:
  - GameState  : Singleton-like model tracking the active game session.
  - Player     : Each participant with their assigned attributes, vote tallies,
                 and a record of which attributes have been revealed so far.

Design notes:
  - Attributes and votes are stored as JSON fields so no schema change is
    needed when attribute lists evolve.
  - A single GameState row is created/reset per game session via the
    GameManager helper in game_logic.py.
  - The Scenario data is stored inline on GameState (copied from scenarios/data.py)
    so a game record is self-contained and not broken if scenario definitions change.
"""

from django.db import models


# ---------------------------------------------------------------------------
# GameState
# ---------------------------------------------------------------------------

class GameState(models.Model):
    """
    Represents a single game session.

    Only one active GameState is expected at a time (id=1 is reused by the
    GameManager.reset() helper). Additional rows can exist for historical
    record-keeping if desired.

    Fields:
      scenario_name      – Human-readable name of the selected scenario.
      scenario_data      – Full snapshot of the scenario dict (weights,
                           threshold, special_rules) at game-start time.
      total_players      – Count of joined players; drives bunker capacity.
      bunker_capacity    – ceil(total_players * 0.5); updated on each join.
      round_number       – Current reveal round (0 = not started yet).
      attribute_order    – JSON list of attribute names in reveal order.
                           Example: ["age", "health", "profession", "skill", "personality"]
      survivors          – JSON list of player UUIDs admitted to the bunker.
      total_points       – Aggregate score of survivors (set after scoring).
      outcome            – "pending" | "success" | "failure".
      created_at         – Timestamp when the game was initialised.
    """

    scenario_name = models.CharField(max_length=200, default="Nuclear Winter")
    scenario_data = models.JSONField(default=dict)

    total_players = models.IntegerField(default=0)
    bunker_capacity = models.IntegerField(default=0)

    round_number = models.IntegerField(default=0)

    # Ordered list of attribute keys to reveal one per round
    # e.g. ["age", "health", "profession", "skill", "personality"]
    attribute_order = models.JSONField(
        default=list,
        help_text="Ordered list of attribute names; one is revealed per round."
    )

    # UUIDs of players admitted to the bunker after voting concludes
    survivors = models.JSONField(default=list)

    total_points = models.IntegerField(default=0)

    outcome = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending",  "Pending"),
            ("success",  "Success"),
            ("failure",  "Failure"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game #{self.pk} — {self.scenario_name} ({self.outcome})"

    @property
    def max_rounds(self):
        """Total number of rounds equals the number of attributes to reveal."""
        return len(self.attribute_order)

    @property
    def current_reveal_attribute(self):
        """
        Returns the attribute name that was revealed in the most recent round,
        or None if no round has started.
        """
        if self.round_number == 0 or not self.attribute_order:
            return None
        idx = self.round_number - 1
        if idx < len(self.attribute_order):
            return self.attribute_order[idx]
        return None  # All attributes revealed


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player(models.Model):
    """
    Represents a single participant in the game.

    Fields:
      player_id        – UUID string, the public identifier shared with the client.
      game             – FK to the GameState this player belongs to.
      attributes       – Full dict of assigned attribute values.
                         Example: {"age": 30, "health": "Healthy",
                                   "profession": "Doctor", "skill": "Surgery",
                                   "personality": "Calm"}
      revealed_attrs   – Dict of attribute_name -> value for attributes that
                         have been publicly revealed so far.
                         Starts empty; grows one key per round.
      votes_received   – Cumulative count of votes this player has received
                         across all rounds.
      vote_log         – JSON list of per-round vote records.
                         Each entry: {"round": int, "voters": [player_id, ...]}
      joined_at        – Timestamp of player registration.
    """

    player_id = models.CharField(
        max_length=36,
        unique=True,
        db_index=True,
        help_text="UUID assigned on join; shared with client as their identity token."
    )

    game = models.ForeignKey(
        GameState,
        on_delete=models.CASCADE,
        related_name="players",
    )

    # Full hidden attribute set — never sent to clients directly
    attributes = models.JSONField(
        default=dict,
        help_text="Complete attribute dict. Keep hidden until revealed by round logic."
    )

    # Subset of attributes that have been publicly revealed
    revealed_attrs = models.JSONField(
        default=dict,
        help_text="Attribute key/value pairs revealed so far."
    )

    # Total votes received; used for bunker admission ranking
    votes_received = models.IntegerField(default=0)

    # Detailed per-round vote log for audit / replay
    vote_log = models.JSONField(
        default=list,
        help_text="List of {round, voters} dicts recording who voted for this player."
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Player {self.player_id[:8]}… (game #{self.game_id})"

    def reveal_attribute(self, attr_name: str) -> None:
        """
        Move a single attribute from hidden to revealed.
        Safe to call even if already revealed (idempotent).

        Args:
            attr_name: Key from self.attributes to reveal (e.g. "age").
        """
        if attr_name in self.attributes and attr_name not in self.revealed_attrs:
            self.revealed_attrs[attr_name] = self.attributes[attr_name]
            self.save(update_fields=["revealed_attrs"])

    def add_vote(self, voter_id: str, round_number: int) -> None:
        """
        Record a vote cast for this player.

        Args:
            voter_id:     player_id of the voter.
            round_number: Current game round number.
        """
        self.votes_received += 1

        # Append to the round-level log
        log_entry = next(
            (e for e in self.vote_log if e["round"] == round_number), None
        )
        if log_entry:
            log_entry["voters"].append(voter_id)
        else:
            self.vote_log.append({"round": round_number, "voters": [voter_id]})

        self.save(update_fields=["votes_received", "vote_log"])
