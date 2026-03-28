from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    CardType, Card, Catastrophe, Bunker, GameSession, PlayerHand,
    SpecialCondition, PlayerSpecialCard, VoteRound, Vote, GameLog
)

# USER SERIALIZERS

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


# CARD SERIALIZERS

class CardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardType
        fields = ['id', 'card_type']


class CardSerializer(serializers.ModelSerializer):
    card_type_display = serializers.CharField(source='get_card_type_display', read_only=True)
    
    class Meta:
        model = Card
        fields = ['id', 'card_type', 'card_type_display', 'name', 'description', 'points']


# SCENARIO SERIALIZERS

class CatastropheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catastrophe
        fields = ['id', 'name', 'description', 'modifier']


class BunkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bunker
        fields = ['id', 'name', 'description', 'modifier', 'is_positive']


# SPECIAL CONDITION SERIALIZERS

class SpecialConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialCondition
        fields = ['id', 'name', 'description', 'effect']


class PlayerSpecialCardSerializer(serializers.ModelSerializer):
    special_condition = SpecialConditionSerializer(read_only=True)
    
    class Meta:
        model = PlayerSpecialCard
        fields = ['id', 'special_condition', 'used', 'used_at']


# PLAYER HAND SERIALIZERS

class PlayerHandDetailedSerializer(serializers.ModelSerializer):
    player = UserSerializer(read_only=True)
    profession = CardSerializer(read_only=True)
    skill = CardSerializer(read_only=True)
    biological = CardSerializer(read_only=True)
    health = CardSerializer(read_only=True)
    hobby = CardSerializer(read_only=True)
    phobia = CardSerializer(read_only=True)
    baggage = CardSerializer(read_only=True)
    additional_info = CardSerializer(read_only=True)
    special_cards = PlayerSpecialCardSerializer(many=True, read_only=True)
    
    class Meta:
        model = PlayerHand
        fields = [
            'id', 'player', 'profession', 'skill', 'biological', 'health',
            'hobby', 'phobia', 'baggage', 'additional_info', 'profession_revealed',
            'skill_revealed', 'biological_revealed', 'health_revealed', 'hobby_revealed',
            'phobia_revealed', 'baggage_revealed', 'additional_info_revealed',
            'is_eliminated', 'eliminated_round', 'total_score', 'special_cards', 'joined_at'
        ]


class PlayerHandSimpleSerializer(serializers.ModelSerializer):
    """For hiding cards during game"""
    player = UserSerializer(read_only=True)
    
    class Meta:
        model = PlayerHand
        fields = ['id', 'player', 'is_eliminated', 'total_score']


# VOTING SERIALIZERS

class VoteSerializer(serializers.ModelSerializer):
    voter_username = serializers.CharField(source='voter.player.username', read_only=True)
    voted_for_username = serializers.CharField(source='voted_for.player.username', read_only=True)
    
    class Meta:
        model = Vote
        fields = ['id', 'voter', 'voted_for', 'voter_username', 'voted_for_username']


class VoteRoundSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)
    
    class Meta:
        model = VoteRound
        fields = ['id', 'round_number', 'votes']


# GAME LOG SERIALIZER

class GameLogSerializer(serializers.ModelSerializer):
    player_username = serializers.CharField(source='player.username', read_only=True, allow_null=True)
    event_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = GameLog
        fields = ['id', 'event_type', 'event_display', 'player', 'player_username', 'message', 'created_at']


# GAME SESSION SERIALIZERS

class GameSessionDetailedSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    catastrophe = CatastropheSerializer(read_only=True)
    bunker = BunkerSerializer(read_only=True)
    players = PlayerHandDetailedSerializer(many=True, read_only=True)
    vote_rounds = VoteRoundSerializer(many=True, read_only=True)
    logs = GameLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = GameSession
        fields = [
            'id', 'game_id', 'created_by', 'catastrophe', 'bunker', 'current_phase',
            'status', 'base_threshold', 'final_threshold', 'final_score', 'max_players',
            'survivors_needed', 'players', 'vote_rounds', 'logs', 'created_at', 'updated_at'
        ]


class GameSessionSimpleSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    catastrophe = CatastropheSerializer(read_only=True)
    bunker = BunkerSerializer(read_only=True)
    player_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GameSession
        fields = [
            'id', 'game_id', 'created_by', 'catastrophe', 'bunker', 'current_phase',
            'status', 'final_threshold', 'final_score', 'max_players', 'survivors_needed',
            'player_count', 'created_at'
        ]
    
    def get_player_count(self, obj):
        return obj.players.filter(is_eliminated=False).count()


class GameSessionCreateSerializer(serializers.ModelSerializer):
    catastrophe_id = serializers.IntegerField(write_only=True)
    bunker_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = GameSession
        fields = ['game_id', 'max_players', 'catastrophe_id', 'bunker_id']
    
    def create(self, validated_data):
        catastrophe_id = validated_data.pop('catastrophe_id')
        bunker_id = validated_data.pop('bunker_id')
        
        game_session = GameSession.objects.create(
            created_by=self.context['request'].user,
            catastrophe_id=catastrophe_id,
            bunker_id=bunker_id,
            **validated_data
        )
        
        # Calculate survivors needed
        player_count = validated_data['max_players']
        if player_count <= 3:
            game_session.survivors_needed = 2
        elif player_count <= 5:
            game_session.survivors_needed = 3
        elif player_count <= 7:
            game_session.survivors_needed = 4
        elif player_count <= 9:
            game_session.survivors_needed = 5
        elif player_count <= 11:
            game_session.survivors_needed = 6
        else:
            game_session.survivors_needed = 7
        
        game_session.calculate_threshold()
        game_session.save()
        
        return game_session
