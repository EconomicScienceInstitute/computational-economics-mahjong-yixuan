# Single Player Mahjong

A simplified single-player version of Mahjong implemented in Python with a web interface.

## Features
- 32-tile simplified Mahjong set
- Web-based interface
- Monte Carlo Tree Search AI for move suggestions
- Real-time game state updates
- Winning hand detection

## Files
- `single_player_mahjong.py`: Core game logic and AI
- `app.py`: Flask web server and API endpoints
- `templates/index.html`: Web interface
- `img/tiles/`: Mahjong tile images
- `requirements.txt`: Project dependencies

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

3. Open browser and navigate to:
```
http://localhost:8080
```

## Game Rules
- Start with 7 tiles
- Draw and discard one tile each turn
- Win by forming specific patterns:
  - 123 + 333 + pair
  - 222 + 333 + pair
  - Four of a kind (4444)

## API Endpoints
- `/`: Main game interface
- `/api/new_game`: Start a new game
- `/api/discard/<tile>`: Discard a tile and draw a new one

## Dependencies
- Flask
- Flask-Session
- Pillow (for image handling) 