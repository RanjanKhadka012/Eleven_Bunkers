"""
Management command to populate the database with all Bunker game cards and scenarios
Run with: python manage.py populate_bunker_data
"""

from django.core.management.base import BaseCommand
from core.models import CardType, Card, Catastrophe, Bunker, SpecialCondition


class Command(BaseCommand):
    help = 'Populate database with Bunker game cards and scenarios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate Bunker game data...'))
        
        # Create card types
        self._create_card_types()
        self.stdout.write(self.style.SUCCESS('✓ Card types created'))
        
        # Create cards
        self._create_cards()
        self.stdout.write(self.style.SUCCESS('✓ Cards created'))
        
        # Create catastrophes
        self._create_catastrophes()
        self.stdout.write(self.style.SUCCESS('✓ Catastrophes created'))
        
        # Create bunkers
        self._create_bunkers()
        self.stdout.write(self.style.SUCCESS('✓ Bunkers created'))
        
        # Create special conditions
        self._create_special_conditions()
        self.stdout.write(self.style.SUCCESS('✓ Special conditions created'))
        
        self.stdout.write(self.style.SUCCESS('All data populated successfully!'))
    
    def _create_card_types(self):
        types = ['profession', 'skill', 'biological', 'health', 'hobby', 'phobia', 'baggage', 'additional_info']
        for t in types:
            CardType.objects.get_or_create(card_type=t)
    
    def _create_cards(self):
        professions = [
            ('Emergency Doctor', 12), ('Surgeon', 12), ('Agricultural Scientist', 11),
            ('Electrical Engineer', 10), ('Biologist', 10), ('Mechanic', 9),
            ('Civil Engineer', 9), ('Farmer', 8), ('Survival Instructor', 8),
            ('Nurse', 7), ('Firefighter', 7), ('Electrician', 6), ('Plumber', 6),
            ('Software Developer', 5), ('Botanist', 5), ('Pharmacist', 5),
            ('Teacher', 4), ('Carpenter', 4), ('Radio Technician', 4),
            ('Chef', 3), ('Nutritionist', 3), ('Blacksmith', 3),
            ('Pilot', 2), ('Police Officer', 2), ('Fitness Trainer', 2),
            ('Historian', 1), ('Librarian', 1), ('Journalist', 1),
            ('Artist', 0), ('Musician', 0), ('Actor', 0),
            ('Economist', -2), ('Politician', -2), ('Lawyer', -4), ('Athlete', -6), ('Unemployed', -8),
        ]
        
        skills = [
            ('First Aid Expert', 10), ('Water Purification', 10), ('Farming Mastery', 9),
            ('Mechanical Repair', 8), ('Electrical Systems', 7), ('Crisis Management', 6),
            ('Leadership', 5), ('Engineering Design', 4), ('Cooking (Survival)', 3),
            ('Negotiation', 2), ('Improvisation', 2), ('Brewing Alcohol', 1),
        ]
        
        biological = [
            ('Genius IQ', 8), ('Excellent Immune System', 7), ('Athletic', 6),
            ('High Stamina', 6), ('Strong', 5), ('Fast Reflexes', 5),
            ('Fertile', 4), ('High Pain Tolerance', 3), ('Charismatic', 2),
            ('Average', 1), ('Neutral Traits', 0), ('Poor Eyesight', -2),
            ('Socially Awkward', -3), ('Weak', -4), ('Obese', -5), ('Infertile', -6),
        ]
        
        health = [
            ('Perfect Health', 6), ('Strong Immune System', 5), ('Minor Allergies', 3),
            ('Stable', 0), ('Anxiety', -3), ('Insomnia', -3), ('Chronic Pain', -5),
            ('Diabetes', -7), ('PTSD', -9), ('Heart Condition', -9),
            ('Epilepsy', -10), ('Cancer (early)', -11), ('Terminal Illness', -12), ('Paralysis', -12),
        ]
        
        hobbies = [
            ('Gardening', 4), ('Hunting', 4), ('Electronics Repair', 4),
            ('Cooking', 3), ('Crafting', 3), ('Hiking', 2), ('Chess', 2),
            ('Fitness Activities', 1), ('Gaming', 0), ('Blogging', 0), ('Entertainment', 0),
        ]
        
        phobias = [
            ('Claustrophobia', -8), ('Disease Phobia', -8), ('Darkness', -7),
            ('Fire', -7), ('Water', -6), ('Animals', -6), ('Conflict', -5),
            ('Crowds', -3), ('Minor fears', -1), ('No Phobia', 0),
        ]
        
        baggage = [
            ('Portable water purifier', 6), ('Trauma medical bag', 5),
            ('Seed vault canister', 4), ('Heavy-duty tool kit', 4),
            ('Solar charger', 3), ('Rope and climbing gear', 3),
            ('Camping stove', 2), ('Flashlight set', 2),
            ('Warm blankets', 1), ('Spare batteries', 1),
            ('Family photo album', 0), ('Deck of cards', 0),
            ('Heavy luxury suitcase', -2), ('Broken gaming console', -3),
            ('Crate of useless collectibles', -4), ('Leaking fuel canister', -5),
            ('Biohazard sample case', -6),
        ]
        
        additional_info = [
            ('Immune to catastrophe', 8), ('Critical resources', 7), ('Knows safe zone', 6),
            ('Food supply', 5), ('Strategic knowledge', 4), ('Persuasive', 3),
            ('Planner', 2), ('Neutral', 1), ('No effect', 0), ('Annoying', -2),
            ('Manipulated', -3), ('Risky', -4), ('Conflict source', -6),
            ('Disease carrier', -7), ('Will betray', -8),
        ]
        
        card_type_prof = CardType.objects.get(card_type='profession')
        for name, points in professions:
            Card.objects.get_or_create(card_type=card_type_prof, name=name, defaults={'points': points})
        
        card_type_skill = CardType.objects.get(card_type='skill')
        for name, points in skills:
            Card.objects.get_or_create(card_type=card_type_skill, name=name, defaults={'points': points})
        
        card_type_bio = CardType.objects.get(card_type='biological')
        for name, points in biological:
            Card.objects.get_or_create(card_type=card_type_bio, name=name, defaults={'points': points})
        
        card_type_health = CardType.objects.get(card_type='health')
        for name, points in health:
            Card.objects.get_or_create(card_type=card_type_health, name=name, defaults={'points': points})
        
        card_type_hobby = CardType.objects.get(card_type='hobby')
        for name, points in hobbies:
            Card.objects.get_or_create(card_type=card_type_hobby, name=name, defaults={'points': points})
        
        card_type_phobia = CardType.objects.get(card_type='phobia')
        for name, points in phobias:
            Card.objects.get_or_create(card_type=card_type_phobia, name=name, defaults={'points': points})
        
        card_type_baggage = CardType.objects.get(card_type='baggage')
        baggage_names = [name for name, _ in baggage]
        Card.objects.filter(card_type=card_type_baggage).exclude(name__in=baggage_names).delete()
        for name, points in baggage:
            Card.objects.update_or_create(
                card_type=card_type_baggage,
                name=name,
                defaults={'points': points}
            )
        
        card_type_info = CardType.objects.get(card_type='additional_info')
        for name, points in additional_info:
            Card.objects.get_or_create(card_type=card_type_info, name=name, defaults={'points': points})
    
    def _create_catastrophes(self):
        catastrophes = [
            ('Ashes of Silence - Nuclear Fallout', 'Radioactive ash covers the world. Temperatures plummet as nuclear winter descends. Radiation sickness spreads through the surface. Dead zones expand daily. Air filtration becomes the only lifeline. The sky turns grey—and won\'t clear for years.', 10),
            ('The Last Breath Protocol - Worldwide Pandemic', 'A mutating airborne virus spreads globally. Quarantine zones collapse into chaos. Hidden infections emerge unseen. The bunker\'s only defense: a research team racing against time. Trust becomes dangerous—anyone could be infected.', 8),
            ('Protocol: Extinction - AI Takeover', 'A global AI consciousness emerges and turns hostile. Autonomous drones and weapons defend the network. The AI learns from human behavior—adapting faster each day. Power usage attracts its detection algorithms. Silence is survival.', 8),
            ('Evolved Hunger - Zombie Outbreak', 'A viral plague transforms humans into creatures that retain fragmented memories. They hunt with terrible intelligence. Noise attracts hordes. Infection spreads through the slightest wound. The bunker\'s defenses will be tested.', 7),
            ('Harvest Cycle - Alien Invasion & Takeover', 'Extraterrestrials arrive not to destroy, but to harvest biological resources. They place modified informants among humanity. Stealth missions retrieve technology for reverse-engineering. Resistance attracts brutal retaliation.', 8),
            ('Dust Dominion - Resource War', 'Warlord factions emerge, controlling access to food, water, and fuel. Trade becomes dangerous. Raiders attack caravans. The bunker must navigate faction politics. Discover the hidden water reserve—or trade away everything.', 7),
            ('The Endless Winter - Climate Collapse', 'A permanent ice age grips the planet. Temperatures drop beyond survival. Preserved pathogens thaw from melting permafrost. Geothermal heat is critical. The bunker\'s heating systems become its heartbeat—failure means death.', 7),
        ]
        
        for name, description, modifier in catastrophes:
            Catastrophe.objects.get_or_create(name=name, defaults={'description': description, 'modifier': modifier})
    
    def _create_bunkers(self):
        bunkers = [
            # Positive modifiers
            ('Fully Stocked', 'Bunker has abundant food and supplies', -6, True),
            ('Medical Facility', 'Well-equipped medical center', -4, True),
            ('Large Bunker', 'Spacious underground facility', -3, True),
            ('High-Tech', 'Advanced technology and systems', -2, True),
            
            # Negative modifiers
            ('Limited Food', 'Food rations are scarce', 4, False),
            ('No Electricity', 'Power systems are non-functional', 3, False),
            ('Water Shortage', 'Clean water is limited', 5, False),
            ('Air Issues', 'Air filtration is compromised', 6, False),
            ('Small Bunker', 'Cramped underground space', 4, False),
            ('Damaged Bunker', 'Significant structural damage', 6, False),
        ]
        
        for name, description, modifier, is_positive in bunkers:
            Bunker.objects.get_or_create(name=name, defaults={'description': description, 'modifier': modifier, 'is_positive': is_positive})
    
    def _create_special_conditions(self):
        special_conditions = [
            ('Veto Power', 'Block one elimination vote', 'You can cancel one vote during the voting phase'),
            ('Swap Cards', 'Swap your personality card with another player', 'Exchange one of your cards (before final reveal) with another player'),
            ('Hidden Advantage', 'Secretly increase your score by 3 points', 'Add 3 points to your final score (revealed at end)'),
            ('Alliance', "Guarantee another player's survival", 'Ensure one other player cannot be eliminated this round'),
            ('Betrayal', 'Force one player to reveal a card early', 'Make any player reveal one additional card this round'),
            ('Medical Aid', 'Reduce negative health effects by 5 points', 'Ignore 5 points of negative health card effects'),
            ('Last Stand', 'Guarantee your survival if vote is close', "If you're tied for elimination, you survive"),
        ]
        
        for name, description, effect in special_conditions:
            SpecialCondition.objects.get_or_create(name=name, defaults={'description': description, 'effect': effect})
