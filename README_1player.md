# Single Player Mahjong

A simplified single-player version of Mahjong implemented in Python with a web interface and AI-powered move suggestions.

## Features
- 32-tile simplified Mahjong set (including 1-9 manzu, East/South/West/North winds, and Green/Red/White dragons, each appearing twice)
- 8-tile hand size
- Web-based interface
- Monte Carlo Tree Search (MCTS) AI for move suggestions
- Dynamic Programming (DP) for optimal strategy analysis
- Real-time game state updates
- Winning hand detection
- Automatic training and simulation capabilities

## Game Rules (Quick Overview)
- Start with 8 tiles
- Draw and discard one tile each turn
- Win by forming specific patterns:
  - Two sequences (chows) + one pair
- Special bonus: +10 points for all-manzu hands

## Tile Set

Below are the 16 unique tiles used in this simplified Mahjong (each appears twice in the set):

**Characters (Manzu, 万子):**
<img src="img/tiles/small/9.jpg" width="40"/> <img src="img/tiles/small/10.jpg" width="40"/> <img src="img/tiles/small/11.jpg" width="40"/> <img src="img/tiles/small/12.jpg" width="40"/> <img src="img/tiles/small/13.jpg" width="40"/> <img src="img/tiles/small/14.jpg" width="40"/> <img src="img/tiles/small/15.jpg" width="40"/> <img src="img/tiles/small/16.jpg" width="40"/> <img src="img/tiles/small/17.jpg" width="40"/>

1 (C1)   2 (C2)   3 (C3)   4 (C4)   5 (C5)   6 (C6)   7 (C7)   8 (C8)   9 (C9)

**Winds (风牌):**
<img src="img/tiles/small/27.jpg" width="40"/> <img src="img/tiles/small/28.jpg" width="40"/> <img src="img/tiles/small/29.jpg" width="40"/> <img src="img/tiles/small/30.jpg" width="40"/>
East (东)   South (南)   West (西)   North (北)

**Dragons (三元牌):**
<img src="img/tiles/small/31.jpg" width="40"/> <img src="img/tiles/small/32.jpg" width="40"/> <img src="img/tiles/small/33.jpg" width="40"/>
Green (绿/发)   Red (红/中)   White (白)

---

## Game Rules
- Each player starts with 8 tiles.
- On each turn, draw one tile and discard one tile.
- The goal is to form a winning hand consisting of:
  - Two sequences (chows, e.g., 1-2-3 of Characters)
  - One pair (two identical tiles)
- Special bonus: +10 points for an all-Characters (Manzu) hand.

## Winning Patterns
- **Sequence (Chow, 顺子):** Three consecutive Characters tiles (e.g., 9-10-11)
- **Pair (对子):** Two identical tiles (e.g., 27-27)
- **Winning Hand Example:** 9-10-11, 12-13-14, 27-27 (two chows + one pair)

## Mathematical Foundations: Markov Decision Process & Bellman Equation

This project's AI and optimal strategy analysis are grounded in the theory of Markov Decision Processes (MDP) and the Bellman Equation:

- **Markov Decision Process (MDP):**  
  The game is modeled as a sequence of states (the current hand and remaining wall), actions (discarding a tile), and stochastic transitions (drawing a new tile). The Markov property holds: the next state depends only on the current state and action, not on the sequence of events that preceded it.

- **Bellman Equation:**  
  The Dynamic Programming (DP) approach recursively computes the value of each state (expected minimal steps to win) using the Bellman optimality principle:
  $$
  V(s) = \min_{a} \mathbb{E}_{s'}[1 + V(s')]
  $$
  where $V(s)$ is the value of state $s$, $a$ is an action (discard), and $s'$ is the next state after drawing a tile.

- **Monte Carlo Tree Search (MCTS):**  
  MCTS approximates the value function and optimal policy by simulating many random playouts from the current state, which is especially useful when the state space is too large for exact DP.

These mathematical foundations ensure that the AI's strategy is both theoretically sound and practically effective.

---

## Project Structure
- `_1_single_player_mahjong.py`: Core game logic and AI implementation
- `_2_app.py`: Flask web server and API endpoints
- `templates/_3_index.html`: Web interface
- `img/tiles/`: Mahjong tile images
- `_5_requirements.txt`: Project dependencies
- `_6_auto_train_mcts.py`: Automatic training and simulation script

## Setup
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

## AI Features
### Monte Carlo Tree Search (MCTS)
- Provides move suggestions based on simulations
- Shows expected steps to win
- Displays win rate statistics
- Configurable simulation depth

### Dynamic Programming (DP)
- Analyzes optimal strategy for specific game states
- Calculates minimal expected steps to win
- Supports both full analysis and specific situation analysis
- Progress tracking with call counter

## Training and Simulation
The `_6_auto_train_mcts.py` script provides:
- Automatic game simulation
- Win rate statistics
- Step count analysis
- Score tracking
- CSV export of results

## API Endpoints
- `/`: Main game interface
- `/api/new_game`: Start a new game
- `/api/discard/<tile>`: Discard a tile and draw a new one

## Latest Updates
- Added DP-based optimal strategy analysis
- Implemented progress tracking for long computations
- Enhanced MCTS with better move suggestions
- Added CSV export for simulation results
- Upgraded to 8-tile hands for better strategy

## Dependencies
- Flask
- Flask-Session
- Pillow (for image handling)
- Python 3.6+ 