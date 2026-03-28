from django.contrib import admin
from .models import (
    CardType, Card, Catastrophe, Bunker, GameSession, PlayerHand,
    SpecialCondition, PlayerSpecialCard, VoteRound, Vote, GameLog
)

# Register models

@admin.register(CardType)
class CardTypeAdmin(admin.ModelAdmin):
    list_display = ['card_type']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['name', 'card_type', 'points']
    list_filter = ['card_type', 'points']
    search_fields = ['name']


@admin.register(Catastrophe)
class CatastropheAdmin(admin.ModelAdmin):
    list_display = ['name', 'modifier']


@admin.register(Bunker)
class BunkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'modifier', 'is_positive']
    list_filter = ['is_positive']


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'created_by', 'current_phase', 'status', 'final_score', 'final_threshold']
    list_filter = ['current_phase', 'status', 'created_at']
    search_fields = ['game_id', 'created_by__username']


@admin.register(PlayerHand)
class PlayerHandAdmin(admin.ModelAdmin):
    list_display = ['player', 'game_session', 'is_eliminated', 'total_score']
    list_filter = ['is_eliminated', 'game_session']
    search_fields = ['player__username']


@admin.register(SpecialCondition)
class SpecialConditionAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(PlayerSpecialCard)
class PlayerSpecialCardAdmin(admin.ModelAdmin):
    list_display = ['player_hand', 'special_condition', 'used']
    list_filter = ['used']


@admin.register(VoteRound)
class VoteRoundAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'round_number']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['vote_round', 'voter', 'voted_for']


@admin.register(GameLog)
class GameLogAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'event_type', 'player', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['game_session__game_id', 'message']
