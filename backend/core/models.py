"""
Bunker Game Database Models

Database schema for the Bunker social survival game

Card Flow:
- 8 card types: profession, skill, biological, health, hobby, phobia, baggage, additional_info
- Each card has points (-8 to +12 range)
- During setup, each player is dealt 8 cards (one of each type)
- 2 special condition cards per player (non-scoring)

Scoring System:
- Base threshold = survivors_needed × 18
- Final threshold = base + catastrophe_modifier + bunker_modifier
- Team survives if: total_score >= final_threshold

Game Flow:
1. Setup: Create session, assign catastrophe/bunker, deal cards
2. Reveal Rounds: Players reveal cards one at a time
3. Voting: Players vote on who to eliminate
4. Final Scoring: Calculate group score and check survival
5. Completed: Game ends
"""

from django.db import models
from django.contrib.auth.models import User


# ========================================
# CARD DATA MODELS
# ========================================

class CardType(models.Model):
    """
    Card type categories - defines the 8 card slots each player has
    Examples: Profession ("Doctor"), Skill ("Negotiation"), Phobia ("Spiders"), etc.
    """
    TYPE_CHOICES = [
        ('profession', 'Profession'),
        ('skill', 'Skill'),
        ('biological', 'Biological'),
        ('health', 'Health'),
        ('hobby', 'Hobby'),
        ('phobia', 'Phobia'),
        ('baggage', 'Baggage'),
        ('additional_info', 'Additional Info'),
    ]
    card_type = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_card_type_display()


class Card(models.Model):
    """
    Individual game cards with scoring values
    Each card is a specific instance within a CardType
    Points range from -8 (very negative) to +12 (very positive)
    
    Examples:
    - Profession "Doctor": +12 points (valuable for survival)
    - Phobia "Claustrophobia": -4 points (liability in a bunker)
    - Hobby "Gardening": +6 points (useful for food production)
    """
    card_type = models.ForeignKey(CardType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.points} pts)"
    
    class Meta:
        ordering = ['card_type', '-points']


# ========================================
# GAME SCENARIO MODELS
# ========================================

class Catastrophe(models.Model):
    """
    Catastrophe scenarios that define the survival challenge
    Each game picks one catastrophe to determine the difficulty modifier
    
    Examples:
    - Nuclear War: +10 modifier (very difficult scenario)
    - Pandemic: +8 modifier (difficult)
    - Climate Change: +5 modifier (moderate)
    
    Higher modifier = higher threshold needed to survive
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    modifier = models.IntegerField()  # Added to threshold calculation
    
    def __str__(self):
        return f"{self.name} (+{self.modifier})"


class Bunker(models.Model):
    """
    Bunker conditions that affect survival difficulty
    Each game picks one positive and one negative condition
    
    Positive conditions (good bunkers):
    - Fully Stocked: -6 modifier (people easily fed, lowers threshold)
    - Medical Facility: -4 modifier (health maintained)
    
    Negative conditions (poor bunkers):
    - Limited Food: +4 modifier (raises threshold)
    - No Electricity: +3 modifier (difficult living conditions)
    
    Negative modifier = easier to survive (good bunker)
    Positive modifier = harder to survive (poor bunker)
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    modifier = models.IntegerField()
    is_positive = models.BooleanField(default=False)  # True = disadvantage (raises threshold)
    
    def __str__(self):
        sign = "-" if self.modifier < 0 else "+"
        return f"{self.name} ({sign}{abs(self.modifier)})"


# ========================================
# GAME SESSION MODELS
# ========================================

class GameSession(models.Model):
    """
    Represents one complete game session
    Tracks all game progress from setup through final scoring
    
    Threshold Calculation:
    final_threshold = (survivors_needed × 18) + catastrophe_mod + bunker_mod
    
    Example with 4 survivors needed:
    - Base: 4 × 18 = 72 points
    - With Nuclear War catastrophe: +10 = 82
    - With Poor Bunker condition: +5 = 87
    - Final threshold = 87 (group must score ≥87 to survive)
    """
    PHASE_CHOICES = [
        ('setup', 'Setup'),
        ('reveal', 'Reveal Rounds'),
        ('voting', 'Voting'),
        ('final_scoring', 'Final Scoring'),
        ('completed', 'Completed'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    game_id = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_games')
    catastrophe = models.ForeignKey(Catastrophe, on_delete=models.SET_NULL, null=True, blank=True)
    bunker = models.ForeignKey(Bunker, on_delete=models.SET_NULL, null=True, blank=True)
    
    current_phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='setup')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    opening_narration = models.TextField(blank=True, help_text="Dramatic opening narration text read at game start")
    ending_narration = models.TextField(blank=True, help_text="Reflective ending narration text read at game conclusion")
    narration_audio_url = models.URLField(blank=True, help_text="URL to generated opening narration audio file")
    
    base_threshold = models.IntegerField(default=0)  # survivors_needed × 18
    final_threshold = models.IntegerField(default=0)  # base + modifiers
    final_score = models.IntegerField(null=True, blank=True)  # Total score of remaining players
    
    max_players = models.IntegerField(default=8)
    survivors_needed = models.IntegerField(default=4)  # How many players remain after voting
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Game {self.game_id} - {self.get_status_display()}"
    
    def calculate_threshold(self):
        """
        Calculate final survival threshold based on catastrophe and bunker
        
        Formula: (survivors_needed × 18) + catastrophe_mod + bunker_mod
        
        This threshold determines what minimum score the final team must achieve
        """
        base = self.survivors_needed * 18
        catastrophe_mod = self.catastrophe.modifier if self.catastrophe else 0
        bunker_mod = self.bunker.modifier if self.bunker else 0
        self.base_threshold = base
        self.final_threshold = base + catastrophe_mod + bunker_mod
        return self.final_threshold
    
    def check_survival(self):
        """
        Check if group survives by comparing final score to threshold
        Returns: True (survives), False (doesn't survive), or None (score not calculated yet)
        """
        if self.final_score is None:
            return None
        return self.final_score >= self.final_threshold


class PlayerHand(models.Model):
    """
    One player's cards and progress in a game session
    Each player starts with 8 cards (one per type) plus 2 special condition cards
    
    Card Fields:
    - profession, skill, biological, health, hobby, phobia, baggage, additional_info
    
    Reveal Tracking:
    - player knows their own cards
    - other players see cards as they're revealed during reveal rounds
    - voting happens after certain cards are revealed
    """
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='players')
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # ===== PLAYER'S CARDS (8 total - one per type) =====
    profession = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='profession_players')
    skill = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='skill_players')
    biological = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='biological_players')
    health = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='health_players')
    hobby = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='hobby_players')
    phobia = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='phobia_players')
    baggage = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='baggage_players')
    additional_info = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='additional_info_players')
    
    # ===== REVEAL STATUS =====
    # Tracks which cards have been revealed to the group
    profession_revealed = models.BooleanField(default=False)
    skill_revealed = models.BooleanField(default=False)
    biological_revealed = models.BooleanField(default=False)
    health_revealed = models.BooleanField(default=False)
    hobby_revealed = models.BooleanField(default=False)
    phobia_revealed = models.BooleanField(default=False)
    baggage_revealed = models.BooleanField(default=False)
    additional_info_revealed = models.BooleanField(default=False)
    
    # ===== GAME STATE =====
    is_eliminated = models.BooleanField(default=False)  # Set to True if voted out
    eliminated_round = models.IntegerField(null=True, blank=True)  # Which voting round
    total_score = models.IntegerField(default=0)  # Sum of all card points (only counts non-special cards)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player.username} in {self.game_session.game_id}"
    
    def calculate_score(self):
        """
        Calculate total score from all 8 cards
        Special condition cards do NOT contribute to this score
        
        Score is used to determine if team survives
        Higher score = more likely to survive the catastrophe
        """
        score = 0
        for card_field in ['profession', 'skill', 'biological', 'health', 'hobby', 'phobia', 'baggage', 'additional_info']:
            card = getattr(self, card_field)
            if card:
                score += card.points
        self.total_score = score
        return score
    
    def get_all_cards(self):
        """Return all 8 cards as a dictionary mapping card type -> Card object"""
        return {
            'profession': self.profession,
            'skill': self.skill,
            'biological': self.biological,
            'health': self.health,
            'hobby': self.hobby,
            'phobia': self.phobia,
            'baggage': self.baggage,
            'additional_info': self.additional_info,
        }
    
    def get_reveal_status(self):
        """Return reveal status mapping for all 8 cards (type -> boolean)"""
        return {
            'profession': self.profession_revealed,
            'skill': self.skill_revealed,
            'biological': self.biological_revealed,
            'health': self.health_revealed,
            'hobby': self.hobby_revealed,
            'phobia': self.phobia_revealed,
            'baggage': self.baggage_revealed,
            'additional_info': self.additional_info_revealed,
        }


class SpecialCondition(models.Model):
    """
    Special condition cards - non-scoring strategic cards
    Every player gets 2 special condition cards (don't count toward survival score)
    
    Examples:
    - "Insider": You know something about another player
    - "Saboteur": You can secretly harm another player's card
    - "Doctor": You can save someone from elimination
    
    These create social/political gameplay without affecting the score calculation
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    effect = models.TextField()  # What the special card does mechanically
    
    def __str__(self):
        return self.name


class PlayerSpecialCard(models.Model):
    """
    Tracks special condition cards assigned to a player
    Stores whether the card has been used and when
    Each player starts with 2 of these
    """
    player_hand = models.ForeignKey(PlayerHand, on_delete=models.CASCADE, related_name='special_cards')
    special_condition = models.ForeignKey(SpecialCondition, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)  # Set to True when player uses the card
    used_at = models.DateTimeField(null=True, blank=True)  # When was it used
    
    def __str__(self):
        return f"{self.special_condition.name} - {self.player_hand.player.username}"


# ========================================
# VOTING MODELS
# ========================================

class VoteRound(models.Model):
    """
    Represents one round of voting to eliminate a player
    Multiple voting rounds happen during the voting phase
    """
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='vote_rounds')
    round_number = models.IntegerField()  # 1st elimination vote, 2nd, etc.
    
    def __str__(self):
        return f"{self.game_session.game_id} - Round {self.round_number}"


class Vote(models.Model):
    """
    One individual vote from a voter -> voted_for
    Aggregating these votes determines who gets eliminated each round
    """
    vote_round = models.ForeignKey(VoteRound, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(PlayerHand, on_delete=models.CASCADE, related_name='votes_cast')
    voted_for = models.ForeignKey(PlayerHand, on_delete=models.CASCADE, related_name='votes_received')
    
    def __str__(self):
        return f"{self.voter.player.username} -> {self.voted_for.player.username}"


# ========================================
# GAME LOG
# ========================================

class GameLog(models.Model):
    """
    Event log tracking all significant game events
    Helps replay game history and debug issues
    """
    EVENT_TYPES = [
        ('phase_change', 'Phase Changed'),
        ('card_revealed', 'Card Revealed'),
        ('player_eliminated', 'Player Eliminated'),
        ('voting_round', 'Voting Round'),
        ('game_ended', 'Game Ended'),
    ]
    
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Who the event concerns
    message = models.TextField()  # Description of what happened
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.game_session.game_id} - {self.get_event_type_display()}"
