# Single Player Mahjong

## About Mahjong

1. Mahjong originated in the Qing Dynasty (around 1840) in China.
2. The four directions (East, South, West, North) form a complete circle of the universe.
3. Character tiles (1-9) progress from unity to longevity, representing the cosmic order.
4. The three Dragon tiles are: Red Dragon (center of the universe), Green Dragon (prosperity), and White Dragon (purity).

**In oriental philosophy, their combination embodies Harmony.**

## Project Overview

A Python-based Single Player Mahjong:

- Simplified 32-tile ruleset optimized
- Monte Carlo Tree Search (MCTS) and Q-learning for automated strategy optimization
- Dynamic Programming for minimal winning steps analysis
- Web interface for interactive single-player Mahjong gameplay
- Automatic game simulation, result saving, and performance analysis
- This is a **must-win game**: every deal is theoretically winnable with optimal play

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

## Mathematical Foundations: MDP, BE, DP & MCTS


- **Markov Decision Process (MDP)**: 
- **State:** The current state is defined by the player's hand, the remaining tiles in the wall, and, if needed, the game history for more advanced analysis.
- **Action:** At each step, the player chooses which tile to discard from their hand.
- **Transition (STEP):** After discarding a tile, the player draws a new tile from the wall, resulting in a new state.
- **Value function (Reward):** The objective is to win in the fewest possible steps and achieve the highest possible score.
No points are awarded during intermediate steps; only the final hand is scored.
When a winning hand is achieved, the score is calculated as 100 minus the number of steps taken, plus a 20-point bonus for a straight (all Character tiles). If the player cannot win or the wall is empty, the score is zero.

**Score Calculation Matrix**
| Steps Taken | Base Score (100 - Steps) | All Character Tiles Bonus | Final Score (if all Characters) |
|:-----------:|:-----------------------:|:------------------------:|:-------------------------------:|
|      0      |          100            |           +20            |             120                 |
|      1      |           99            |           +20            |             119                 |
|      2      |           98            |           +20            |             118                 |
|      5      |           95            |           +20            |             115                 |
|     10      |           90            |           +20            |             110                 |
|     20      |           80            |           +20            |             100                 |
|     50      |           50            |           +20            |              70                 |
|    100      |            0            |           +20            |              20                 |


- **Bellman Equation (BE):**
  - $V(s) = \min_a E_{s'}[1 + V(s')]$
  - $V(s)$: Expected steps to win from state $s$
  - $a$: Possible discard actions
  - $s'$: Next state after drawing a tile
- Implementation: Uses **Monte Carlo Tree Search (MCTS)** to approximate solutions through simulation
- **Dynamic Programming (DP)**: Solves Bellman equation recursively for optimal value function
- **Memoization:** Use lru_cache to avoid redundant computation


## Project Structure
- `single_player_mahjong.py`: Core game logic and AI
- `app.py`: Web server and API
- `index.html`: Web interface
- `auto_train_mcts.py`: Training script

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
The `auto_train_mcts.py` script provides:
- Automated game simulations
- Performance metrics collection
- Strategy effectiveness analysis
- CSV export for detailed analysis 

## Setup and Run
1. Dependencies:
```bash
# Install required packages
pip3 install -r requirements.txt
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

## Testing

### Unit Test (A)
Test the hand-winning logic (`is_win`) with a variety of hands:
```bash
python3 test/test_is_win.py
```
All test cases should show `PASS`.

### Integration Test (B)
Simulate a full single-player mahjong game with random tiles, AI decision, and scoring:
```bash
python3 test/test_integration_game.py
```
You will see the full game process and final result.

### Regression Test (C)
(Optional) Run all tests at once:
```bash
python3 test/run_all_tests.py
```
This will automatically run all test scripts.

### Adding New Tests
- To add new hand patterns for `is_win`, edit `test/test_is_win.py`.
- To test specific game flows, modify or extend `test/test_integration_game.py`.

### Notes
- All tests are self-contained and require only Python 3 and the dependencies in `requirements.txt`.
- Each time you change core logic, please rerun all tests to ensure correctness.
