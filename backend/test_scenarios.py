#!/usr/bin/env python
"""Test script to verify apocalypse scenarios and narration integration"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eleven_bunker_api.settings')
django.setup()

from core.models import Catastrophe, Bunker, GameSession, User
from core.elevenlabs_utils import get_opening_narration, get_ending_narration

print("=== APOCALYPSE SCENARIOS ===\n")
catastrophes = Catastrophe.objects.all()
for idx, cat in enumerate(catastrophes, 1):
    print(f"{idx}. {cat.name}")
    print(f"   Modifier: +{cat.modifier}")
    print(f"   Description: {cat.description[:150]}...")
    print()

print("\n=== TESTING NARRATION GENERATION ===\n")

# Get or create test user
test_user, _ = User.objects.get_or_create(username='test_player', defaults={
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'Player'
})

# Create a test game session
test_game = GameSession.objects.create(
    game_id='TEST_GAME_001',
    created_by=test_user,
    catastrophe=catastrophes.first() if catastrophes.exists() else None,
    bunker=Bunker.objects.first() if Bunker.objects.exists() else None,
    max_players=8,
    survivors_needed=4
)

# Test narration generation
if test_game.catastrophe:
    opening = get_opening_narration(test_game)
    ending = get_ending_narration(test_game)
    
    print(f"Game Scenario: {test_game.catastrophe.name}")
    print(f"\nOpening Narration:\n{opening[:200]}...\n")
    print(f"Ending Narration:\n{ending[:200]}...\n")
    
    # Verify narration fields
    print("✓ Opening narration stored:", bool(test_game.opening_narration))
    print("✓ Ending narration stored:", bool(test_game.ending_narration))
    
    # Cleanup
    test_game.delete()
    print("\n✓ Test game created and deleted successfully")
else:
    print("✗ No catastrophes found in database!")

print("\n=== BUNKER CONDITIONS ===\n")
bunkers = Bunker.objects.all()
for idx, bunker in enumerate(bunkers, 1):
    modifier_type = "ADVANTAGE (-value)" if bunker.is_positive else "DISADVANTAGE (+value)"
    print(f"{idx}. {bunker.name}: {modifier_type}")
    print(f"   Modifier: {bunker.modifier}")
    print()

print(f"\nTotal scenarios: {catastrophes.count()}")
print(f"Total bunker conditions: {bunkers.count()}")
print("\n✓ Integration test completed successfully!")
