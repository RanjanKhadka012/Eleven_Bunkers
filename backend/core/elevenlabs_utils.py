"""
ElevenLabs Text-to-Speech utilities for Bunker game
"""
import os
from elevenlabs import ElevenLabs
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Initialize ElevenLabs client
client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))


def text_to_speech(text, voice_id='21m00Tcm4TlvDq8ikWAM', output_path=None):
    """
    Convert text to speech using ElevenLabs API
    
    Args:
        text: Text to convert to speech
        voice_id: Voice ID (default is Rachel)
        output_path: Path to save audio file (optional)
    
    Returns:
        Audio bytes or file path if saved
    """
    try:
        audio = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_monolingual_v1"
        )
        
        if output_path:
            client.save(audio, output_path)
            return output_path
        else:
            return audio
    
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise


def get_card_narration(card):
    """
    Generate narration for a card
    
    Args:
        card: Card object
    
    Returns:
        Narration text
    """
    narration = f"{card.name}. {card.description if card.description else ''}"
    return narration.strip()


def get_player_summary_narration(player_hand):
    """
    Generate narration for a player's revealed cards
    
    Args:
        player_hand: PlayerHand object
    
    Returns:
        Narration text
    """
    parts = [f"{player_hand.player.first_name or player_hand.player.username}'s summary:"]
    
    cards = player_hand.get_all_cards()
    reveal_status = player_hand.get_reveal_status()
    
    for card_type, revealed in reveal_status.items():
        if revealed and cards[card_type]:
            parts.append(f"{card_type.replace('_', ' ').title()}: {cards[card_type].name}")
    
    return " ".join(parts)


def get_game_announcement(game_session):
    """
    Generate announcement for game start
    
    Args:
        game_session: GameSession object
    
    Returns:
        Announcement text
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


def available_voices():
    """
    Get list of available voices from ElevenLabs
    
    Returns:
        List of voice objects
    """
    try:
        voices = client.voices.get_all()
        return voices
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        return []
