import random
from _1_single_player_mahjong import init_tiles, is_win, mcts_decision
import csv
from functools import lru_cache

TOTAL_GAMES = 1000  # Number of games to simulate
SIMS_PER_MOVE = 10  # Number of MCTS simulations per move

win_count = 0
step_list = []
score_list = []

dp_calls = 0  # Global counter for DP calls

# Scoring function: steps + all-manzu bonus
def calc_score(hand, steps):
    score = 100 - steps
    # Support both dict and int tile representations
    def tile_num(t):
        return t['number'] if isinstance(t, dict) else t
    if all(9 <= tile_num(t) <= 17 for t in hand):
        score += 10
    return max(score, 0)

# --- Dynamic Programming for a specific situation ---
# State: (current hand tuple, remaining wall tuple)
# Action: discard one tile from hand
# Transition: discard a tile, draw a new tile from the wall, enter new state
# Value function: minimal expected steps to win from current state
# Memoization: use lru_cache to avoid redundant computation

@lru_cache(maxsize=None)
def dp(hand_tuple, wall_tuple):
    global dp_calls
    dp_calls += 1
    if dp_calls % 10000 == 0:
        print(f"DP calls: {dp_calls}")
    # Base case: already a winning hand
    if is_win(list(hand_tuple)):
        return 0  # 0 steps needed if already win
    # Base case: wall is empty, cannot win
    if not wall_tuple:
        return float('inf')

    min_expected_steps = float('inf')
    # Try discarding each unique tile in hand
    for discard in set(hand_tuple):
        # Remove the discard tile from hand
        new_hand = list(hand_tuple)
        new_hand.remove(discard)
        # For each possible draw from the wall
        for i, draw in enumerate(wall_tuple):
            # Add the drawn tile to hand
            next_hand = tuple(sorted(new_hand + [draw]))
            # Remove the drawn tile from wall
            next_wall = wall_tuple[:i] + wall_tuple[i+1:]
            # Recursively compute expected steps for the new state
            steps = 1 + dp(next_hand, next_wall)
            # Take the minimum expected steps over all possible draws
            if steps < min_expected_steps:
                min_expected_steps = steps
    return min_expected_steps

# Example: DP analysis for a specific hand and wall
# You can change these values to analyze different situations
specific_hand = [9, 10, 11, 12, 13, 14, 27, 27]  # Example: C1-C6, East, East
specific_wall = [9, 10, 11, 12, 13, 14, 27, 28, 29, 30, 31, 32, 33, 15, 16, 17, 28, 29, 30, 31, 32, 33, 15, 16]
print("Running DP analysis for a specific hand and wall...")
result = dp(tuple(sorted(specific_hand)), tuple(sorted(specific_wall)))
print(f"Minimal expected steps to win from this specific state: {result}")
print("DP analysis done. Starting simulation...")

with open("steps_per_win.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Game", "Steps", "Score", "Win"])
    for game in range(TOTAL_GAMES):
        hand, wall = init_tiles()
        steps = 0
        game_won = False
        while True:
            # Check if the hand is a winning hand
            if len(hand) == 8 and is_win([t if isinstance(t, int) else t['number'] for t in hand]):
                win_count += 1
                game_won = True
                score = calc_score(hand, steps)
                step_list.append(steps)
                score_list.append(score)
                writer.writerow([game + 1, steps, score, 1])  # Write after each win
                break
            # If the wall is empty, the game is over (no win)
            if not wall:
                score = 0
                score_list.append(score)
                writer.writerow([game + 1, steps, score, 0])
                break
            # For each possible discard, simulate and select by priority
            best_discard = None
            best_tuple = (float('inf'), float('-inf'), float('-inf'))  # (steps, score, win_rate)
            for discard in set([t if isinstance(t, int) else t['number'] for t in hand]):
                sim_hand = [t if isinstance(t, int) else t['number'] for t in hand]
                sim_hand.remove(discard)
                sim_wall = wall.copy()
                random.shuffle(sim_wall)
                sim_steps = 0
                temp_hand = sim_hand.copy()
                temp_wall = sim_wall.copy()
                win = False
                # Simulate until win or wall is empty
                while temp_wall and sim_steps < 30:
                    draw = temp_wall.pop(0)
                    temp_hand.append(draw)
                    sim_steps += 1
                    for possible_discard in temp_hand:
                        test_hand = temp_hand.copy()
                        test_hand.remove(possible_discard)
                        if is_win(test_hand):
                            win = True
                            break
                    if win:
                        break
                    if len(temp_hand) > 8:
                        temp_hand.remove(random.choice(temp_hand))
                sim_score = calc_score(temp_hand, sim_steps) if win else 0
                win_rate = 1 if win else 0
                # Priority: minimal steps, then highest score, then win
                candidate = (sim_steps if win else float('inf'), sim_score, win_rate)
                if candidate < best_tuple:
                    best_tuple = candidate
                    best_discard = discard
            if best_discard is None:
                # No valid move, break
                score = 0
                score_list.append(score)
                writer.writerow([game + 1, steps, score, 0])
                break
            # Remove the selected discard
            for idx, t in enumerate(hand):
                tnum = t if isinstance(t, int) else t['number']
                if tnum == best_discard:
                    hand.pop(idx)
                    break
            # Draw a new tile from the wall
            draw = wall.pop(0)
            hand.append(draw)
            steps += 1
        if (game + 1) % 10 == 0:
            print(f"Simulated {game + 1} games...")

print(f"Total games: {TOTAL_GAMES}")
print(f"Number of wins: {win_count}")
print(f"Win rate: {win_count / TOTAL_GAMES:.2%}")
if win_count > 0:
    print(f"Average steps to win: {sum(step_list) / win_count:.2f}")
    print(f"Average score: {sum(score_list) / TOTAL_GAMES:.2f}")
    print(f"Minimum steps to win: {min(step_list)}")
    print(f"Maximum steps to win: {max(step_list)}")
else:
    print("No wins in the simulation.")

print(f"Total score: {sum(score_list)}") 