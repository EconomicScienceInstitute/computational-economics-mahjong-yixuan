import random
from collections import defaultdict
import csv
import os
import pickle

# Do not import from single_player_mahjong at the top to avoid circular import

# Generate a fixed 'Qingyise' (pure one suit) ready hand (Tingpai)
def get_qingyise_tingpai():
    hand = [11, 12, 13, 14, 15, 16, 17, 18]
    wall = [i for i in range(11, 20)] * 4
    for t in hand:
        wall.remove(t)
    random.shuffle(wall)
    return hand.copy(), wall

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2, use_feature_state=False):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.use_feature_state = use_feature_state

    def state_to_tuple(self, hand):
        """Convert a hand (list of tiles) to a sorted tuple for Q-table lookup."""
        return tuple(sorted(hand))

    def hand_to_features(self, hand):
        from collections import Counter
        c = Counter(hand)
        num_pairs = sum(1 for v in c.values() if v == 2)
        num_triplets = sum(1 for v in c.values() if v == 3)
        num_winds = sum(1 for t in hand if 27 <= t <= 30)
        num_dragons = sum(1 for t in hand if 31 <= t <= 33)
        return (num_pairs, num_triplets, num_winds, num_dragons)

    def state_key(self, hand):
        if self.use_feature_state:
            return self.hand_to_features(hand)
        else:
            return tuple(sorted(hand))

    def get_q_value(self, hand, action):
        return self.q_table.get((self.state_key(hand), action), 0.0)

    def update_q_value(self, hand, action, reward, next_hand, next_actions):
        key = (self.state_key(hand), action)
        next_qs = [self.get_q_value(next_hand, a) for a in next_actions] if next_actions else [0.0]
        max_next_q = max(next_qs)
        old_q = self.q_table.get(key, 0.0)
        self.q_table[key] = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)

    def act_greedy(self, hand):
        actions = list(set(hand))
        if not actions:
            return None
        q_values = [self.get_q_value(hand, a) for a in actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def train(self, hand, wall, n_episodes=10000, is_win_func=None):
        """
        Train the Q-learning agent on a specific hand and wall configuration.
        Args:
            hand: Initial hand
            wall: Wall tiles
            n_episodes: Number of training episodes
            is_win_func: Custom function to check for winning hand (optional)
        """
        # Import is_win here to avoid circular import
        from single_player_mahjong import is_win
        if is_win_func is None:
            is_win_func = is_win
        
        for episode in range(n_episodes):
            h = hand[:]
            w = wall[:]
            random.shuffle(w)
            
            while not is_win_func(h):
                # Choose action using epsilon-greedy policy
                if random.random() < self.epsilon:
                    if not h:  # If hand is empty, skip this iteration
                        break
                    action = random.choice(list(set(h)))
                else:
                    action = self.act_greedy(h)
                
                if action is None:
                    break
                
                # Take action and observe next state
                h.remove(action)
                if w:
                    draw = w.pop()
                    h.append(draw)
                
                # Update Q-value
                reward = -1
                next_actions = list(set(h))
                self.update_q_value(hand, action, reward, h, next_actions)
                
                if is_win_func(h):
                    break
            
            if (episode + 1) % 1000 == 0:
                print(f"Completed {episode + 1} training episodes")
        
        return self.q_table

    def save_q_table(self, filename):
        """Save the Q-table to a file using pickle."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load_q_table(self, filename):
        """Load the Q-table from a file using pickle. If file does not exist, do nothing."""
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.q_table = defaultdict(float, data)

def train_and_evaluate(hand, wall, n_episodes=10000, n_eval=1000):
    """
    Train a Q-learning agent and evaluate its performance.
    During evaluation, record the score breakdown (base_score, bonus, total) for each win, and print the breakdown and summary statistics.
    """
    # Import is_win and calc_score here to avoid circular import
    from single_player_mahjong import is_win, calc_score
    
    # Initialize and train agent
    agent = QLearningAgent(alpha=0.1, gamma=0.9, epsilon=0.2)
    print(f"\nTraining Q-learning agent for {n_episodes} episodes...")
    agent.train(hand, wall, n_episodes)
    print("Training complete.")

    # Evaluate performance
    print(f"\nEvaluating performance over {n_eval} runs...")
    steps_list = []
    base_scores = []
    bonuses = []
    total_scores = []
    for i in range(n_eval):
        h = hand[:]
        w = wall[:]
        random.shuffle(w)
        steps = 0
        while not is_win(h):
            discard = agent.act_greedy(h)
            if discard is None:
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
            bonuses.append(bonus)
            total_scores.append(score)
        if (i + 1) % 100 == 0:
            print(f"Completed {i + 1}/{n_eval} evaluation runs")
    
    if not steps_list:
        print("\nNo successful wins in evaluation!")
        return float('inf'), float('inf'), float('inf')
    
    # Calculate statistics
    avg_steps = sum(steps_list) / len(steps_list)
    min_steps = min(steps_list)
    max_steps = max(steps_list)
    avg_base = sum(base_scores) / len(base_scores)
    avg_bonus = sum(bonuses) / len(bonuses)
    avg_total = sum(total_scores) / len(total_scores)
    total_total = sum(total_scores)
    
    print("\nEvaluation Results:")
    print(f"Average steps to win: {avg_steps:.2f}")
    print(f"Minimum steps: {min_steps}")
    print(f"Maximum steps: {max_steps}")
    print(f"Average base score: {avg_base:.2f}")
    print(f"Average bonus: {avg_bonus:.2f}")
    print(f"Average total score: {avg_total:.2f}")
    print(f"Total score (all wins): {total_total}")
    
    return avg_steps, min_steps, max_steps, avg_base, avg_bonus, avg_total, total_total

def main():
    # Import required functions here to avoid circular import
    from single_player_mahjong import calc_score
    agent = QLearningAgent(alpha=0.2, gamma=0.9, epsilon=0.2)
    print("Training Q-learning agent...")
    agent.train(hand, wall)
    print(f"Q-table size: {len(agent.q_table)}")
    n_games = 10
    total_wins = 0
    total_steps = 0
    total_base_score = 0
    total_bonus = 0
    total_score = 0
    print("\nRunning test games...")
    print("\nFormat: Hand | Steps | Basic Score | Bonus | Total Score")
    print("-" * 60)

    results_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'results', 'q_learning_results.csv')
    results_path = os.path.abspath(results_path)
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    file_exists = os.path.isfile(results_path)
    with open(results_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Hand', 'Steps', 'Basic Score', 'Bonus', 'Total Score', 'Details'])

        for game in range(n_games):
            print(f"\nGame {game + 1}/{n_games}")
            hand, wall = get_qingyise_tingpai()
            steps = 0
            print(f"Initial hand: {sorted(hand)}")
            while True:
                if len(hand) == 8 and is_win(hand):
                    score, base_score, bonus, details = calc_score(hand, steps)
                    total_wins += 1
                    total_steps += steps
                    total_base_score += base_score
                    total_bonus += bonus
                    total_score += score
                    print("\nFinal Results:")
                    print(f"Hand: {sorted(hand)}")
                    print(f"Steps: {steps}")
                    print(f"Basic Score: {base_score}")
                    print(f"Bonus: {bonus}")
                    print(f"Total Score: {score}")
                    print(f"Details: {', '.join(details)}")
                    writer.writerow([
                        ' '.join(map(str, sorted(hand))),
                        steps,
                        base_score,
                        bonus,
                        score,
                        '; '.join(details)
                    ])
                    break
                if not wall:
                    print("\nGame Over: No more tiles in the wall.")
                    print(f"Final hand: {sorted(hand)}")
                    break
                discard = agent.act_greedy(hand)
                hand.remove(discard)
                draw = wall.pop(0)
                hand.append(draw)
                steps += 1
                print(f"Step {steps}: Discard {discard}, Draw {draw}, Hand: {sorted(hand)}")
    print("\nFinal Statistics:")
    print(f"Games played: {n_games}")
    print(f"Wins: {total_wins} ({total_wins/n_games*100:.1f}%)")
    if total_wins > 0:
        print(f"Average steps per win: {total_steps/total_wins:.1f}")
        print(f"Average basic score: {total_base_score/total_wins:.1f}")
        print(f"Average bonus: {total_bonus/total_wins:.1f}")
        print(f"Average total score: {total_score/total_wins:.1f}")

if __name__ == "__main__":
    # Example usage
    hand = [9, 10, 11, 12, 13, 14, 15, 16]  # 1-8 Manzu
    wall = [i for i in range(9, 18)] * 2  # 1-9 Manzu, 2 copies each
    for t in hand:
        wall.remove(t)
    
    avg_steps, min_steps, max_steps, avg_base, avg_bonus, avg_total, total_total = train_and_evaluate(hand, wall)
    main() 