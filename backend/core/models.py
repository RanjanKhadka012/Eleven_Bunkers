from django.db import models
from django.contrib.auth.models import User

# CARD DATA MODELS

class CardType(models.Model):
    """Categories of cards"""
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
    """Individual game cards with scoring"""
    card_type = models.ForeignKey(CardType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.points} pts)"
    
    class Meta:
        ordering = ['card_type', '-points']


# GAME SCENARIO MODELS

class Catastrophe(models.Model):
    """Catastrophe scenarios"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    modifier = models.IntegerField()  # Threshold modifier
    
    def __str__(self):
        return f"{self.name} (+{self.modifier})"


class Bunker(models.Model):
    """Bunker conditions"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    modifier = models.IntegerField()  # Can be negative or positive
    is_positive = models.BooleanField(default=False)
    
    def __str__(self):
        sign = "-" if self.modifier < 0 else "+"
        return f"{self.name} ({sign}{abs(self.modifier)})"


# GAME SESSION MODELS

class GameSession(models.Model):
    """Main game session"""
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
    
    base_threshold = models.IntegerField(default=0)
    final_threshold = models.IntegerField(default=0)
    final_score = models.IntegerField(null=True, blank=True)
    
    max_players = models.IntegerField(default=8)
    survivors_needed = models.IntegerField(default=4)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Game {self.game_id} - {self.get_status_display()}"
    
    def calculate_threshold(self):
        """Calculate final threshold based on catastrophe and bunker modifiers"""
        base = self.survivors_needed * 18
        catastrophe_mod = self.catastrophe.modifier if self.catastrophe else 0
        bunker_mod = self.bunker.modifier if self.bunker else 0
        self.base_threshold = base
        self.final_threshold = base + catastrophe_mod + bunker_mod
        return self.final_threshold
    
    def check_survival(self):
        """Check if group survives"""
        if self.final_score is None:
            return None
        return self.final_score >= self.final_threshold


class PlayerHand(models.Model):
    """Player's cards in a game"""
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='players')
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Card assignments (one of each type)
    profession = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='profession_players')
    skill = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='skill_players')
    biological = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='biological_players')
    health = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='health_players')
    hobby = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='hobby_players')
    phobia = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='phobia_players')
    baggage = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='baggage_players')
    additional_info = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL, related_name='additional_info_players')
    
    # Reveal status (track which cards have been revealed)
    profession_revealed = models.BooleanField(default=False)
    skill_revealed = models.BooleanField(default=False)
    biological_revealed = models.BooleanField(default=False)
    health_revealed = models.BooleanField(default=False)
    hobby_revealed = models.BooleanField(default=False)
    phobia_revealed = models.BooleanField(default=False)
    baggage_revealed = models.BooleanField(default=False)
    additional_info_revealed = models.BooleanField(default=False)
    
    # Game state
    is_eliminated = models.BooleanField(default=False)
    eliminated_round = models.IntegerField(null=True, blank=True)
    total_score = models.IntegerField(default=0)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player.username} in {self.game_session.game_id}"
    
    def calculate_score(self):
        """Calculate total score from all cards"""
        score = 0
        for card_field in ['profession', 'skill', 'biological', 'health', 'hobby', 'phobia', 'baggage', 'additional_info']:
            card = getattr(self, card_field)
            if card:
                score += card.points
        self.total_score = score
        return score
    
    def get_all_cards(self):
        """Return all cards as a dictionary"""
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
        """Return reveal status for all cards"""
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
    """Special condition cards that don't count toward scoring"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    effect = models.TextField()  # Description of what it does
    
    def __str__(self):
        return self.name


class PlayerSpecialCard(models.Model):
    """Special condition cards assigned to players"""
    player_hand = models.ForeignKey(PlayerHand, on_delete=models.CASCADE, related_name='special_cards')
    special_condition = models.ForeignKey(SpecialCondition, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.special_condition.name} - {self.player_hand.player.username}"


class VoteRound(models.Model):
    """Tracks voting rounds"""
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='vote_rounds')
    round_number = models.IntegerField()
    
    def __str__(self):
        return f"{self.game_session.game_id} - Round {self.round_number}"


class Vote(models.Model):
    """Individual votes cast"""
    vote_round = models.ForeignKey(VoteRound, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(PlayerHand, on_delete=models.CASCADE, related_name='votes_cast')
    voted_for = models.ForeignKey(PlayerHand, on_delete=models.CASCADE, related_name='votes_received')
    
    def __str__(self):
        return f"{self.voter.player.username} -> {self.voted_for.player.username}"


class GameLog(models.Model):
    """Track game events"""
    EVENT_TYPES = [
        ('phase_change', 'Phase Changed'),
        ('card_revealed', 'Card Revealed'),
        ('player_eliminated', 'Player Eliminated'),
        ('voting_round', 'Voting Round'),
        ('game_ended', 'Game Ended'),
    ]
    
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.game_session.game_id} - {self.get_event_type_display()}"
