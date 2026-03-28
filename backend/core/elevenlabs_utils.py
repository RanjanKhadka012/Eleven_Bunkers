"""
ElevenLabs Text-to-Speech (TTS) Integration for Bunker Game

Provides utilities to convert game content to realistic audio narration.
Enhances gameplay by reading cards, player summaries, and game announcements aloud.

API Key: Stored in ELEVENLABS_API_KEY environment variable
Model: eleven_monolingual_v1 (optimized for English)
Default Voice: Rachel (ID: 21m00Tcm4TlvDq8ikWAM)

Usage:
    from .elevenlabs_utils import text_to_speech, get_card_narration
    
    # Generate narration for a card
    narration = get_card_narration(card)
    audio = text_to_speech(narration)  # returns bytes
    
    # Listen to voices available
    voices = available_voices()
"""

import os
from django.conf import settings
import logging

try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize ElevenLabs SDK client with API key from environment
# Will be None if elevenlabs package is not installed
if ELEVENLABS_AVAILABLE:
    client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
else:
    client = None


def text_to_speech(text, voice_id='21m00Tcm4TlvDq8ikWAM', output_path=None):
    """
    Convert text to speech using ElevenLabs API
    
    Args:
        text (str): Text content to convert to speech
        voice_id (str): ElevenLabs voice ID (default: Rachel voice)
        output_path (str, optional): Path to save audio file. If None, returns audio bytes
    
    Returns:
        bytes or str: Audio bytes if output_path is None, otherwise file path
    
    Raises:
        Exception: If API call fails or elevenlabs not installed
    
    Example:
        >>> narration = "Doctor. Expert in medicine and surgery."
        >>> audio_bytes = text_to_speech(narration)
        >>> # Save to file
        >>> text_to_speech(narration, output_path="card_audio.mp3")
    """
    if not ELEVENLABS_AVAILABLE or client is None:
        raise ImportError("ElevenLabs package not installed. Install with: pip install elevenlabs")
    
    try:
        # Call ElevenLabs API to generate speech
        audio = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_monolingual_v1"  # Optimized for English
        )
        
        # Optionally save to file
        if output_path:
            client.save(audio, output_path)
            return output_path
        else:
            # Return raw audio bytes for streaming or encoding
            return audio
    
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise


def get_card_narration(card):
    """
    Generate narration text for a single card
    
    Combines card name and description into a coherent narration.
    Used before text_to_speech() to generate audio playback.
    
    Args:
        card (Card): Card object with name and description attributes
    
    Returns:
        str: Narration text suitable for speech synthesis
    
    Example:
        >>> card = Card.objects.get(name="Doctor")
        >>> narration = get_card_narration(card)
        >>> print(narration)
        "Doctor. A skilled medical professional."
    """
    narration = f"{card.name}. {card.description if card.description else ''}"
    return narration.strip()


def get_player_summary_narration(player_hand):
    """
    Generate narration summarizing a player's revealed cards
    
    Creates a narrative summary of all cards that have been revealed
    for a specific player. Useful for reading aloud character profiles.
    
    Args:
        player_hand (PlayerHand): Player's hand object containing all cards and reveal status
    
    Returns:
        str: Narration text listing revealed cards
    
    Example Output:
        "Alice's summary: Profession: Doctor. Skill: Leadership. Phobia: Heights."
    """
    # Start with player name
    parts = [f"{player_hand.player.first_name or player_hand.player.username}'s summary:"]
    
    # Get all cards and their reveal status
    cards = player_hand.get_all_cards()
    reveal_status = player_hand.get_reveal_status()
    
    # Add each revealed card to narration
    for card_type, revealed in reveal_status.items():
        if revealed and cards[card_type]:
            # Format card type name (e.g., "additional_info" -> "Additional Info")
            card_type_display = card_type.replace('_', ' ').title()
            parts.append(f"{card_type_display}: {cards[card_type].name}")
    
    return " ".join(parts)


def get_game_announcement(game_session):
    """
    Generate dramatic announcement for game start
    
    Creates a narrative announcement of the catastrophe, bunker conditions,
    and game parameters. Played at game start for immersion.
    
    Args:
        game_session (GameSession): The game session with catastrophe and bunker set
    
    Returns:
        str: Announcement text with game scenario details
    
    Example Output:
        "Welcome to Bunker! Catastrophe: Nuclear War. Bunker: Fully Stocked. 
         Final Threshold: 92. Survivors needed: 4. Let the game begin!"
    """
    announcement = (
        f"Welcome to Bunker! "
        f"Catastrophe: {game_session.catastrophe.name}. "
        f"Bunker: {game_session.bunker.name}. "
        f"Final Threshold: {game_session.final_threshold}. "
        f"Survivors needed: {game_session.survivors_needed}. "
        f"Let the game begin!"
    )
    return announcement


def get_opening_narration(game_session):
    """
    Generate opening narration for game start
    
    Returns the dramatic opening narration that sets the tone for the apocalypse scenario.
    This is read aloud at game start to immerse players in the narrative.
    
    Args:
        game_session (GameSession): The game session with catastrophe and narration set
    
    Returns:
        str: Opening narration text with apocalypse scenario context
    
    Example Output:
        "The world you once knew… is gone. Civilization crumbled the moment..."
    """
    if game_session.opening_narration:
        return game_session.opening_narration
    else:
        # Fallback if narration not set
        return f"The catastrophe has struck. {game_session.catastrophe.name}. The world above is destroyed. You are in the bunker now. Survive or perish together."


def get_ending_narration(game_session):
    """
    Generate ending narration for game conclusion
    
    Returns the reflective ending narration played after final scoring.
    Summarizes the group's survival status and reflects on the experience.
    
    Args:
        game_session (GameSession): The game session with survival status and narration set
    
    Returns:
        str: Ending narration text reflecting on the game outcome
    
    Example Output:
        "In the end, survival was never guaranteed..."
    """
    if game_session.ending_narration:
        ending = game_session.ending_narration
        # Add survival outcome to narration
        if game_session.check_survival():
            ending += " Your group survived the bunker. Against all odds, you made it through."
        else:
            ending += " Your group did not survive. The bunker could not save you all."
        return ending
    else:
        # Fallback if narration not set
        if game_session.check_survival():
            return "Your group survived! You made it through the catastrophe."
        else:
            return "Your group did not survive the catastrophe. Better luck next time."


def available_voices():
    """
    Fetch list of available voices from ElevenLabs
    
    Returns all voices available on the user's ElevenLabs account.
    Useful for UI dropdown to let users select different voice preferences.
    
    Returns:
        list: List of voice objects with properties like name, id, labels, etc.
              Empty list if API fails or elevenlabs not installed
    
    Voice Example:
        {
            'voice_id': '21m00Tcm4TlvDq8ikWAM',
            'name': 'Rachel',
            'category': 'premade',
            ...
        }
    """
    if not ELEVENLABS_AVAILABLE or client is None:
        logger.warning("ElevenLabs not available - returning empty voice list")
        return []
    
    try:
        voices = client.voices.get_all()
        return voices
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        return []
