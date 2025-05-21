print("=== THIS IS PURE Q-LEARNING SCRIPT ===")
import random
import os
import csv
from datetime import datetime
from q_learning import train_and_evaluate

def save_results(
    hand, wall_size,
    avg_steps, avg_base, avg_total,
    min_steps, min_base, min_total,
    max_total, max_total_steps,
    n_episodes, n_eval,
    qtable_entries, qtable_min, qtable_max, qtable_mean,
    results_dir='results'):
    """
    Append single hand Q-learning results to a CSV file with clear headers and detailed breakdown, including Q-table summary statistics.
    Always ensure the correct header is the first line. If not, create a temp file, write the header, then the old content and new row, and replace the original file.
    """
    import csv
    import shutil
    os.makedirs(results_dir, exist_ok=True)
    filename = os.path.join(results_dir, 'q_learning_single_hand_results.csv')
    header = [
        'Timestamp', 'Training Episodes', 'Evaluation Runs', 'Initial Hand', 'Wall Size',
        'Average Steps', 'Average Base Score', 'Average Total Score',
        'Minimum Steps', 'Base Score (Min Steps)', 'Total Score (Min Steps)',
        'Maximum Total Score', 'Steps (Max Total Score)',
        'Q-table Entries', 'Q-value Min', 'Q-value Max', 'Q-value Mean'
    ]
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), n_episodes, n_eval, ','.join(map(str, hand)), wall_size,
        f'{avg_steps:.2f}', f'{avg_base:.2f}', f'{avg_total:.2f}',
        min_steps, min_base, min_total,
        max_total, max_total_steps,
        qtable_entries, f'{qtable_min:.4f}', f'{qtable_max:.4f}', f'{qtable_mean:.4f}'
    ]
    file_exists = os.path.isfile(filename)
    need_header = True
    if file_exists:
        with open(filename, 'r', newline='') as f:
            first_line = f.readline().strip().split(',')
            if first_line[:4] == header[:4] and len(first_line) == len(header):
                need_header = False
    if file_exists and need_header:
        # Create a temp file, write header, then old content, then new row
        temp_filename = filename + '.tmp'
        with open(temp_filename, 'w', newline='') as temp_f:
            writer = csv.writer(temp_f)
            writer.writerow(header)
            with open(filename, 'r', newline='') as old_f:
                for line in old_f:
                    if line.strip():
                        temp_f.write(line)
            writer.writerow(row)
        shutil.move(temp_filename, filename)
    else:
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(row)
    print(f"\nResults appended to: {filename}")

def export_q_table_to_csv(agent, filename):
    """Export the Q-table to a CSV file for inspection."""
    import csv
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['State', 'Action', 'Q-value'])
        for (state, action), q in agent.q_table.items():
            writer.writerow([state, action, q])
    print(f"Q-table exported to: {filename}")

def main():
    """
    Train Q-learning on a fixed hand for specified episodes, then evaluate and save detailed results to CSV (append mode).
    """
    # Configuration
    N_EPISODES = 10000  # Number of training episodes
    N_EVAL = 1000      # Number of evaluation runs
    
    # 1. Define the fixed hand and wall (Qingyise: 1-8 Manzu)
    hand = [9, 10, 11, 12, 13, 14, 15, 16]  # 1-8 Manzu
    wall = [i for i in range(9, 18)] * 2  # 1-9 Manzu, 2 copies each
    for t in hand:
        wall.remove(t)
    wall_size = len(wall)

    print(f"\nInitial hand: {hand}")
    print(f"Wall tiles: {wall_size} tiles")

    # 2. Train and evaluate
    from single_player_mahjong import is_win, calc_score
    agent_results = []
    agent = None
    q_table_path = os.path.join('results', 'q_table_single_hand.pkl')
    def custom_train_and_evaluate(hand, wall, n_episodes=10000, n_eval=1000):
        from single_player_mahjong import is_win, calc_score
        nonlocal agent
        from q_learning import QLearningAgent
        agent = QLearningAgent(alpha=0.1, gamma=0.9, epsilon=0.2)
        # Load Q-table if exists
        if os.path.exists(q_table_path):
            agent.load_q_table(q_table_path)
            print(f"Loaded Q-table from {q_table_path}")
        else:
            print("No existing Q-table found. Training from scratch.")
        agent.train(hand, wall, n_episodes)
        # Save Q-table after training
        agent.save_q_table(q_table_path)
        print(f"Saved Q-table to {q_table_path}")
        agent.epsilon = 0
        steps_list = []
        base_scores = []
        total_scores = []
        for i in range(n_eval):
            h = hand[:]
            w = wall[:]
            random.shuffle(w)
            steps = 0
            while not is_win(h):
                discard = agent.act_greedy(h)
                if discard is None:
                    print(f"[DEBUG] Evaluation break: hand={h}, wall={w}, steps={steps}")
                    break
                h.remove(discard)
                if w:
                    draw = w.pop()
                    h.append(draw)
                steps += 1
            if is_win(h):
                steps_list.append(steps)
                score, base_score, bonus, details = calc_score(h, steps)
                base_scores.append(base_score)
                total_scores.append(score)
        return steps_list, base_scores, total_scores

    steps_list, base_scores, total_scores = custom_train_and_evaluate(hand, wall, N_EPISODES, N_EVAL)
    if not steps_list:
        print("\nNo successful wins in evaluation!")
        return
    avg_steps = sum(steps_list) / len(steps_list)
    avg_base = sum(base_scores) / len(base_scores)
    avg_total = sum(total_scores) / len(total_scores)
    min_steps = min(steps_list)
    min_idx = steps_list.index(min_steps)
    min_base = base_scores[min_idx]
    min_total = total_scores[min_idx]
    max_total = max(total_scores)
    max_idx = total_scores.index(max_total)
    max_total_steps = steps_list[max_idx]

    # Q-table statistics
    if agent is not None:
        q_values = list(agent.q_table.values())
        if q_values:
            min_q = min(q_values)
            max_q = max(q_values)
            mean_q = sum(q_values) / len(q_values)
            qtable_entries = len(q_values)
            qtable_min = min_q
            qtable_max = max_q
            qtable_mean = mean_q
        else:
            qtable_entries = 0
            qtable_min = 0.0
            qtable_max = 0.0
            qtable_mean = 0.0
    else:
        qtable_entries = 0
        qtable_min = 0.0
        qtable_max = 0.0
        qtable_mean = 0.0

    # 3. Save results (append mode)
    save_results(
        hand, wall_size,
        avg_steps, avg_base, avg_total,
        min_steps, min_base, min_total,
        max_total, max_total_steps,
        N_EPISODES, N_EVAL,
        qtable_entries, qtable_min, qtable_max, qtable_mean
    )

    # Print a summary preview in the terminal
    print("\n===== Q-learning Single Hand Evaluation Summary =====")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Initial hand: {hand}")
    print(f"Wall size: {wall_size}")
    print(f"Training episodes: {N_EPISODES}")
    print(f"Evaluation runs: {N_EVAL}")
    print(f"Average steps to win: {avg_steps:.2f}")
    print(f"Average base score: {avg_base:.2f}")
    print(f"Average total score: {avg_total:.2f}")
    print(f"Minimum steps: {min_steps} (Base score: {min_base}, Total score: {min_total})")
    print(f"Maximum total score: {max_total} (Steps: {max_total_steps})")

    # Q-table statistics
    if agent is not None:
        q_values = list(agent.q_table.values())
        if q_values:
            min_q = min(q_values)
            max_q = max(q_values)
            mean_q = sum(q_values) / len(q_values)
            print(f"Q-table entries: {len(q_values)}")
            print(f"Q-value: min={min_q:.4f}, max={max_q:.4f}, mean={mean_q:.4f}")
            # Show top 5 max/min Q-value samples
            sorted_q = sorted(agent.q_table.items(), key=lambda x: x[1])
            print("Top 5 min Q-value samples:")
            for (state, action), q in sorted_q[:5]:
                print(f"  State: {state}, Action: {action}, Q: {q:.4f}")
            print("Top 5 max Q-value samples:")
            for (state, action), q in sorted_q[-5:]:
                print(f"  State: {state}, Action: {action}, Q: {q:.4f}")
    print("===================================================\n")

    # Export Q-table to CSV for inspection
    export_q_table_to_csv(agent, os.path.join('results', 'q_table_single_hand_dump.csv'))

if __name__ == "__main__":
    main() 