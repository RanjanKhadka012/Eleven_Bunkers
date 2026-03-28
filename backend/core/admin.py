"""
Django Admin Configuration for Bunker Game

Registers all game models with the Django admin interface.
Provides searchable, filterable views for managing game data:
- Card definitions
- Catastrophe and bunker scenarios
- Active game sessions
- Player hands and scores
- Voting records
- Game event logs

Access at: http://localhost:8000/admin/
"""

from django.contrib import admin
from .models import (
    CardType, Card, Catastrophe, Bunker, GameSession, PlayerHand,
    SpecialCondition, PlayerSpecialCard, VoteRound, Vote, GameLog
)


# ========================================
# CARD ADMINISTRATION
# ========================================

@admin.register(CardType)
class CardTypeAdmin(admin.ModelAdmin):
    """
    Card type categories (profession, skill, biological, etc.)
    Read-only in admin - should not be changed after creation
    """
    list_display = ['card_type']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """
    Individual game cards with scores
    
    Admin Features:
    - Sort by name, type, or points
    - Filter by type and point value
    - Search by card name
    
    Typically populated via management command: python manage.py populate_bunker_data
    """
    list_display = ['name', 'card_type', 'points']
    list_filter = ['card_type', 'points']
    search_fields = ['name']


# ========================================
# SCENARIO ADMINISTRATION
# ========================================

@admin.register(Catastrophe)
class CatastropheAdmin(admin.ModelAdmin):
    """
    Catastrophe scenarios that affect survival threshold
    
    Each catastrophe has a modifier that increases the difficulty.
    Examples: Nuclear War (+10), Pandemic (+8), Climate Change (+5)
    """
    list_display = ['name', 'modifier']


@admin.register(Bunker)
class BunkerAdmin(admin.ModelAdmin):
    """
    Bunker conditions (advantages and disadvantages)
    
    Positive conditions: make survival easier (negative modifier)
    Negative conditions: make survival harder (positive modifier)
    
    Filter by is_positive to see advantages vs disadvantages
    """
    list_display = ['name', 'modifier', 'is_positive']
    list_filter = ['is_positive']


@admin.register(SpecialCondition)
class SpecialConditionAdmin(admin.ModelAdmin):
    """
    Special condition cards (non-scoring strategic cards)
    
    These are assigned 2 per player and don't count toward the survival score.
    They provide special abilities or effects during gameplay.
    """
    list_display = ['name']


# ========================================
# GAME SESSION ADMINISTRATION
# ========================================

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    """
    Active and completed game sessions
    
    Admin Features:
    - Track game phase (setup, reveal, voting, final_scoring, completed)
    - Monitor game status (active, completed, failed)
    - View final scores and thresholds
    - Search by game ID or creator username
    - Filter by phase, status, and creation date
    
    View to understand:
    - How many survivors are needed
    - What threshold was calculated
    - Which catastrophe/bunker was selected
    """
    list_display = ['game_id', 'created_by', 'current_phase', 'status', 'final_score', 'final_threshold']
    list_filter = ['current_phase', 'status', 'created_at']
    search_fields = ['game_id', 'created_by__username']


@admin.register(PlayerHand)
class PlayerHandAdmin(admin.ModelAdmin):
    """
    Individual player cards in a game
    
    Admin Features:
    - See which players are in which games
    - Track elimination status
    - View final scores
    - Filter by eliminated status
    
    Shows:
    - Player name and game session
    - Whether player was eliminated
    - Final calculated score from cards
    """
    list_display = ['player', 'game_session', 'is_eliminated', 'total_score']
    list_filter = ['is_eliminated', 'game_session']
    search_fields = ['player__username']


# ========================================
# VOTING ADMINISTRATION
# ========================================

@admin.register(PlayerSpecialCard)
class PlayerSpecialCardAdmin(admin.ModelAdmin):
    """
    Special condition cards assigned to players
    
    Tracks:
    - Which player has which special card
    - Whether the card has been used
    - When it was used
    """
    list_display = ['player_hand', 'special_condition', 'used']
    list_filter = ['used']


@admin.register(VoteRound)
class VoteRoundAdmin(admin.ModelAdmin):
    """
    Voting rounds in a game
    
    Multiple rounds happen during voting phase as players get eliminated.
    Round 1: vote to eliminate first player
    Round 2: vote to eliminate second player
    etc.
    """
    list_display = ['game_session', 'round_number']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """
    Individual votes cast by players
    
    Shows:
    - Which player voted for whom
    - Which voting round
    
    Useful for analyzing voting patterns
    """
    list_display = ['vote_round', 'voter', 'voted_for']


# ========================================
# GAME LOG ADMINISTRATION
# ========================================

@admin.register(GameLog)
class GameLogAdmin(admin.ModelAdmin):
    """
    Complete event log for every game
    
    Tracks all significant events:
    - Phase changes (setup → reveal → voting → final)
    - Card reveals (when cards become visible)
    - Player eliminations
    - Voting rounds
    - Game outcomes
    
    Admin Features:
    - Filter by event type (phase_change, card_revealed, player_eliminated, etc.)
    - Search by game ID or message content
    - Sort by date created
    
    Useful for debugging or replaying game history
    """
    list_display = ['game_session', 'event_type', 'player', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['game_session__game_id', 'message']
