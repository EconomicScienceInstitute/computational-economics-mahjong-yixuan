# Single Player Mahjong

A simplified single-player version of Mahjong implemented in Python with a web interface.

## 1. Features
- 32-tile simplified Mahjong set
- Web-based interface
- Monte Carlo Tree Search AI for move suggestions
- Real-time game state updates
- Winning hand detection

## 2. Files
- `_1_single_player_mahjong.py`: Core game logic and AI
- `_2_app.py`: Flask web server and API endpoints
- `templates/_3_index.html`: Web interface
- `img/tiles/`: Mahjong tile images (will be renamed to _4_tiles)
- `_5_requirements.txt`: Project dependencies

## 3. Setup
1. Install dependencies:
```bash
pip install -r _5_requirements.txt
```

2. Run the server:
```bash
python _2_app.py
```

3. Open browser and navigate to:
```
http://localhost:8080
```

## 4. Game Rules
- Start with 7 tiles
- Draw and discard one tile each turn
- Win by forming specific patterns:
  - 123 + 333 + pair
  - 222 + 333 + pair
  - Four of a kind (4444)

## 5. API Endpoints
- `/`: Main game interface
- `/api/new_game`: Start a new game
- `/api/discard/<tile>`: Discard a tile and draw a new one

## Dependencies
- Flask
- Flask-Session
- Pillow (for image handling) 