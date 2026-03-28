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
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# CARD VIEWSETS

class CardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Card.objects.all()
        card_type = self.request.query_params.get('card_type')
        if card_type:
            queryset = queryset.filter(card_type__card_type=card_type)
        return queryset.order_by('card_type', '-points')


class CardTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CardType.objects.all()
    serializer_class = CardTypeSerializer


# SCENARIO VIEWSETS

class CatastropheViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Catastrophe.objects.all()
    serializer_class = CatastropheSerializer


class BunkerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bunker.objects.all()
    serializer_class = BunkerSerializer
    
    @action(detail=False, methods=['get'])
    def positive(self, request):
        """Get positive bunker conditions"""
        queryset = self.get_queryset().filter(is_positive=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def negative(self, request):
        """Get negative bunker conditions"""
        queryset = self.get_queryset().filter(is_positive=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SpecialConditionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SpecialCondition.objects.all()
    serializer_class = SpecialConditionSerializer


# GAME SESSION VIEWSET

class GameSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return GameSession.objects.filter(
            Q(created_by=self.request.user) | Q(players__player=self.request.user)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GameSessionCreateSerializer
        elif self.action == 'retrieve':
            return GameSessionDetailedSerializer
        else:
            return GameSessionSimpleSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new game session"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game_session = serializer.save()
        
        # Add game creator as first player
        PlayerHand.objects.create(game_session=game_session, player=request.user)
        
        return Response(
            GameSessionDetailedSerializer(game_session).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def join_game(self, request, pk=None):
        """Join an existing game"""
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
        """Start the game and deal cards"""
        game_session = self.get_object()
        
        if game_session.created_by != request.user:
            return Response(
                {"detail": "Only game creator can start the game"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if game_session.current_phase != 'setup':
            return Response(
                {"detail": "Game already started"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deal cards to each player
        players = game_session.players.all()
        card_types = CardType.objects.all()
        
        for player_hand in players:
            for card_type in card_types:
                # Get random card of this type
                cards = Card.objects.filter(card_type=card_type)
                if cards.exists():
                    random_card = cards.order_by('?').first()
                    setattr(player_hand, card_type.card_type, random_card)
            
            # Add 2 special condition cards
            special_cards = SpecialCondition.objects.order_by('?')[:2]
            player_hand.save()
            
            for special_card in special_cards:
                PlayerSpecialCard.objects.create(
                    player_hand=player_hand,
                    special_condition=special_card
                )
        
        # Update game state
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
        """Reveal a card for the current player"""
        game_session = self.get_object()
        card_type = request.data.get('card_type')
        
        player_hand = get_object_or_404(
            PlayerHand,
            game_session=game_session,
            player=request.user
        )
        
        if not card_type or card_type not in ['profession', 'skill', 'biological', 'health', 'hobby', 'phobia', 'baggage', 'additional_info']:
            return Response(
                {"detail": "Invalid card type"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark card as revealed
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
        """Cast a vote to eliminate a player"""
        game_session = self.get_object()
        voted_for_id = request.data.get('voted_for_id')
        
        voter = get_object_or_404(
            PlayerHand,
            game_session=game_session,
            player=request.user
        )
        
        voted_for = get_object_or_404(
            PlayerHand,
            game_session=game_session,
            id=voted_for_id
        )
        
        if voted_for.player == request.user:
            return Response(
                {"detail": "Cannot vote for yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create vote round
        vote_round, _ = VoteRound.objects.get_or_create(
            game_session=game_session,
            round_number=1
        )
        
        # Create vote
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
        """Eliminate a player based on voting"""
        game_session = self.get_object()
        player_id = request.data.get('player_id')
        round_number = request.data.get('round_number', 1)
        
        player_hand = get_object_or_404(PlayerHand, id=player_id, game_session=game_session)
        
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
        """Calculate final score and determine survival"""
        game_session = self.get_object()
        
        if game_session.created_by != request.user:
            return Response(
                {"detail": "Only game creator can finalize scoring"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate total score
        total_score = 0
        survivors = game_session.players.filter(is_eliminated=False)
        
        for player_hand in survivors:
            player_hand.calculate_score()
            player_hand.save()
            total_score += player_hand.total_score
        
        game_session.final_score = total_score
        game_session.current_phase = 'final_scoring'
        
        # Determine survival
        survived = game_session.check_survival()
        if survived:
            game_session.status = 'completed'
        else:
            game_session.status = 'failed'
        
        game_session.save()
        
        # Log event
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
        """Get current game status"""
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


# TEXT-TO-SPEECH VIEWSETS

class TextToSpeechViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def card_narration(self, request):
        """Generate narration for a card"""
        card_id = request.data.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        
        narration = get_card_narration(card)
        audio = text_to_speech(narration, voice_id=request.data.get('voice_id', '21m00Tcm4TlvDq8ikWAM'))
        
        return Response({
            'narration': narration,
            'audio': audio
        })
    
    @action(detail=False, methods=['post'])
    def player_summary(self, request):
        """Generate narration for player summary"""
        player_hand_id = request.data.get('player_hand_id')
        player_hand = get_object_or_404(PlayerHand, id=player_hand_id)
        
        narration = get_player_summary_narration(player_hand)
        audio = text_to_speech(narration, voice_id=request.data.get('voice_id', '21m00Tcm4TlvDq8ikWAM'))
        
        return Response({
            'narration': narration,
            'audio': audio
        })
    
    @action(detail=False, methods=['post'])
    def game_announcement(self, request):
        """Generate narration for game start"""
        game_session_id = request.data.get('game_session_id')
        game_session = get_object_or_404(GameSession, id=game_session_id)
        
        announcement = get_game_announcement(game_session)
        audio = text_to_speech(announcement, voice_id=request.data.get('voice_id', '21m00Tcm4TlvDq8ikWAM'))
        
        return Response({
            'announcement': announcement,
            'audio': audio
        })
