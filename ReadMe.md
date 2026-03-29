# 🎮 Bunker - Social Survival Game
Bunker throws you and your friends into a last-chance survival showdown. Spin up a lobby, get a wild catastrophe (alien harvests? nuclear fallout?), and race through reveal rounds to prove your worth. Flaunt your profession, flex your skills, hide your baggage—then debate, accuse, and vote before the clock slams shut. Hosts can pause, skip, or jump to the verdict. ElevenLabs voiceovers boom out the story beats, and every elimination changes the fate: hit the survival threshold or humanity’s toast. Fast setup, frantic decisions, brutal fun—ready to find out who makes it into the bunker?

A full-stack web application for playing **Bunker**, an engaging social deduction game where players debate who gets into a survival bunker based on hidden persona cards and a complex point-scoring system.

## 📖 Game Overview

**Bunker** is a social game for 4-8 players where:
1. **Setup**: Each player is randomly assigned 8 hidden persona cards (profession, skill, phobia, etc.) and 2 special condition cards
2. **Reveal**: Players gradually reveal their cards to the group
3. **Debate**: Players discuss and debate who should be eliminated
4. **Vote**: Players vote to eliminate candidates
5. **Final Scoring**: The remaining survivors' cards are scored
6. **Outcome**: Humanity survives if the team score meets the threshold determined by catastrophe + bunker conditions

**Win Condition**: `final_score >= (survivors_needed × 9) + catastrophe_modifier + bunker_modifier`

Example: With 4 survivors needed, Nuclear War catastrophe (+10), and a Poor Bunker (+5):
- Base threshold: 4 × 9 = 36
- With modifiers: 36 + 10 + 5 = **41 points needed to survive**

---

## 🏗️ Project Structure

```
Eleven_Bunker/
├── src/                         # React application (Vite)
│   ├── components/              # React components
│   │   ├── HomeScreen.jsx
│   │   ├── JoinScreen.jsx
│   │   └── LobbyScreen.jsx
│   ├── lib/
│   │   └── lobbyStorage.js      # Local storage utilities
│   ├── styles/
│   │   └── app.css              # Global styles (glassmorphism design)
│   ├── App.jsx                  # Main app component
│   └── main.jsx                 # React entry point
│
├── backend/                     # Django REST API
│   ├── core/
│   │   ├── models.py            # 11 database models (Card, GameSession, etc.)
│   │   ├── views.py             # 7 ViewSets with game logic
│   │   ├── serializers.py       # REST serializers
│   │   ├── urls.py              # API routes
│   │   ├── admin.py             # Django admin configuration
│   │   ├── elevenlabs_utils.py  # Text-to-speech integration
│   │   └── management/
│   │       └── commands/
│   │           └── populate_bunker_data.py
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
│
├── index.html                   # HTML entry point
├── vite.config.js               # Vite configuration
├── package.json                 # NPM dependencies
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Git

### Frontend Setup

```bash
# Navigate to project root
cd Eleven_Bunker

# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev
```

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
node server.js

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env to add ElevenLabs API key
# ELEVENLABS_API_KEY=<your api key here>

## 🎯 Key Features

### Frontend Features
- ✅ Host/Join game lobby system
- ✅ Real-time lobby synchronization (1-second polling)
- ✅ Local storage-based lobby persistence
- ✅ Responsive design (mobile-first)
- ✅ Glassmorphism UI with organic green aesthetic
- ⏳ Card reveal interface (coming soon)
- ⏳ Voting UI (coming soon)
- ⏳ Score calculation display (coming soon)

### Backend Features
- ✅ Complete REST API with 25+ endpoints
- ✅ 11 database models for full game logic
- ✅ Card dealing and random assignment
- ✅ Threshold calculation with modifiers
- ✅ Scoring system (-8 to +12 points per card)
- ✅ Voting round management
- ✅ Text-to-speech narration (ElevenLabs)
- ✅ Game event logging
- ✅ Django admin interface with search/filter

### Technology Stack

**Frontend:**
- React 19.2
- Vite 8.0 (build tool)
- CSS3 (Grid, Glassmorphism)
- localStorage API

**Backend:**
- Django 6.0.3
- Django REST Framework 3.17
- SQLite/PostgreSQL (database)
- ElevenLabs SDK (text-to-speech)
- django-cors-headers 4.9

---

## 🎨 Game Data

### Card Types (8 total)
Each player has one card of each type, randomly assigned:
1. **Profession** (e.g., Doctor +12, Prisoner -8)
2. **Skill** (e.g., Leadership +6, Incompetent -5)
3. **Age** (e.g., 24 +3, 70 -4)
4. **Health** (e.g., Healthy +7, Diseased -6)
5. **Hobby** (e.g., Gardening +6, Gambler -3)
6. **Phobia** (e.g., None +2, Claustrophobia -4)
7. **Baggage** (e.g., Clean +4, Criminal -8)
8. **Additional Info** (e.g., Optimist +3, Pessimist -2)

### Catastrophes (7 scenarios)
- Nuclear War (+10) - Extreme difficulty
- Alien Invasion (+9)
- Pandemic (+8)
- Zombie Apocalypse (+6)
- Climate Disaster (+5)
- EMP Strike (+4)
- Meteor Strike (+3)

### Bunker Conditions (10 total)
**Positive (make survival easier):**
- Fully Stocked (-6)
- Medical Facility (-4)
- Large Space (-3)
- High-Tech (-2)

**Negative (make survival harder):**
- Limited Food (+4)
- Small Space (+4)
- No Electricity (+3)
- Damaged Structure (+6)
- No Water Supply (+5)
- Polluted Air (+6)

### Special Conditions (per player)
2 strategic cards per player that affect gameplay but don't count toward survival score

---

## 📡 API Endpoints

### Base URL: `http://localhost:8000/api/`

### Game Session Endpoints
- `POST /game-sessions/` - Create new game
- `GET /game-sessions/` - List your games
- `GET /game-sessions/{id}/` - Get game details
- `POST /game-sessions/{id}/join_game/` - Join game
- `POST /game-sessions/{id}/start_game/` - Start game (deal cards)
- `POST /game-sessions/{id}/reveal_card/` - Reveal a card
- `POST /game-sessions/{id}/cast_vote/` - Vote to eliminate
- `POST /game-sessions/{id}/eliminate_player/` - Eliminate voted player
- `POST /game-sessions/{id}/final_scoring/` - Calculate results
- `GET /game-sessions/{id}/game_status/` - Get quick status

### Card Endpoints
- `GET /cards/` - List all cards (filterable by type)
- `GET /card-types/` - List 8 card types

### Scenario Endpoints
- `GET /catastrophes/` - List all catastrophe scenarios
- `GET /bunkers/` - List all bunker conditions
- `GET /bunkers/positive/` - Get advantage bunkers
- `GET /bunkers/negative/` - Get disadvantage bunkers
- `GET /special-conditions/` - List special condition cards

### Text-to-Speech Endpoints
- `POST /text-to-speech/card_narration/` - Generate card audio
- `POST /text-to-speech/player_summary/` - Generate player summary audio
- `POST /text-to-speech/game_announcement/` - Generate game start announcement

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# ElevenLabs API Key for text-to-speech
ELEVENLABS_API_KEY=sk_a6a35fec4355cb53c7525944ee1b7bc573837d6b27d8e510

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Database (optional, defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/bunker
```

---

## 📚 Code Documentation

The codebase is thoroughly commented:

### Frontend Files
- **App.jsx** - Game state management, screen transitions, lobby sync
- **Components/** - HomeScreen, JoinScreen, LobbyScreen
- **lobbyStorage.js** - Local storage utilities for lobby persistence
- **app.css** - Design system and CSS variables

### Backend Files
- **models.py** - 11 database models with docstrings
- **views.py** - 7 ViewSets with detailed endpoint documentation
- **elevenlabs_utils.py** - Text-to-speech integration
- **admin.py** - Django admin with helpful descriptions

---

## 🎮 How to Play

### 1. **Start a Game**
- Click "Host Game" to create a new lobby
- Share the 6-character access code with friends

### 2. **Join a Game**
- Click "Join"
- Enter your player name and access code
- Wait for host to start

### 3. **Game Begins**
- Cards are randomly assigned (you know your own)
- Players reveal cards one at a time
- Discuss and debate who's the liability

### 4. **Voting**
- Vote to eliminate players
- Majority vote eliminates that player
- Repeat until 4 survivors remain (or as configured)

### 5. **Final Score**
- Remaining players' cards are added up
- Compare to threshold (base + catastrophe + bunker)
- Humanity survives if score >= threshold!

---

## 🐛 Debugging

### Frontend Issues
- Check browser console for React errors
- Frontend runs on `http://localhost:3000`
- Backend proxy configured in `vite.config.js`

### Backend Issues
- Check Django logs: `python manage.py runserver`
- Django admin available at `http://localhost:8000/admin`
- Database shell: `python manage.py shell`

### Database Issues
```bash
# Reset database (fresh start)
rm db.sqlite3
python manage.py migrate
python manage.py populate_bunker_data
```

---

## 📝 TODO - Features in Development

- [ ] Implement API integration in frontend components
- [ ] Build card reveal UI
- [ ] Build voting interface
- [ ] Add score calculation display
- [ ] Implement WebSocket for real-time updates
- [ ] Add user authentication/JWT
- [ ] Create game history/replay feature
- [ ] Mobile app optimization
- [ ] Sound effects and animations
- [ ] Deployment setup (Heroku/Railway)

---

## 👨‍💻 Development Tips

### Hot Reload
Both frontend and backend support hot reload in development:
- **Frontend**: Vite automatically reloads on file changes
- **Backend**: Django runserver watches for file changes

### Testing API Endpoints
Use Django admin interface:
```
http://localhost:8000/admin/
```

Or use a REST client like Insomnia/Postman with the API endpoints listed above.

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/card-reveal

# Make changes and commit
git add .
git commit -m "Add card reveal functionality"

# Push to GitHub
git push origin feature/card-reveal
```

---

## 📄 License

ISC License - See LICENSE file

---

## 👤 Author

**Ranjan Khadka** - [GitHub](https://github.com/RanjanKhadka012)

---

## 🙏 Acknowledgments

- ElevenLabs API for realistic text-to-speech narration
- Django and React communities
- All contributors and testers

---

## 📞 Support

For issues or questions:
1. Check the [GitHub Issues](https://github.com/RanjanKhadka012/Eleven_Bunkers/issues)
2. Review detailed documentation in code comments
3. Contact the development team

---

**Enjoy the game! 🎮 Remember: In the bunker, everyone has secrets... what are yours?**
