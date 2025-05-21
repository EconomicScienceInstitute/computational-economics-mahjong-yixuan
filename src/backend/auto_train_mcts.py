import random
from single_player_mahjong import init_tiles, is_win, mcts_decision, calc_score
import csv
from functools import lru_cache
from collections import Counter
import time

# Configuration
TOTAL_GAMES = 10  # Number of games to simulate
N_SIMULATIONS = 100  # Number of MCTS simulations

dp_calls = 0  # Counter for DP function calls

# =====================
# Dynamic Programming (DP) Section
# =====================

@lru_cache(maxsize=None)
def dp(hand_tuple, wall_counter_tuple):
    """
    DP function to compute minimal expected steps to win from a given state.
    Args:
        hand_tuple (tuple): Current hand as a sorted tuple of tile numbers
        wall_counter_tuple (tuple): Remaining wall as tuple(sorted(Counter(wall).items()))
    Returns:
        int: Minimal expected steps to win from this state
    """
    global dp_calls
    dp_calls += 1
    wall_counter = Counter(dict(wall_counter_tuple))
    # Pruning: if not enough tiles to form a hand, return infinity
    if len(hand_tuple) + sum(wall_counter.values()) < 8:
        return float('inf')
    # Base case: already a winning hand
    if is_win(list(hand_tuple)):
        return 0
    # Base case: wall is empty, cannot win
    if not wall_counter:
        return float('inf')
    min_expected_steps = float('inf')
    # Try discarding each unique tile in hand
    for discard in set(hand_tuple):
        new_hand = list(hand_tuple)
        new_hand.remove(discard)
        # For each possible draw from the wall
        for draw in wall_counter:
            if wall_counter[draw] == 0:
                continue
            next_hand = tuple(sorted(new_hand + [draw]))
            next_wall_counter = wall_counter.copy()
            next_wall_counter[draw] -= 1
            if next_wall_counter[draw] == 0:
                del next_wall_counter[draw]
            next_wall_counter_tuple = tuple(sorted(next_wall_counter.items()))
            steps = 1 + dp(next_hand, next_wall_counter_tuple)
            if steps < min_expected_steps:
                min_expected_steps = steps
    return min_expected_steps

def q_learning_train(hand, wall, n_episodes=10000):
    """
    Train a Q-learning agent on a specific hand and wall configuration.
    """
    # Initialize Q-table
    q_table = {}
    alpha = 0.1  # learning rate
    gamma = 0.9  # discount factor
    epsilon = 0.2  # exploration rate
    
    for episode in range(n_episodes):
        h = hand[:]
        w = wall[:]
        random.shuffle(w)
        
        while not is_win(h):
            # Choose action using epsilon-greedy policy
            if random.random() < epsilon:
                discard = random.choice(h)
            else:
                # Get Q-values for current state
                state = tuple(sorted(h))
                if state not in q_table:
                    q_table[state] = {tile: 0 for tile in set(h)}
                q_values = q_table[state]
                max_q = max(q_values.values())
                best_actions = [a for a, q in q_values.items() if q == max_q]
                discard = random.choice(best_actions)
            
            # Take action and observe next state
            h.remove(discard)
            if w:
                draw = w.pop()
                h.append(draw)
            
            # Update Q-value
            state = tuple(sorted(h))
            if state not in q_table:
                q_table[state] = {tile: 0 for tile in set(h)}
            
            # Calculate reward
            reward = 1 if is_win(h) else -1
            
            # Update Q-value using Q-learning update rule
            old_value = q_table[state].get(discard, 0)
            next_max = max(q_table[state].values()) if q_table[state] else 0
            new_value = old_value + alpha * (reward + gamma * next_max - old_value)
            q_table[state][discard] = new_value
            
            if is_win(h):
                break
    
    return q_table

def q_greedy_discard(hand, q_table):
    """
    Choose the best action according to the Q-table.
    """
    state = tuple(sorted(hand))
    if state not in q_table:
        return random.choice(hand)
    q_values = q_table[state]
    max_q = max(q_values.values())
    best_actions = [a for a, q in q_values.items() if q == max_q]
    return random.choice(best_actions)

# =====================
# Monte Carlo Tree Search (MCTS) Section
# =====================

def dp_qingyise_single_case():
    """
    Run DP analysis for the same 'qingyise' (all manzu) tenpai hand as used in Q-learning/MCTS experiments.
    Prints minimal steps and optimal score for direct comparison.
    """
    # Hand: 1-8 manzu (9-16), wall: remaining manzu tiles (9-17, each 2 copies, minus hand)
    hand = [9, 10, 11, 12, 13, 14, 15, 16]  # 1-8 manzu
    wall = [i for i in range(9, 18)] * 2  # 1-9 manzu, 2 copies each
    for t in hand:
        wall.remove(t)
    from collections import Counter
    hand_tuple = tuple(sorted(hand))
    wall_counter_tuple = tuple(sorted(Counter(wall).items()))
    min_steps = dp(hand_tuple, wall_counter_tuple)
    score, base_score, combo_bonus, details = calc_score(hand, min_steps)
    print("\n=== DP Analysis for Qingyise Tenpai (same as Q-learning/MCTS) ===")
    print(f"Hand: {hand}")
    print(f"Wall: {wall}")
    print(f"Minimal steps to win (DP): {min_steps}")
    print(f"Optimal score (DP): {score} (Base: {base_score}, Bonus: {combo_bonus}, Details: {details})")

if __name__ == "__main__":
    # --- DP analysis for a specific hand and wall ---
    specific_hand = [9, 10, 11, 12, 13, 14, 27, 27]  # Example: C1-C6, East, East
    specific_wall = [9, 10, 11, 12, 13, 14, 27, 28, 29, 30, 31, 32, 33, 15, 16, 17, 28, 29, 30, 31, 32, 33, 15, 16]
    print("Running DP analysis for a specific hand and wall...")
    wall_counter_tuple = tuple(sorted(Counter(specific_wall).items()))
    result = dp(tuple(sorted(specific_hand)), wall_counter_tuple)
    print(f"Minimal expected steps to win from this specific state: {result}")
    print("DP analysis done. Starting simulation...")

    # Save DP result to CSV as the first row
    with open("steps_per_win.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # DP analysis result header
        writer.writerow(["DP_Hand", "DP_Wall", "DP_MinSteps"])
        writer.writerow([specific_hand, specific_wall, result])
        writer.writerow([])  # Empty row for separation
        # Game simulation result header
        writer.writerow(["Game", "TotalScore", "Steps", "BaseScore", "ComboBonus", "Details", "Win"])
        win_count = 0
        step_list = []
        score_list = []
        for game in range(TOTAL_GAMES):
            hand, wall = init_tiles()
            steps = 0
            game_won = False
            while True:
                # Check if the hand is a winning hand
                if len(hand) == 8 and is_win([t if isinstance(t, int) else t['number'] for t in hand]):
                    win_count += 1
                    game_won = True
                    total_score, base_score, combo_bonus, details = calc_score(hand, steps)
                    step_list.append(steps)
                    score_list.append(total_score)
                    writer.writerow([game + 1, total_score, steps, base_score, combo_bonus, "; ".join(details), 1])
                    break
                # If the wall is empty, the game is over (no win)
                if not wall:
                    total_score = 0
                    base_score = 0
                    combo_bonus = 0
                    details = ""
                    score_list.append(total_score)
                    writer.writerow([game + 1, total_score, steps, base_score, combo_bonus, details, 0])
                    break
                # Use DP optimal strategy to select the discard
                min_steps = float('inf')
                best_discard = None
                for discard in set([t if isinstance(t, int) else t['number'] for t in hand]):
                    new_hand = [t if isinstance(t, int) else t['number'] for t in hand]
                    new_hand.remove(discard)
                    wall_counter_tuple = tuple(sorted(Counter(wall).items()))
                    steps_needed = 1 + dp(tuple(sorted(new_hand)), wall_counter_tuple)
                    if steps_needed < min_steps:
                        min_steps = steps_needed
                        best_discard = discard
                # Remove the selected discard
                for idx, t in enumerate(hand):
                    tnum = t if isinstance(t, int) else t['number']
                    if tnum == best_discard:
                        hand.pop(idx)
                        break
                # Draw a new tile from the wall
                draw = wall.pop(0)

    # --- Batch DP analysis for typical hands ---
    print("\nRunning batch DP analysis for typical hands...")
    dp_results = analyze_typical_hands()
    print(f"Batch DP analysis completed. Total hands analyzed: {len(dp_results)}")
    print("Results saved to dp_analysis_results.csv")
    
    # --- MCTS simulation ---
    print("\nStarting MCTS simulation...")
    # Run games and collect statistics
    total_steps = 0
    for game in range(TOTAL_GAMES):
        print(f"\nGame {game + 1}/{TOTAL_GAMES}")
        hand, wall = init_tiles()
        steps = 0
        while len(hand) == 8 and not is_win(hand):
            suggested_discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=N_SIMULATIONS)
            if suggested_discard is None:
                print("No winning path found")
                break
            # Process the suggested move
            hand.remove(suggested_discard)
            if wall:
                new_tile = wall.pop(random.randrange(len(wall)))
                hand.append(new_tile)
                steps += 1
                print(f"Step {steps}: Discarded {suggested_discard}, Drew {new_tile}")
                print(f"Current hand: {sorted(hand)}")
            else:
                print("No more tiles in wall")
                break
        if is_win(hand):
            win_count += 1
            print(f"Won in {steps} steps!")
            total_steps += steps
        else:
            print("Did not win")
    print(f"\nResults after {TOTAL_GAMES} games:")
    print(f"Wins: {win_count}/{TOTAL_GAMES} ({win_count/TOTAL_GAMES*100:.1f}%)")
    if win_count > 0:
        print(f"Average steps to win: {total_steps/win_count:.1f}")

    dp_qingyise_single_case()

