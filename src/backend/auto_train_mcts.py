import random
from single_player_mahjong import init_tiles, is_win, mcts_decision, calc_score
import csv
from functools import lru_cache
from collections import Counter
import time

# Configuration
TOTAL_GAMES = 1  # Number of games to simulate
N_SIMULATIONS = 100  # Number of MCTS simulations

dp_calls = 0  # Counter for DP function calls

# =====================
# Dynamic Programming (DP) Section
# =====================

# --- Dynamic Programming for a specific situation ---
# State: (current hand tuple, remaining wall as Counter tuple)
# Action: discard one tile from hand
# Transition: discard a tile, draw a new tile from the wall, enter new state
# Value function: minimal expected steps to win from current state
# Memoization: use lru_cache to avoid redundant computation

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
    if dp_calls % 5000 == 0:
        print(f"DP calls: {dp_calls}")
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

# Example: DP analysis for a specific hand and wall
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

# DP analysis for multiple typical hands

def analyze_typical_hands():
    """
    Analyze multiple typical mahjong hands and save results to CSV.
    """
    print("\nStarting analysis of typical hands...")
    results = []
    typical_hands = generate_typical_hands()
    # Create CSV file and write header
    with open("dp_analysis_results.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["HandType", "Hand", "Wall", "MinSteps", "Description"])
    for hand_info in typical_hands:
        print(f"\nAnalyzing {hand_info['name']}...")
        print(f"DP calls before: {dp_calls}")
        wall_counter_tuple = tuple(sorted(Counter(hand_info['wall']).items()))
        result = dp(tuple(sorted(hand_info['hand'])), wall_counter_tuple)
        print(f"DP calls after: {dp_calls}")
        # Save results
        results.append({
            'name': hand_info['name'],
            'hand': hand_info['hand'],
            'wall': hand_info['wall'],
            'min_steps': result,
            'description': hand_info['description']
        })
        # Write to CSV
        with open("dp_analysis_results.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                hand_info['name'],
                hand_info['hand'],
                hand_info['wall'],
                result,
                hand_info['description']
            ])
    print("\nAll hand analysis completed! Results saved to dp_analysis_results.csv")
    return results

def generate_typical_hands():
    """Generate typical hands for 8-tile single player mahjong"""
    hands = []
    
    # 1. Different pair types and positions
    # Man tiles pairs (9-17)
    for pair in range(9, 18):  # All man tiles
        # Pair at front
        # hands.append({
        #     'name': f'Man-Pair-{pair}-Front',
        #     'hand': [pair, pair, 10, 11, 12, 13, 14, 15],
        #     'wall': [16, 17, 28, 29, 30, 32, 33],  # Full wall for full analysis
        #     'description': f'Hand with man tile pair {pair} at front and two chows'
        # })
        hands.append({
            'name': f'Man-Pair-{pair}-Front',
            'hand': [pair, pair, 10, 11, 12, 13, 14, 15],
            # 'wall': [16, 17, 28, 29, 30, 32, 33],  # Full wall for full analysis
            # 'wall': [16, 17],  # For 2-tile wall
            'wall': [16],        # For 1-tile wall, minimal DP test
            'description': f'Hand with man tile pair {pair} at front and two chows'
        })
        # Pair in middle
        hands.append({
            'name': f'Man-Pair-{pair}-Middle',
            'hand': [10, 11, 12, pair, pair, 13, 14, 15],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with man tile pair {pair} in middle and two chows'
        })
        # Pair at back
        hands.append({
            'name': f'Man-Pair-{pair}-Back',
            'hand': [10, 11, 12, 13, 14, 15, pair, pair],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with man tile pair {pair} at back and two chows'
        })
    
    # Wind tiles pairs (27-30)
    for pair in range(27, 31):  # All wind tiles
        # Pair at front
        hands.append({
            'name': f'Wind-Pair-{pair}-Front',
            'hand': [pair, pair, 10, 11, 12, 13, 14, 15],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with wind tile pair {pair} at front and two chows'
        })
        # Pair in middle
        hands.append({
            'name': f'Wind-Pair-{pair}-Middle',
            'hand': [10, 11, 12, pair, pair, 13, 14, 15],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with wind tile pair {pair} in middle and two chows'
        })
        # Pair at back
        hands.append({
            'name': f'Wind-Pair-{pair}-Back',
            'hand': [10, 11, 12, 13, 14, 15, pair, pair],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with wind tile pair {pair} at back and two chows'
        })
    
    # Dragon tiles pairs (31-33)
    for pair in range(31, 34):  # All dragon tiles
        # Pair at front
        hands.append({
            'name': f'Dragon-Pair-{pair}-Front',
            'hand': [pair, pair, 10, 11, 12, 13, 14, 15],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with dragon tile pair {pair} at front and two chows'
        })
        # Pair in middle
        hands.append({
            'name': f'Dragon-Pair-{pair}-Middle',
            'hand': [10, 11, 12, pair, pair, 13, 14, 15],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with dragon tile pair {pair} in middle and two chows'
        })
        # Pair at back
        hands.append({
            'name': f'Dragon-Pair-{pair}-Back',
            'hand': [10, 11, 12, 13, 14, 15, pair, pair],
            'wall': [16, 17, 28, 29, 30, 32, 33],
            'description': f'Hand with dragon tile pair {pair} at back and two chows'
        })
    
    # 2. Different chow combinations
    # Consecutive chows
    hands.append({
        'name': 'Consecutive-Chows',
        'hand': [9, 10, 11, 10, 11, 12, 27, 27],
        'wall': [13, 14, 15, 16, 17, 28, 29, 30, 31],
        'description': 'Hand with consecutive chows and a pair'
    })
    
    # Separated chows
    hands.append({
        'name': 'Separated-Chows',
        'hand': [9, 10, 11, 15, 16, 17, 27, 27],
        'wall': [12, 13, 14, 28, 29, 30, 31, 32, 33],
        'description': 'Hand with separated chows and a pair'
    })
    
    # 3. Different waiting tiles
    # Multiple waiting tiles
    hands.append({
        'name': 'Multiple-Waiting',
        'hand': [9, 10, 11, 12, 13, 14, 15, 16],
        'wall': [17, 17, 27, 27, 28, 28, 29, 29, 30, 30],
        'description': 'Hand that can win with multiple tiles'
    })
    
    # Near winning hand
    hands.append({
        'name': 'Near-Winning',
        'hand': [9, 10, 11, 12, 13, 14, 27, 27],
        'wall': [15],
        'description': 'Hand that needs only one tile to win'
    })
    
    # return hands  # Uncomment this line to restore full analysis
    # return hands[:10]  # For small-scale testing
    return hands[:1]  # For minimal DP testing, only analyze the first hand

# =====================
# Monte Carlo Tree Search (MCTS) Section
# =====================

if __name__ == "__main__":
    # First analyze multiple typical hands
    dp_results = analyze_typical_hands()
    
    # Then run MCTS simulation
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

