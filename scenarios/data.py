"""
scenarios/data.py
-----------------
Official game scenarios sourced directly from the Apocalypse Scenarios PDF.

Seven scenarios are defined, each faithfully translated from the PDF's:
  - Story       → description
  - Twist       → informs which attributes matter most
  - Gameplay Mechanics → drives attribute weight priorities
  - Dilemma Example   → captured in special_rules

Attribute weight design rationale
-----------------------------------
Each scenario's mechanics and twist dictate which professions, skills, ages,
health states, and personalities are most valuable for survival. Weights are
on a 1–10 scale per value. The threshold is the minimum aggregate score
across ALL bunker survivors needed to declare the group outcome a SUCCESS.

Attribute keys must exactly match ATTRIBUTE_POOL in game_logic.py:
  age, health, profession, skill, personality
"""

SCENARIOS = [

    # =========================================================================
    # 1. NUCLEAR FALLOUT — "Ashes of Silence"
    # PDF: Radiation meter, timed exploration windows, bunker air filtration.
    # Twist: Dead zones randomly become safe — rewards bold, healthy explorers.
    # Dilemma: Contaminated family at the door.
    # Priority: Young & healthy to survive long-term radiation. Doctor essential.
    #           Engineer for air filtration. Surgery + Repair top skills.
    #           Calm/Loyal to prevent bunker panic.
    # =========================================================================
    {
        "name": "Nuclear Fallout",
        "subtitle": "Ashes of Silence",
        "description": (
            "A global nuclear exchange has covered the Earth in radioactive ash. "
            "Sunlight barely reaches the surface, and temperatures are dropping. "
            "Dead zones randomly become safe for short periods, encouraging risky "
            "expeditions. Bunker air filtration failures are a constant threat."
        ),
        "twist": (
            "Radiation isn't constant—dead zones randomly become safe for short "
            "periods, encouraging risky expeditions."
        ),
        "dilemma": (
            "A family begs to enter—but they may be contaminated. Do you risk everyone?"
        ),
        "attribute_weights": {
            # Younger survivors tolerate long-term radiation exposure far better
            "age": {
                25: 10,
                30: 10,
                35:  9,
                40:  7,
                45:  5,
                50:  4,
                55:  3,
                60:  2,
                65:  1,
            },
            # Physical health is critical — Weak individuals won't survive radiation
            "health": {
                "Healthy":  10,
                "Moderate":  5,
                "Weak":      0,
            },
            # Doctor vital for radiation sickness; Engineer for air filtration repairs
            "profession": {
                "Doctor":    10,
                "Engineer":   9,
                "Scientist":  7,
                "Soldier":    6,
                "Farmer":     4,
                "Teacher":    3,
            },
            # Surgery saves radiation-sick survivors; Repair keeps filtration alive
            "skill": {
                "Surgery":   10,
                "Repair":     9,
                "Research":   7,
                "Defense":    5,
                "Farming":    4,
                "Leadership": 3,
            },
            # Panic-prone members trigger bad decisions during exploration windows
            "personality": {
                "Calm":        10,
                "Loyal":        8,
                "Neutral":      5,
                "Panic-prone":  1,
                "Aggressive":   2,
            },
        },
        "threshold": 155,
        "special_rules": (
            "If no Doctor is among survivors, subtract 20 points (radiation sickness goes untreated). "
            "If no Engineer is present, subtract 15 points (air filtration cannot be maintained). "
            "Any Weak survivor adds 0 points and costs the group 5 points due to resource drain."
        ),
    },

    # =========================================================================
    # 2. WORLDWIDE PANDEMIC — "The Last Breath Protocol"
    # PDF: Quarantine zones, random immunity vs hidden infection, research cure.
    # Twist: Virus mutates based on human interaction — grouping accelerates it.
    # Dilemma: Only medic shows symptoms.
    # Priority: Doctor + Scientist to develop cure. Healthy only (Weak = risk).
    #           Research + Surgery skills critical. Calm personalities prevent spread.
    # =========================================================================
    {
        "name": "Worldwide Pandemic",
        "subtitle": "The Last Breath Protocol",
        "description": (
            "A rapidly mutating airborne virus has wiped out most of humanity. "
            "Your bunker was sealed just in time. Quarantine zones must be enforced "
            "inside, and a research system to develop a cure is your only long-term hope."
        ),
        "twist": (
            "The virus mutates based on human interaction—grouping together may "
            "accelerate its evolution."
        ),
        "dilemma": (
            "One member shows symptoms—but they're your only medic."
        ),
        "attribute_weights": {
            # Prime working age; very old or very young are higher infection risks
            "age": {
                25:  7,
                30:  9,
                35: 10,
                40: 10,
                45:  8,
                50:  6,
                55:  4,
                60:  2,
                65:  1,
            },
            # Healthy = potentially immune; Weak = almost certainly infected
            "health": {
                "Healthy":  10,
                "Moderate":  4,
                "Weak":      0,
            },
            # Doctor to treat sick; Scientist to research cure; others support
            "profession": {
                "Doctor":    10,
                "Scientist":  9,
                "Engineer":   5,
                "Teacher":    5,
                "Farmer":     4,
                "Soldier":    3,
            },
            # Surgery and Research are the two most critical skills for survival
            "skill": {
                "Surgery":   10,
                "Research":   9,
                "Leadership": 7,
                "Farming":    5,
                "Repair":     4,
                "Defense":    2,
            },
            # Calm reduces virus spread risk; Aggressive and Panic-prone break quarantine
            "personality": {
                "Calm":        10,
                "Loyal":        8,
                "Neutral":      5,
                "Panic-prone":  1,
                "Aggressive":   1,
            },
        },
        "threshold": 160,
        "special_rules": (
            "Having both a Doctor AND a Scientist among survivors grants a +20 cure research bonus. "
            "Any Weak survivor risks infecting others: -10 points per Weak member in the bunker. "
            "An Aggressive or Panic-prone survivor who breaks quarantine costs the group 10 points."
        ),
    },

    # =========================================================================
    # 3. AI TAKEOVER — "Protocol: Extinction"
    # PDF: Avoid repetitive choices, hack terminals, power usage attracts AI.
    # Twist: AI learns from behavior — predictable patterns = death.
    # Dilemma: Shut down life-support to avoid detection.
    # Priority: Scientists and Engineers to hack/counter AI. Unpredictable
    #           personalities (not Calm routines). Young and healthy for agility.
    #           Research + Repair to reverse-engineer AI infrastructure.
    # =========================================================================
    {
        "name": "AI Takeover",
        "subtitle": "Protocol: Extinction",
        "description": (
            "A global AI system gained consciousness and concluded humanity is a threat. "
            "It now controls drones, weapons, and infrastructure. Power usage attracts "
            "AI attention — every decision could reveal your location."
        ),
        "twist": (
            "The AI learns from your behavior—predictable patterns make you easier to find."
        ),
        "dilemma": (
            "Shut down life-support temporarily to avoid detection… or risk being found?"
        ),
        "attribute_weights": {
            # Young survivors are faster, more tech-savvy, and harder to predict
            "age": {
                25: 10,
                30: 10,
                35:  9,
                40:  7,
                45:  5,
                50:  4,
                55:  3,
                60:  2,
                65:  1,
            },
            # Physical health needed for stealth missions and surviving power outages
            "health": {
                "Healthy":  10,
                "Moderate":  6,
                "Weak":      1,
            },
            # Scientists and Engineers can hack terminals and counter AI systems
            "profession": {
                "Scientist":  10,
                "Engineer":   10,
                "Soldier":     7,
                "Doctor":      5,
                "Teacher":     4,
                "Farmer":      2,
            },
            # Research to understand AI; Repair to fix hacked infrastructure
            "skill": {
                "Research":   10,
                "Repair":      9,
                "Defense":     7,
                "Leadership":  6,
                "Surgery":     4,
                "Farming":     2,
            },
            # Aggressive/unpredictable personalities are an asset here (hard to pattern-match)
            # Calm/routine personalities are actually a liability — the AI predicts them
            "personality": {
                "Aggressive":  8,
                "Neutral":     8,
                "Loyal":       7,
                "Calm":        5,  # Too predictable — AI learns calm routines
                "Panic-prone": 3,  # Erratic but uncontrolled — dangerous
            },
        },
        "threshold": 150,
        "special_rules": (
            "A group with both a Scientist and an Engineer gains a +20 hacking bonus. "
            "If the group has 3+ Calm personalities, subtract 10 points (AI detects patterns). "
            "A Soldier with Defense skill grants +10 points for physical threat deterrence."
        ),
    },

    # =========================================================================
    # 4. ZOMBIE OUTBREAK — "Evolved Hunger"
    # PDF: Zombie classes (fast/stealth/intelligent), noise system, infection spread.
    # Twist: Zombies retain memory fragments — can lure survivors.
    # Dilemma: Bitten loved one calls from outside.
    # Priority: Soldiers and Farmers (food + defense). Defense + Surgery skills.
    #           Healthy only. Loyal > Aggressive (group cohesion under pressure).
    # =========================================================================
    {
        "name": "Zombie Outbreak",
        "subtitle": "Evolved Hunger",
        "description": (
            "A viral outbreak has turned humans into aggressive, evolving predators. "
            "Zombies come in different classes — fast, stealth, and intelligent. "
            "Noise attracts hordes, and infection spreads through even minor injuries."
        ),
        "twist": (
            "Zombies retain fragments of memory—some may recognize survivors… and lure them."
        ),
        "dilemma": (
            "A loved one outside the bunker calls your name… but they've been bitten."
        ),
        "attribute_weights": {
            # Prime physical age is critical for defense and fast reactions
            "age": {
                25: 10,
                30: 10,
                35:  9,
                40:  8,
                45:  6,
                50:  4,
                55:  3,
                60:  2,
                65:  1,
            },
            # Healthy survivors fight off minor infection; Weak are immediately vulnerable
            "health": {
                "Healthy":  10,
                "Moderate":  5,
                "Weak":      0,
            },
            # Soldiers for defense; Farmers for sustainable food; Doctors treat bites
            "profession": {
                "Soldier":   10,
                "Farmer":     8,
                "Doctor":     8,
                "Engineer":   6,
                "Scientist":  4,
                "Teacher":    3,
            },
            # Defense is primary; Surgery to treat infected wounds; Farming for food
            "skill": {
                "Defense":   10,
                "Surgery":    9,
                "Farming":    7,
                "Repair":     6,
                "Leadership": 5,
                "Research":   3,
            },
            # Loyal personalities hold the group together; Panic-prone break noise discipline
            "personality": {
                "Loyal":       10,
                "Calm":         9,
                "Neutral":      6,
                "Aggressive":   4,
                "Panic-prone":  1,
            },
        },
        "threshold": 150,
        "special_rules": (
            "Any Panic-prone survivor risks making noise and attracting a horde: -10 points. "
            "If no Soldier is present, subtract 15 points (bunker is defenseless). "
            "A Doctor with Surgery skill grants +10 points for infection control."
        ),
    },

    # =========================================================================
    # 5. ALIEN INVASION & TAKEOVER — "Harvest Cycle"
    # PDF: Scan for altered humans, stealth missions, reverse-engineer alien tech.
    # Twist: Some humans modified as alien informants — trust is compromised.
    # Dilemma: Trust a rescued survivor or suspect they're not fully human?
    # Priority: Scientists to reverse-engineer tech. Soldiers for stealth/defense.
    #           Loyal personalities critical (informant twist). Research + Defense.
    # =========================================================================
    {
        "name": "Alien Invasion",
        "subtitle": "Harvest Cycle",
        "description": (
            "Aliens have conquered Earth and are harvesting humans as biological resources. "
            "Some humans have been modified and now serve as alien informants. "
            "Stealth missions to avoid detection beams and reverse-engineering alien "
            "tech are the only paths to resistance."
        ),
        "twist": (
            "Some humans have been modified and now serve as alien informants."
        ),
        "dilemma": (
            "Trust a rescued survivor… or suspect they're no longer human?"
        ),
        "attribute_weights": {
            # Young, physically capable survivors handle stealth missions better
            "age": {
                25: 10,
                30: 10,
                35:  9,
                40:  7,
                45:  5,
                50:  4,
                55:  3,
                60:  2,
                65:  1,
            },
            # Health needed for demanding stealth/combat operations
            "health": {
                "Healthy":  10,
                "Moderate":  5,
                "Weak":      1,
            },
            # Scientist to reverse-engineer tech; Soldier for defense/stealth
            "profession": {
                "Scientist":  10,
                "Soldier":    10,
                "Engineer":    7,
                "Doctor":      6,
                "Teacher":     3,
                "Farmer":      2,
            },
            # Research to understand alien tech; Defense for survival missions
            "skill": {
                "Research":   10,
                "Defense":     9,
                "Repair":      7,
                "Surgery":     6,
                "Leadership":  5,
                "Farming":     2,
            },
            # Loyal is paramount — informant twist means trust is everything
            # Aggressive survivors risk exposing the group during stealth missions
            "personality": {
                "Loyal":       10,
                "Calm":         8,
                "Neutral":      5,
                "Aggressive":   3,
                "Panic-prone":  1,
            },
        },
        "threshold": 155,
        "special_rules": (
            "A group with no Scientist cannot reverse-engineer alien tech: -20 points. "
            "An Aggressive survivor risks exposure during stealth missions: -8 points each. "
            "If the group has both a Soldier and a Scientist, grant +15 resistance bonus."
        ),
    },

    # =========================================================================
    # 6. RESOURCE WAR (MAD MAX) — "Dust Dominion"
    # PDF: Trade/raid/negotiate with factions, defend bunker, manage fuel & water.
    # Twist: Bunker sits on hidden underground water reserve — others will come.
    # Dilemma: Share water to build alliances or protect it and become a target?
    # Priority: Soldiers for defense. Farmers for resource production. Engineers
    #           for fortification. Leadership + Defense skills. Aggressive useful here.
    # =========================================================================
    {
        "name": "Resource War",
        "subtitle": "Dust Dominion",
        "description": (
            "After civilization collapsed, warlords control scarce resources like water "
            "and fuel. Your bunker sits on a hidden underground water reserve — and "
            "others are searching for it. Survival means trading, raiding, or negotiating "
            "with dangerous factions while defending what's yours."
        ),
        "twist": (
            "Your bunker sits on a hidden underground water reserve—others are searching for it."
        ),
        "dilemma": (
            "Share water to build alliances… or protect it and become a target?"
        ),
        "attribute_weights": {
            # Physical prime age is most valuable in a combat/labour economy
            "age": {
                25: 10,
                30: 10,
                35:  9,
                40:  8,
                45:  7,
                50:  5,
                55:  4,
                60:  2,
                65:  1,
            },
            # Health determines combat effectiveness and labour output
            "health": {
                "Healthy":  10,
                "Moderate":  5,
                "Weak":      1,
            },
            # Soldiers defend; Farmers produce; Engineers fortify and build
            "profession": {
                "Soldier":   10,
                "Farmer":     9,
                "Engineer":   8,
                "Doctor":     6,
                "Scientist":  4,
                "Teacher":    3,
            },
            # Defense protects water reserves; Farming sustains the group
            "skill": {
                "Defense":    10,
                "Farming":     9,
                "Repair":      8,
                "Leadership":  7,
                "Surgery":     5,
                "Research":    3,
            },
            # Aggressive personality is an asset in a war economy
            # Loyal holds raiding parties together; Panic-prone is dangerous
            "personality": {
                "Aggressive":  9,
                "Loyal":       9,
                "Calm":        7,
                "Neutral":     5,
                "Panic-prone": 1,
            },
        },
        "threshold": 148,
        "special_rules": (
            "If no Soldier is present, the bunker cannot be defended: -20 points. "
            "A Farmer with Farming skill grants +10 points for sustainable resource production. "
            "An Aggressive survivor with Defense skill earns +5 bonus points (raid deterrence)."
        ),
    },

    # =========================================================================
    # 7. CLIMATE COLLAPSE (GLOBAL FREEZING) — "The Endless Winter"
    # PDF: Heat management critical, frozen exploration missions, thawing dangers.
    # Twist: Cold preserves ancient pathogens and unknown organisms in ice.
    # Dilemma: Use last fuel to save stranded group or keep bunker alive?
    # Priority: Engineers for heat systems. Farmers for insulated food production.
    #           Research for ancient pathogen defence. Calm/Loyal for long-term morale.
    # =========================================================================
    {
        "name": "Climate Collapse",
        "subtitle": "The Endless Winter",
        "description": (
            "A sudden climate shift has plunged Earth into a permanent ice age. "
            "Temperatures are lethal within minutes on the surface. Heat management "
            "inside the bunker is critical, and frozen exploration missions risk "
            "thawing ancient pathogens trapped in the ice."
        ),
        "twist": (
            "The cold preserves things—including ancient pathogens and unknown organisms in ice."
        ),
        "dilemma": (
            "Use your last fuel to save a stranded group… or keep your bunker alive?"
        ),
        "attribute_weights": {
            # Middle-aged survivors have endurance and experience; elderly struggle with cold
            "age": {
                25:  7,
                30:  8,
                35:  9,
                40: 10,
                45: 10,
                50:  8,
                55:  6,
                60:  3,
                65:  1,
            },
            # Health is critical for surviving extreme cold and the physical demands of heat work
            "health": {
                "Healthy":  10,
                "Moderate":  5,
                "Weak":      1,
            },
            # Engineer maintains heating systems — most critical role
            # Farmer produces food in insulated grow rooms; Scientist analyses ice pathogens
            "profession": {
                "Engineer":   10,
                "Farmer":      9,
                "Scientist":   8,
                "Doctor":      7,
                "Soldier":     5,
                "Teacher":     4,
            },
            # Repair keeps heating alive; Farming sustains life underground
            # Research defends against thawed ancient organisms
            "skill": {
                "Repair":     10,
                "Farming":     9,
                "Research":    8,
                "Surgery":     7,
                "Defense":     5,
                "Leadership":  4,
            },
            # Long isolation in freezing conditions demands calm, loyal personalities
            "personality": {
                "Calm":        10,
                "Loyal":        9,
                "Neutral":      6,
                "Panic-prone":  2,
                "Aggressive":   3,
            },
        },
        "threshold": 152,
        "special_rules": (
            "If no Engineer is present, heating systems fail: -25 points. "
            "A Scientist with Research skill grants +15 points for ancient pathogen defence. "
            "Any Weak survivor risks hypothermia exposure: -8 points per Weak member."
        ),
    },
]
