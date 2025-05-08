import random
from _1_single_player_mahjong import init_tiles, is_win, mcts_decision
import csv

TOTAL_GAMES = 1000  # Simulate 1000 games
SIMS_PER_MOVE = 10  # Keep per-move simulations at 10 for speed

win_count = 0
step_list = []

with open("steps_per_win.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Game", "Steps"])
    for game in range(TOTAL_GAMES):
        hand, wall = init_tiles()
        steps = 0
        while True:
            # Check if the hand is a winning hand
            if len(hand) == 8 and is_win(hand):
                win_count += 1
                step_list.append(steps)
                writer.writerow([game + 1, steps])  # Write after each win
                break
            # If the wall is empty, the game is over (no win)
            if not wall:
                break
            # Use MCTS to decide which tile to discard
            discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=SIMS_PER_MOVE)
            if discard is None:
                break
            hand.remove(discard)
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
    print(f"Minimum steps to win: {min(step_list)}")
    print(f"Maximum steps to win: {max(step_list)}")
else:
    print("No wins in the simulation.")

def calc_score(hand, steps):
    score = 100 - steps
    if all(9 <= t['number'] <= 17 for t in hand):  # All manzu
        score += 10
    return max(score, 0) 