"""
game/urls.py
------------
URL routing for all game API endpoints.

Endpoint summary:
  POST /join          – Player joins game (optionally resets it).
  GET  /start-round   – Reveal next attribute for all players.
  POST /vote          – Cast a vote for a player.
  GET  /bunker-result – Finalise survivors and compute outcome.
  GET  /game-state    – Full game state snapshot.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("join",          views.join,          name="join"),
    path("start-round",   views.start_round,   name="start-round"),
    path("vote",          views.vote,           name="vote"),
    path("bunker-result", views.bunker_result,  name="bunker-result"),
    path("game-state",    views.game_state,     name="game-state"),
]
