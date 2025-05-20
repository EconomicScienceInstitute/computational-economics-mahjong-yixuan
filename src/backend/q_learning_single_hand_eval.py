print("=== THIS IS PURE Q-LEARNING SCRIPT ===")
import random
from auto_train_mcts import q_learning_train, q_greedy_discard, is_win

def main():
    """
    Train Q-learning on a fixed hand for 10,000 episodes, then evaluate the average steps to win
    using the trained Q-table.
    """
    # 1. Define the fixed hand and wall (Qingyise: 1-8 Manzu)
    hand = [9, 10, 11, 12, 13, 14, 15, 16]  # 1-8 Manzu
    wall = [i for i in range(9, 18)] * 2  # 1-9 Manzu, 2 copies each
    for t in hand:
        wall.remove(t)

    # 2. Q-learning training (10,000 episodes)
    print("Training Q-learning agent on the fixed hand for 10,000 episodes...")
    q_agent = q_learning_train(hand, wall, n_episodes=10000)
    print("Training complete.")

    # 3. Evaluate average steps to win using the trained Q-table
    n_eval = 1000
    steps_list = []
    for _ in range(n_eval):
        h = hand[:]
        w = wall[:]
        random.shuffle(w)  # Shuffle wall for each evaluation
        steps = 0
        while not is_win(h):
            discard = q_greedy_discard(h, q_agent)
            h.remove(discard)
            if w:
                draw = w.pop()
                h.append(draw)
            steps += 1
        steps_list.append(steps)
    avg_steps = sum(steps_list) / len(steps_list)
    print(f"Q-learning average steps to win (over {n_eval} runs): {avg_steps:.2f}")

if __name__ == "__main__":
    main() 