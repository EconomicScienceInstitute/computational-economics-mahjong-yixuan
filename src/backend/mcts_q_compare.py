import csv
import os
from single_player_mahjong import mcts_decision, get_qingyise_tingpai, calc_score, is_win
from q_learning import QLearningAgent

# Experiment parameters
N_GAMES = 20  # Number of test games for each method
N_SIM = 200   # Number of MCTS simulations per decision (keep small for speed)

# Prepare Q-learning agent (assume already trained or train here)
q_agent = QLearningAgent(alpha=0.2, gamma=0.9, epsilon=0.2)
print("Training Q-learning agent for experiment...")
q_agent.learn(episodes=1000)
print(f"Q-table size: {len(q_agent.q_table)}")

# Prepare CSV for saving results
results_path = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'mcts_q_compare_results.csv')
results_path = os.path.abspath(results_path)
os.makedirs(os.path.dirname(results_path), exist_ok=True)
file_exists = os.path.isfile(results_path)
with open(results_path, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
        writer.writerow([
            'Method', 'Game', 'Hand', 'Steps', 'Base Score', 'Bonus', 'Total Score', 'Details', 'Win'
        ])

    # Run original MCTS (no Q-learning)
    print("\nRunning original MCTS...")
    for game in range(N_GAMES):
        hand, wall = get_qingyise_tingpai()
        steps = 0
        orig_hand = hand.copy()
        while True:
            if len(hand) == 8 and is_win(hand):
                score, base_score, bonus, details = calc_score(hand, steps)
                print(f"[MCTS] Game {game+1}: Win in {steps} steps, Score: {score}, Bonus: {bonus}")
                print("DEBUG: Winning hand for bonus check:", hand)
                writer.writerow([
                    'MCTS', game+1, ' '.join(map(str, sorted(hand))), steps, base_score, bonus, score, '; '.join(details), 1
                ])
                break
            if not wall:
                print(f"[MCTS] Game {game+1}: No win.")
                writer.writerow([
                    'MCTS', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=N_SIM, q_agent=None)
            if discard is None or discard not in hand:
                writer.writerow([
                    'MCTS', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            hand.remove(discard)
            draw = wall.pop(0)
            hand.append(draw)
            steps += 1

    # Run MCTS with Q-learning-guided rollout
    print("\nRunning MCTS with Q-learning-guided rollout...")
    for game in range(N_GAMES):
        hand, wall = get_qingyise_tingpai()
        steps = 0
        orig_hand = hand.copy()
        while True:
            if len(hand) == 8 and is_win(hand):
                score, base_score, bonus, details = calc_score(hand, steps)
                print(f"[MCTS+Q] Game {game+1}: Win in {steps} steps, Score: {score}, Bonus: {bonus}")
                print("DEBUG: Winning hand for bonus check:", hand)
                writer.writerow([
                    'MCTS+Q', game+1, ' '.join(map(str, sorted(hand))), steps, base_score, bonus, score, '; '.join(details), 1
                ])
                break
            if not wall:
                print(f"[MCTS+Q] Game {game+1}: No win.")
                writer.writerow([
                    'MCTS+Q', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=N_SIM, q_agent=q_agent)
            if discard is None or discard not in hand:
                writer.writerow([
                    'MCTS+Q', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            hand.remove(discard)
            draw = wall.pop(0)
            hand.append(draw)
            steps += 1

print("\nExperiment finished. Results saved to results/mcts_q_compare_results.csv") 