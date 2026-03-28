"""
Bunker Game API Views

REST API endpoints for the Bunker game backend. Uses Django REST Framework viewsets
to provide CRUD operations and custom actions for game management.

API Endpoints Summary:
- /cards/ - Read-only access to game cards
- /card-types/ - Read-only list of card type categories
- /catastrophes/ - Read-only list of catastrophe scenarios
- /bunkers/ - Read-only list of bunker conditions (positive and negative)
- /special-conditions/ - Read-only list of special condition cards
- /game-sessions/ - Full game session management (create, join, start, vote, score)
- /text-to-speech/ - Generate audio narration for cards and game events
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
import random
import uuid

from .models import (
    CardType, Card, Catastrophe, Bunker, GameSession, PlayerHand,
    SpecialCondition, PlayerSpecialCard, VoteRound, Vote, GameLog
)
from .serializers import (
    CardTypeSerializer, CardSerializer, CatastropheSerializer, BunkerSerializer,
    GameSessionDetailedSerializer, GameSessionSimpleSerializer, GameSessionCreateSerializer,
    PlayerHandDetailedSerializer, SpecialConditionSerializer, VoteRoundSerializer,
    UserSerializer, GameLogSerializer
)
from .elevenlabs_utils import (
    text_to_speech, get_card_narration, get_player_summary_narration, get_game_announcement
)


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination for list endpoints - returns 10 results per page"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ========================================
# READ-ONLY CARD VIEWSETS
# ========================================

class CardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to game cards
    
    Endpoints:
    - GET /cards/ - List all cards with pagination
    - GET /cards/?card_type=profession - Filter by card type
    - GET /cards/{id}/ - Get single card
    """
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Allow filtering by card_type query parameter"""
        queryset = Card.objects.all()
        card_type = self.request.query_params.get('card_type')
        if card_type:
            queryset = queryset.filter(card_type__card_type=card_type)
        return queryset.order_by('card_type', '-points')


class CardTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to card type categories
    
    Endpoints:
    - GET /card-types/ - List all 8 card types
    - GET /card-types/{id}/ - Get single card type
    """
    queryset = CardType.objects.all()
    serializer_class = CardTypeSerializer


# ========================================
# READ-ONLY SCENARIO VIEWSETS
# ========================================

class CatastropheViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to catastrophe scenarios
    
    Endpoints:
    - GET /catastrophes/ - List all 7 catastrophe scenarios
    - GET /catastrophes/{id}/ - Get single catastrophe
    """
    queryset = Catastrophe.objects.all()
    serializer_class = CatastropheSerializer


class BunkerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to bunker conditions
    
    Endpoints:
    - GET /bunkers/ - List all bunker conditions
    - GET /bunkers/positive/ - Get positive conditions (advantage)
    - GET /bunkers/negative/ - Get negative conditions (disadvantage)
    - GET /bunkers/{id}/ - Get single condition
    """
    queryset = Bunker.objects.all()
    serializer_class = BunkerSerializer
    
    @action(detail=False, methods=['get'])
    def positive(self, request):
        """Get positive bunker conditions (make survival easier)"""
        queryset = self.get_queryset().filter(is_positive=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def negative(self, request):
        """Get negative bunker conditions (make survival harder)"""
        queryset = self.get_queryset().filter(is_positive=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SpecialConditionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to special condition cards
    
    Endpoints:
    - GET /special-conditions/ - List all special conditions
    - GET /special-conditions/{id}/ - Get single special condition
    """
    queryset = SpecialCondition.objects.all()
    serializer_class = SpecialConditionSerializer


# ========================================
# MAIN GAME SESSION VIEWSET
# ========================================

class GameSessionViewSet(viewsets.ModelViewSet):
    """
    Full game session management
    
    Requires authentication. Users can only see games they created or joined.
    
    Main Endpoints (REST):
    - POST /game-sessions/ - Create new game session
    - GET /game-sessions/ - List your games
    - GET /game-sessions/{id}/ - Get game details
    - PATCH /game-sessions/{id}/ - Update game
    - DELETE /game-sessions/{id}/ - Delete game
    
    Game Action Endpoints:
    - POST /game-sessions/{id}/join_game/ - Player joins game
    - POST /game-sessions/{id}/start_game/ - Host starts game (deals cards)
    - POST /game-sessions/{id}/reveal_card/ - Reveal a card
    - POST /game-sessions/{id}/cast_vote/ - Vote to eliminate player
    - POST /game-sessions/{id}/eliminate_player/ - Eliminate voted player
    - POST /game-sessions/{id}/final_scoring/ - Calculate final score
    - GET /game-sessions/{id}/game_status/ - Get current game status
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Only return games the user created or joined"""
        return GameSession.objects.filter(
            Q(created_by=self.request.user) | Q(players__player=self.request.user)
        ).distinct()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return GameSessionCreateSerializer
        elif self.action == 'retrieve':
            return GameSessionDetailedSerializer
        else:
            return GameSessionSimpleSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new game session
        POST /game-sessions/
        
        Creates a new game and adds the creator as the first player (host)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game_session = serializer.save()
        
        # Add game creator as first player (host)
        PlayerHand.objects.create(game_session=game_session, player=request.user)
        
        return Response(
            GameSessionDetailedSerializer(game_session).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def join_game(self, request, pk=None):
        """
        Join an existing game
        POST /game-sessions/{id}/join_game/
        
        Validation:
        - Player not already in game
        - Game is not full (max 8 players)
        - Game hasn't started yet
        """
        game_session = self.get_object()
        
        # Check if player already joined
        if PlayerHand.objects.filter(game_session=game_session, player=request.user).exists():
            return Response(
                {"detail": "Already joined this game"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if game is full
        player_count = game_session.players.count()
        if player_count >= game_session.max_players:
            return Response(
                {"detail": "Game is full"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add player to game
        player_hand = PlayerHand.objects.create(game_session=game_session, player=request.user)
        
        # Log event
        GameLog.objects.create(
            game_session=game_session,
            event_type='phase_change',
            player=request.user,
            message=f"{request.user.username} joined the game"
        )
        
        return Response(
            PlayerHandDetailedSerializer(player_hand).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def start_game(self, request, pk=None):
        """
        Start the game and deal cards to all players
        POST /game-sessions/{id}/start_game/
        
        Only the host (game creator) can start the game.
        Transitions game from 'setup' phase to 'reveal' phase.
        
        Card Dealing:
        - Each player gets 1 random card of each type (8 total)
        - Each player gets 2 random special condition cards
        - Each special condition card is non-scoring (don't count toward survival)
        """
        game_session = self.get_object()
        
        # Validation: only host can start
        if game_session.created_by != request.user:
            return Response(
                {"detail": "Only game creator can start the game"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validation: can't start if already started or not in setup
        if game_session.current_phase != 'setup':
            return Response(
                {"detail": "Game already started"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deal cards to each player
        players = game_session.players.all()
        card_types = CardType.objects.all()
        
        for player_hand in players:
            # Assign one random card to each card type slot
            for card_type in card_types:
                cards = Card.objects.filter(card_type=card_type)
                if cards.exists():
                    random_card = cards.order_by('?').first()
                    setattr(player_hand, card_type.card_type, random_card)
            
            # Give player 2 special condition cards (non-scoring)
            special_cards = SpecialCondition.objects.order_by('?')[:2]
            player_hand.save()
            
            for special_card in special_cards:
                PlayerSpecialCard.objects.create(
                    player_hand=player_hand,
                    special_condition=special_card
                )
        
        # Update game to reveal phase
        game_session.current_phase = 'reveal'
        game_session.save()
        
        # Log event
        GameLog.objects.create(
            game_session=game_session,
            event_type='phase_change',
            player=request.user,
            message="Game started! Cards dealt."
        )
        
        return Response(
            GameSessionDetailedSerializer(game_session).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reveal_card(self, request, pk=None):
        """
        Reveal one of the player's cards to the group
        POST /game-sessions/{id}/reveal_card/
        
        Request body: {"card_type": "profession"}
        
        During reveal rounds, players reveal one card type at a time
        so other players can see their attributes and discuss who to eliminate.
        """
        game_session = self.get_object()
        card_type = request.data.get('card_type')
        
        # Get requesting player's hand in this game
        player_hand = get_object_or_404(
            PlayerHand,
            game_session=game_session,
            player=request.user
        )
        
        # Validate card type is valid
        valid_types = ['profession', 'skill', 'biological', 'health', 'hobby', 'phobia', 'baggage', 'additional_info']
        if not card_type or card_type not in valid_types:
            return Response(
                {"detail": "Invalid card type"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark card as revealed in database
        setattr(player_hand, f"{card_type}_revealed", True)
        player_hand.save()
        
        # Log event
        card = getattr(player_hand, card_type)
        GameLog.objects.create(
            game_session=game_session,
            event_type='card_revealed',
            player=request.user,
            message=f"{request.user.username} revealed {card_type}: {card.name}"
        )
        
        return Response(
            PlayerHandDetailedSerializer(player_hand).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cast_vote(self, request, pk=None):
        """
        Cast a vote to eliminate another player
        POST /game-sessions/{id}/cast_vote/
        
        Request body: {"voted_for_id": <player_hand_id>}
        
        During voting phase, players vote on who to eliminate.
        A player cannot vote for themselves.
        If a player changes their vote, it updates the previous vote.
        """
        game_session = self.get_object()
        voted_for_id = request.data.get('voted_for_id')
        
        # Get voting player's hand
        voter = get_object_or_404(
            PlayerHand,
            game_session=game_session,
            player=request.user
        )
        
        # Get the player being voted for
        voted_for = get_object_or_404(
            PlayerHand,
            game_session=game_session,
            id=voted_for_id
        )
        
        # Validation: can't vote for yourself
        if voted_for.player == request.user:
            return Response(
                {"detail": "Cannot vote for yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create a vote round (round 1 unless specified)
        vote_round, _ = VoteRound.objects.get_or_create(
            game_session=game_session,
            round_number=1
        )
        
        # Create or update vote (allows changing vote before elimination)
        Vote.objects.update_or_create(
            vote_round=vote_round,
            voter=voter,
            defaults={'voted_for': voted_for}
        )
        
        return Response(
            VoteRoundSerializer(vote_round).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def eliminate_player(self, request, pk=None):
        """
        Eliminate a player (usually the one with most votes)
        POST /game-sessions/{id}/eliminate_player/
        
        Request body: {"player_id": <player_hand_id>, "round_number": 1}
        
        Only the host should call this after vote counting.
        Marks the player as eliminated and records which voting round.
        """
        game_session = self.get_object()
        player_id = request.data.get('player_id')
        round_number = request.data.get('round_number', 1)
        
        # Get player to eliminate
        player_hand = get_object_or_404(PlayerHand, id=player_id, game_session=game_session)
        
        # Mark as eliminated
        player_hand.is_eliminated = True
        player_hand.eliminated_round = round_number
        player_hand.save()
        
        # Log event
        GameLog.objects.create(
            game_session=game_session,
            event_type='player_eliminated',
            player=player_hand.player,
            message=f"{player_hand.player.username} was eliminated"
        )
        
        return Response(
            {"detail": "Player eliminated"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def final_scoring(self, request, pk=None):
        """
        Calculate final score and determine if team survives
        POST /game-sessions/{id}/final_scoring/
        
        Only the host (game creator) can finalize scoring.
        
        Survival Calculation:
        - Sum total points of all remaining (non-eliminated) players' scoring cards
        - Compare to final_threshold = (survivors_needed × 18) + catastrophe_mod + bunker_mod
        - If final_score >= final_threshold: team survives
        - Else: team fails
        """
        game_session = self.get_object()
        
        # Validation: only host can finalize
        if game_session.created_by != request.user:
            return Response(
                {"detail": "Only game creator can finalize scoring"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate total score from remaining players
        total_score = 0
        survivors = game_session.players.filter(is_eliminated=False)
        
        for player_hand in survivors:
            player_hand.calculate_score()
            player_hand.save()
            total_score += player_hand.total_score
        
        # Update game with final score and phase
        game_session.final_score = total_score
        game_session.current_phase = 'final_scoring'
        
        # Determine survival
        survived = game_session.check_survival()
        if survived:
            game_session.status = 'completed'
        else:
            game_session.status = 'failed'
        
        game_session.save()
        
        # Log final event
        result = "Humanity survived!" if survived else "Humanity failed!"
        GameLog.objects.create(
            game_session=game_session,
            event_type='game_ended',
            player=request.user,
            message=f"Final Score: {total_score} / {game_session.final_threshold}. {result}"
        )
        
        return Response(
            GameSessionDetailedSerializer(game_session).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def game_status(self, request, pk=None):
        """
        Get current game status
        GET /game-sessions/{id}/game_status/
        
        Returns quick summary: phase, number of players, eliminated count,
        threshold needed, current score so far.
        """
        game_session = self.get_object()
        
        return Response({
            'game_id': game_session.game_id,
            'phase': game_session.current_phase,
            'status': game_session.status,
            'players': game_session.players.count(),
            'eliminated': game_session.players.filter(is_eliminated=True).count(),
            'final_threshold': game_session.final_threshold,
            'final_score': game_session.final_score,
            'catastrophe': CatastropheSerializer(game_session.catastrophe).data,
            'bunker': BunkerSerializer(game_session.bunker).data,
        })


# ========================================
# TEXT-TO-SPEECH VIEWSET
# ========================================

class TextToSpeechViewSet(viewsets.ViewSet):
    """
    Generate audio narration for cards and game events using ElevenLabs API
    
    Endpoints:
    - POST /text-to-speech/card_narration/ - Narrate a card
    - POST /text-to-speech/player_summary/ - Narrate a player's card summary
    - POST /text-to-speech/game_announcement/ - Narrate game start
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def card_narration(self, request):
        """
        Generate narration for a single card
        POST /text-to-speech/card_narration/
        
        Request body: {"card_id": <id>, "voice_id": "21m00Tcm4TlvDq8ikWAM"}
        
        Returns narration text and base64-encoded audio MP3
        """
        card_id = request.data.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        
        # Generate narration text based on card content
        narration = get_card_narration(card)
        
        # Convert text to speech using ElevenLabs API
        audio = text_to_speech(narration, voice_id=request.data.get('voice_id', '21m00Tcm4TlvDq8ikWAM'))
        
        return Response({
            'narration': narration,
            'audio': audio
        })
    
    @action(detail=False, methods=['post'])
    def player_summary(self, request):
        """
        Generate narration summarizing a player's cards
        POST /text-to-speech/player_summary/
        
        Request body: {"player_hand_id": <id>, "voice_id": "21m00Tcm4TlvDq8ikWAM"}
        
        Summarizes all 8 cards and special conditions for a player
        """
        player_hand_id = request.data.get('player_hand_id')
        player_hand = get_object_or_404(PlayerHand, id=player_hand_id)
        
        # Generate narration text summarizing player's cards
        narration = get_player_summary_narration(player_hand)
        
        # Convert to audio
        audio = text_to_speech(narration, voice_id=request.data.get('voice_id', '21m00Tcm4TlvDq8ikWAM'))
        
        return Response({
            'narration': narration,
            'audio': audio
        })
    
    @action(detail=False, methods=['post'])
    def game_announcement(self, request):
        """
        Generate game start announcement
        POST /text-to-speech/game_announcement/
        
        Request body: {"game_session_id": <id>, "voice_id": "21m00Tcm4TlvDq8ikWAM"}
        
        Generates dramatic announcement of the catastrophe and bunker scenario
        """
        game_session_id = request.data.get('game_session_id')
        game_session = get_object_or_404(GameSession, id=game_session_id)
        
        # Generate dramatic announcement text
        announcement = get_game_announcement(game_session)
        
        # Convert to audio
        audio = text_to_speech(announcement, voice_id=request.data.get('voice_id', '21m00Tcm4TlvDq8ikWAM'))
        
        return Response({
            'announcement': announcement,
            'audio': audio
        })
