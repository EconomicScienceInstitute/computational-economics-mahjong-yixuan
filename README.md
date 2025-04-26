# Mahjong AI System Design Document

## 1. Project Overview

### 1.1 Project Goals
- Implement a Mahjong AI system based on Dynamic Programming
- Model Mahjong decision-making using Markov Decision Process (MDP)
- Optimize strategy selection using Bellman equation
- Support human-AI gameplay (0-4 human players)

### 1.2 Technology Stack
- Backend: Python
  * FastAPI (Web Framework)
  * NumPy (Vectorized Computation)
  * WebSocket (Real-time Communication)
- Performance Analysis:
  * line_profiler (Code Performance Analysis)
  * memory_profiler (Memory Usage Analysis)

### 1.3 Core Features
1. **Basic Game System**
   - Tile representation and management
   - Game state tracking
   - Rule validation (winning hands, ready hands)

2. **AI Decision System**
   - State evaluation
   - Action selection
   - Strategy optimization

3. **Performance Optimization**
   - State space compression
   - Computation result caching
   - Vectorized operations

## 2. Theoretical Foundation

### 2.1 MDP (Markov Decision Process)
The core challenge of Mahjong AI is to select optimal actions at each decision point based on the current state. MDP provides a mathematical framework to solve this sequential decision-making problem:

1. **Markov Property**: The next state depends only on the current state and action, independent of history
   - Example: Current hand + visible tiles contain all information needed for decision making
   
2. **State Transition**: Each action leads to state transitions with certain probabilities
   - Example: After discarding a tile, the next drawn tile is random
   
3. **Immediate Rewards**: Each state transition has an associated reward value
   - Example: Forming a sequence yields positive reward, breaking a potential set yields negative reward

#### State Space (S)
- **Hand State**: [t1, t2, ..., tn] where ti represents each tile
- **Visible Information**: 
  * Discarded tiles by all players
  * Exposed melds (Chi/Pon)
- **Game Progress**: 
  * Remaining tile count
  * Current round/wind

#### Action Space (A)
- **Discard Actions**: Choose one tile to discard
- **Meld Actions**:
  * Chi (Sequence formation)
  * Pon (Triplet formation)
- **Special Actions**:
  * Declare win
  * Skip (Pass on opponent's discard)

#### Transition Probability (P)
P(s'|s,a) = P(draw) * P(opponents_actions)
where:
- P(draw): Probability of drawing each possible tile
  * Based on visible tiles and remaining count
- P(opponents_actions): Probability of opponent actions
  * Estimated from visible discards and exposed melds

#### Reward Function (R)
R(s,a,s') = Immediate_Value + Potential_Value
where:
- Immediate_Value:
  * Complete set (sequence/triplet): +3
  * Partial set progress: +1
  * Breaking existing set: -2
  * Ready hand formation: +5
- Potential_Value:
  * Tile efficiency (flexibility for future sets)
  * Distance to ready hand
  * Safety consideration (avoid dangerous discards)

### 2.2 Bellman Equation and Dynamic Programming

The Bellman equation is the core tool for solving MDP problems. It expresses a key idea: the value of a state under optimal policy can be calculated recursively.

1. **Core Concept**:
   - State value = Immediate reward + Discounted sum of future values
   - Using recursion to break down long-term decisions into a series of single-step decisions

2. **Mathematical Expression**:
   V(s) = max_a[R(s,a) + γ * Σ P(s'|s,a)V(s')]
   - V(s): Value of state s
   - R(s,a): Immediate reward for action a
   - γ: Discount factor (0.8-0.95)
   - P(s'|s,a): State transition probability
   - V(s'): Value of next state

3. **Application in Mahjong**:
   - Evaluate the value of each tile discard option
   - Balance immediate gains (e.g., forming a sequence) vs long-term benefits (e.g., ready hand opportunity)
   - Find optimal discard strategy through iterative calculation

#### Implementation Details
For each state s and action a:
1. Calculate immediate reward R(s,a)
2. Estimate transition probabilities P(s'|s,a)
3. Update value function:
   V(s) = max_a[R(s,a) + γ * Σ P(s'|s,a)V(s')]

#### Value Iteration Process
1. Initialize V0(s) = 0 for all states
2. For each iteration k:
   Vk+1(s) = max_a[R(s,a) + γ * Σ P(s'|s,a)Vk(s')]
3. Continue until ||Vk+1 - Vk|| < ε

### 2.3 Dynamic Programming Methods

#### State Value Calculation
1. **Value Iteration**:
   - Iteratively update state values
   - Use Bellman equation for updates
   - Stop when convergence reached

2. **Policy Iteration**:
   - Alternate between policy evaluation and improvement
   - More stable but slower than value iteration

3. **Monte Carlo Simulation**:
   - Sample-based approach
   - Good for high-dimensional state spaces
   - Used for initial value estimation

#### Strategy Optimization
1. **Value-based Selection**:
   - Choose actions that maximize expected value
   - Consider both immediate and future rewards

2. **Balance Considerations**:
   - Exploration vs exploitation
   - Risk vs reward
   - Offensive vs defensive play

## 3. System Flow Diagrams

**Flowchart Legend:**
- Pink nodes (🟪): Initial states
- Blue nodes (🟦): Processing steps and decision points
- Green nodes (🟩): Final results/actions

### 3.1 Basic Game Flow
```
[Game Start] -> [Deal] -> [Turn Start] -> [AI/Player Action] -> [Discard] -> [Win Check] -> [Turn End]
                                         ^                                                    |
                                         |____________________________________________________|
```

### 3.2 AI Decision Flow (Detailed Decision Tree)

```mermaid
flowchart TD
    A[Current Game State] --> B{Winning Hand?}
    B -->|Yes| C[Win Game]
    B -->|No| D{Ready Hand?}
    
    D -->|Yes| E[Defensive Play]
    D -->|No| F{Evaluate Hand}
    
    F --> G[Calculate Immediate Value]
    F --> H[Estimate Future Value]
    
    G --> I{Choose Action}
    H --> I
    
    I --> J[Form Sequence]
    I --> K[Form Triplet]
    I --> L[Prepare Ready Hand]
    I --> M[Defensive Discard]
    
    J --> N[Execute Action]
    K --> N
    L --> N
    M --> N
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
    style N fill:#bfb,stroke:#333,stroke-width:2px
```

### 3.3 State Value Calculation Flow

```mermaid
flowchart TD
    A[State] --> B[Calculate]
    B --> C[Action Loop]
    C --> D[Simulate]
    D --> E[Value]
    E --> F[Update]
    F --> C
    F --> G[Max Value]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bfb,stroke:#333,stroke-width:2px
```

### 3.4 State Transition Example
```
Current Hand    Action(Discard 8 Characters)    New State(After Draw)
[1,1,1,8,8] -> [1,1,1,8]                    -> [1,1,1,8,?]
Rewards:
- Maintain sequence +1
- Break pair -1
- Ready hand opportunity +2
```

### 3.5 Tile Notation

In Mahjong, there are three suits (Characters, Circles/Dots, and Bamboo) and two types of honor tiles (Winds and Dragons). Each tile has a unique notation for easy reference.

#### Characters (万)
- Notation: 1-9 with 'C' suffix (e.g., 1C, 2C)
- Complete set (1-9):
  
  ![1 Character](img/tiles/small/9.jpg) ![2 Character](img/tiles/small/10.jpg) ![3 Character](img/tiles/small/11.jpg) ![4 Character](img/tiles/small/12.jpg) ![5 Character](img/tiles/small/14.jpg) ![6 Character](img/tiles/small/15.jpg) ![7 Character](img/tiles/small/16.jpg) ![8 Character](img/tiles/small/17.jpg) ![9 Character](img/tiles/small/18.jpg)

#### Circles/Dots (筒)
- Notation: 1-9 with 'D' suffix (e.g., 1D, 2D)
- Complete set (1-9):
  
  ![1 Dot](img/tiles/small/18.jpg) ![2 Dot](img/tiles/small/19.jpg) ![3 Dot](img/tiles/small/20.jpg) ![4 Dot](img/tiles/small/21.jpg) ![5 Dot](img/tiles/small/22.jpg) ![6 Dot](img/tiles/small/23.jpg) ![7 Dot](img/tiles/small/24.jpg) ![8 Dot](img/tiles/small/25.jpg) ![9 Dot](img/tiles/small/26.jpg)

#### Bamboo (条)
- Notation: 1-9 with 'B' suffix (e.g., 1B, 2B)
- Complete set (1-9):
  
  ![1 Bamboo](img/tiles/small/0.jpg) ![2 Bamboo](img/tiles/small/1.jpg) ![3 Bamboo](img/tiles/small/2.jpg) ![4 Bamboo](img/tiles/small/3.jpg) ![5 Bamboo](img/tiles/small/4.jpg) ![6 Bamboo](img/tiles/small/5.jpg) ![7 Bamboo](img/tiles/small/6.jpg) ![8 Bamboo](img/tiles/small/7.jpg) ![9 Bamboo](img/tiles/small/8.jpg)

#### Honor Tiles
- **Winds** (风牌): East (E), South (S), West (W), North (N)
  * Notation: E, S, W, N
  * Complete set:
  
  ![East](img/tiles/small/31.jpg) ![South](img/tiles/small/32.jpg) ![West](img/tiles/small/33.jpg) ![North](img/tiles/small/34.jpg)

- **Dragons** (三元牌): Red (R), Green (G), White (W)
  * Notation: R, G, W
  * Complete set:
  
  ![Red](img/tiles/small/35.jpg) ![Green](img/tiles/small/36.jpg) ![White](img/tiles/small/37.jpg)

#### Special Tiles
- **Blank Tile** (白板): Used as a wild card in some variants
  ![Blank](img/tiles/small/blank.jpg)

- **Concealed Tile** (暗牌): Represents a face-down tile
  ![Concealed](img/tiles/small/concealed.jpg)

#### Tile Combinations
1. **Sequence** (顺子): Three consecutive tiles of the same suit
   - Example: 1C-2C-3C, 4D-5D-6D, 7B-8B-9B

2. **Triplet** (刻子): Three identical tiles
   - Example: 1C-1C-1C, 5D-5D-5D, E-E-E

3. **Pair** (对子): Two identical tiles
   - Example: 2C-2C, 8D-8D, R-R