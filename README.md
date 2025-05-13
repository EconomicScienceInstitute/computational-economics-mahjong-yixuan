# Single Player Mahjong

A Python-based Mahjong AI training platform featuring:
- Monte Carlo Tree Search for real-time move suggestions
- Dynamic Programming optimization for minimal winning steps
- Web interface with interactive gameplay and move hints
- Simplified 32-tile ruleset optimized for AI learning
- Automatic game simulation and performance analysis

## Game Rules
1. **Basic Rules**
   - Use 32 tiles (16 unique tiles, each appears twice)
   - Start with 8 tiles
   - Each turn: draw one tile and discard one
   - Goal: Form a winning hand with minimal steps

2. **Winning Pattern**
   - Must have exactly 8 tiles
   - Required combinations:
     * Two sequences (each: three consecutive Character tiles, e.g., 1-2-3)
     * One pair (two identical tiles)
   - Note: Only Character tiles (1-9) can form sequences

3. **Scoring System**
   - Base Score: 100 - steps (minimum 0)
   - Combination Bonus:
     * All Characters (all tiles are 1-9 Characters) +20
   - Final score = Base score + Combination bonus

## Tile Set
Each tile appears exactly twice in the game:

**Characters (Manzu, 万子):**
1 (C1)   2 (C2)   3 (C3)   4 (C4)   5 (C5)   6 (C6)   7 (C7)   8 (C8)   9 (C9)

<img src="img/tiles/small/9.jpg" width="40"/> <img src="img/tiles/small/10.jpg" width="40"/> <img src="img/tiles/small/11.jpg" width="40"/> <img src="img/tiles/small/12.jpg" width="40"/> <img src="img/tiles/small/13.jpg" width="40"/> <img src="img/tiles/small/14.jpg" width="40"/> <img src="img/tiles/small/15.jpg" width="40"/> <img src="img/tiles/small/16.jpg" width="40"/> <img src="img/tiles/small/17.jpg" width="40"/>

**Winds (风牌):**
East (东)   South (南)   West (西)   North (北)

<img src="img/tiles/small/27.jpg" width="40"/> <img src="img/tiles/small/28.jpg" width="40"/> <img src="img/tiles/small/29.jpg" width="40"/> <img src="img/tiles/small/30.jpg" width="40"/>

**Dragons (三元牌):**
Green (绿/发)   Red (红/中)   White (白)

<img src="img/tiles/small/31.jpg" width="40"/> <img src="img/tiles/small/32.jpg" width="40"/> <img src="img/tiles/small/33.jpg" width="40"/>

## Winning Pattern Examples
A winning hand requires two sequences (in Characters) and one pair:
- Valid sequences: Any three consecutive Characters (1-2-3, 2-3-4, ..., 7-8-9)
- Valid pairs: Any two identical tiles (Characters, Winds, or Dragons)

Example:
- Sequence 1: (1-2-3) 
<img src="img/tiles/small/9.jpg" width="30"/> <img src="img/tiles/small/10.jpg" width="30"/> <img src="img/tiles/small/11.jpg" width="30"/> 
- Sequence 2: (4-5-6)
<img src="img/tiles/small/12.jpg" width="30"/> <img src="img/tiles/small/13.jpg" width="30"/> <img src="img/tiles/small/14.jpg" width="30"/> 
- Pair: (East-East)
<img src="img/tiles/small/27.jpg" width="30"/> <img src="img/tiles/small/27.jpg" width="30"/> 

Bonus: +20 points if all tiles are Characters

## Core Implementation
1. **Key Functions**
   - `init_tiles()`: Initialize game with 8 random tiles
   - `is_ready()`: Check if hand is ready to win (tingpai)
   - `is_win()`: Check if hand is winning
   - `mcts_decision()`: AI decision using Monte Carlo Tree Search
   - `shanten()`: Calculate steps away from winning
   - `calc_score()`: Calculate final score

2. **AI Strategy**
   - For each possible discard:
     * Simulates thousands of games
     * Records win rate and average steps to win
   - Suggests the move with highest chance of quick win
   - Shows expected steps needed and win probability

## Mathematical Foundations: MDP, BE, DP & MCTS
The AI strategy is based on:
- **Markov Decision Process (MDP)**: Models the game as states (current hand) and actions (discards)
- **Bellman Equation (BE)**: \[ V(s) = \min_{a} \mathbb{E}_{s'}[1 + V(s')] \]
  * V(s): Expected steps to win from state s
  * a: Possible discard actions
  * s': Next state after drawing a tile
- **Dynamic Programming (DP)**: Solves Bellman equation recursively for optimal value function
- Implementation: Uses **Monte Carlo Tree Search (MCTS)** to approximate solutions through simulation

### Dynamic Programming Implementation Details
- **State:** (current hand tuple, remaining wall tuple)
- **Action:** Discard one tile from hand
- **Transition:** Discard a tile, draw a new tile from the wall, enter new state
- **Value function:** Minimal expected steps to win from current state
- **Memoization:** Use lru_cache to avoid redundant computation

## Project Structure
- `single_player_mahjong.py`: Core game logic and AI
- `app.py`: Web server and API
- `_3_index.html`: Web interface
- `_6_auto_train_mcts.py`: Training script


## AI Implementation
### Monte Carlo Tree Search (MCTS)
- Real-time move suggestions through game simulation
- Win probability estimation
- Expected steps to win calculation
- Configurable simulation depth and parameters

### Dynamic Programming (DP)
- Optimal strategy analysis for game states
- Minimal steps calculation using Bellman equation
- Full state space analysis capability
- Progress tracking for long computations

### Training and Analysis
The `_6_auto_train_mcts.py` script provides:
- Automated game simulations
- Performance metrics collection
- Strategy effectiveness analysis
- CSV export for detailed analysis 

## Setup and Run
1. Dependencies:
```bash
# Install required packages
pip3 install -r _5_requirements.txt
```
Required packages:
- Flask: Web server framework
- Flask-Session: Session management
- Pillow: Image processing
- Python 3.6+

2. Start Server:
```bash
python3 app.py
```

3. Access Game:
- Open browser: `http://127.0.0.1:8080`
- Available routes:
  * `/`: Main game interface
  * `/api/new_game`: Start a new game
  * `/api/discard/<tile>`: Process tile discard
