import csv
import os
from single_player_mahjong import mcts_decision, get_qingyise_tingpai, get_man_wind_tingpai, get_man_dragon_tingpai, calc_score, is_win
from q_learning import QLearningAgent
import pandas as pd
import sys

def main():
    # Experiment parameters
    N_GAMES = 100  # Number of test games for each method (per hand type, changed from 100 to 20)
    N_SIM = 200   # Number of MCTS simulations per decision (keep small for speed)

    # Parse hand type from command line
    hand_types = {
        "QINGYISE": get_qingyise_tingpai,
        "MAN_WIND": get_man_wind_tingpai,
        "MAN_DRAGON": get_man_dragon_tingpai
    }
    batch_types = ["MAN_WIND", "MAN_DRAGON"]
    if len(sys.argv) > 1:
        hand_label = sys.argv[1].upper()
        if hand_label == "BOTH":
            for label in batch_types:
                run_experiment(label, hand_types[label], N_GAMES, N_SIM)
            return
        elif hand_label not in hand_types:
            print(f"Unknown hand type: {hand_label}. Choose from: {list(hand_types.keys())} or BOTH")
            return
    else:
        hand_label = "QINGYISE"
    hand_func = hand_types[hand_label]
    run_experiment(hand_label, hand_func, N_GAMES, N_SIM)

def run_experiment(hand_label, hand_func, N_GAMES, N_SIM):
    print(f"\n===== Testing Hand Type: {hand_label} =====")

    # Prepare Q-learning agent (assume already trained or train here)
    q_agent = QLearningAgent(alpha=0.2, gamma=0.9, epsilon=0.2)
    print("Training Q-learning agent for experiment...")
    q_agent.learn(episodes=1000)
    print(f"Q-table size: {len(q_agent.q_table)}")

    # Prepare CSV for saving results
    results_path = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'mcts_q_compare_results.csv')
    results_path = os.path.abspath(results_path)
    os.makedirs(os.path.dirname(results_path), exist_ok=True)

    # Run original MCTS (no Q-learning)
    print(f"\nRunning original MCTS for {hand_label}...")
    results = []
    for game in range(N_GAMES):
        hand, wall = hand_func()
        steps = 0
        while True:
            if len(hand) == 8 and is_win(hand):
                score, base_score, bonus, details = calc_score(hand, steps)
                print(f"[MCTS_{hand_label}] Game {game+1}: Win in {steps} steps, Score: {score}, Bonus: {bonus}")
                results.append([
                    f'MCTS_{hand_label}', game+1, ' '.join(map(str, sorted(hand))), steps, base_score, bonus, score, '; '.join(details), 1
                ])
                break
            if not wall:
                print(f"[MCTS_{hand_label}] Game {game+1}: No win.")
                results.append([
                    f'MCTS_{hand_label}', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=N_SIM, q_agent=None)
            if discard is None or discard not in hand:
                results.append([
                    f'MCTS_{hand_label}', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            hand.remove(discard)
            draw = wall.pop(0)
            hand.append(draw)
            steps += 1

    # Run MCTS with Q-learning-guided rollout
    print(f"\nRunning MCTS+Q for {hand_label}...")
    for game in range(N_GAMES):
        hand, wall = hand_func()
        steps = 0
        while True:
            if len(hand) == 8 and is_win(hand):
                score, base_score, bonus, details = calc_score(hand, steps)
                print(f"[MCTS+Q_{hand_label}] Game {game+1}: Win in {steps} steps, Score: {score}, Bonus: {bonus}")
                results.append([
                    f'MCTS+Q_{hand_label}', game+1, ' '.join(map(str, sorted(hand))), steps, base_score, bonus, score, '; '.join(details), 1
                ])
                break
            if not wall:
                print(f"[MCTS+Q_{hand_label}] Game {game+1}: No win.")
                results.append([
                    f'MCTS+Q_{hand_label}', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=N_SIM, q_agent=q_agent)
            if discard is None or discard not in hand:
                results.append([
                    f'MCTS+Q_{hand_label}', game+1, ' '.join(map(str, sorted(hand))), steps, 0, 0, 0, '', 0
                ])
                break
            hand.remove(discard)
            draw = wall.pop(0)
            hand.append(draw)
            steps += 1

    # Calculate and append averages for each method
    results_df = pd.DataFrame(results, columns=['Method', 'Game', 'Hand', 'Steps', 'Base Score', 'Bonus', 'Total Score', 'Details', 'Win'])
    avg_rows = []
    for method in [f'MCTS_{hand_label}', f'MCTS+Q_{hand_label}']:
        method_df = results_df[results_df['Method'] == method]
        avg_steps = method_df['Steps'].mean()
        avg_score = method_df['Total Score'].mean()
        avg_rows.append([
            f'{method}_AVG', 'AVG', '', avg_steps, '', '', avg_score, f'Average Steps: {avg_steps:.2f}, Average Score: {avg_score:.2f}', 1
        ])
    # Append average rows to results
    for row in avg_rows:
        results.append(row)
    # Save results to CSV in append mode (do not overwrite previous results)
    if not os.path.exists(results_path):
        results_df = pd.DataFrame(results, columns=['Method', 'Game', 'Hand', 'Steps', 'Base Score', 'Bonus', 'Total Score', 'Details', 'Win'])
        results_df.to_csv(results_path, index=False, mode='w', header=True)
    else:
        results_df = pd.DataFrame(results, columns=['Method', 'Game', 'Hand', 'Steps', 'Base Score', 'Bonus', 'Total Score', 'Details', 'Win'])
        results_df.to_csv(results_path, index=False, mode='a', header=False)

    # Print detailed results for this hand type
    print(f"\nDetailed Results Analysis for {hand_label}:")
    print("=" * 50)
    for method in [f'MCTS_{hand_label}', f'MCTS+Q_{hand_label}']:
        print(f"\n{method} Results:")
        print("-" * 30)
        method_df = results_df[results_df['Method'] == method]
        for _, row in method_df.iterrows():
            if row['Game'] == 'AVG':
                print(f"AVG: Average Steps = {row['Steps']:.2f}, Average Total Score = {row['Total Score']:.2f}")
            else:
                print(f"Game {int(row['Game'])}: Steps = {int(row['Steps'])}, Total Score = {int(row['Total Score'])}")
                if row['Bonus'] > 0:
                    print(f"  Bonus: {row['Details']}")
        avg_steps = method_df['Steps'].mean()
        avg_score = method_df['Total Score'].mean()
        print(f"\n{method} Averages:")
        print(f"Average Steps: {avg_steps:.2f}")
        print(f"Average Total Score: {avg_score:.2f}")

if __name__ == "__main__":
    main() 