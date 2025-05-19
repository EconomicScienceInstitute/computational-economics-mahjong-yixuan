import random
from collections import defaultdict
import csv
import os

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
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = defaultdict(float)  # key: (state, action), value: Q-value
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.epsilon = epsilon  # exploration rate

    def state_to_tuple(self, hand):
        # Import shanten here to avoid circular import
        from single_player_mahjong import shanten
        hand_tuple = tuple(sorted(hand))
        shanten_num = shanten(hand)
        return (hand_tuple, shanten_num)

    def choose_action(self, hand):
        possible_discards = list(set(hand))
        if random.random() < self.epsilon:
            return random.choice(possible_discards)
        state = self.state_to_tuple(hand)
        q_values = [self.q_table[(state, a)] for a in possible_discards]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(possible_discards, q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, episodes=1000):
        for ep in range(episodes):
            hand, wall = get_qingyise_tingpai()
            steps = 0
            while True:
                # Import is_win here to avoid circular import
                from single_player_mahjong import is_win
                if len(hand) == 8 and is_win(hand):
                    reward = 1000 - steps
                    break
                if not wall:
                    reward = 0
                    break
                state = self.state_to_tuple(hand)
                action = self.choose_action(hand)
                hand.remove(action)
                if wall:
                    draw = wall.pop(0)
                    hand.append(draw)
                next_state = self.state_to_tuple(hand)
                current_shanten = state[1]
                next_shanten = next_state[1]
                shanten_reward = (current_shanten - next_shanten) * 10
                next_possible_discards = list(set(hand))
                if next_possible_discards:
                    max_next_q = max([self.q_table[(next_state, a)] for a in next_possible_discards])
                else:
                    max_next_q = 0
                self.q_table[(state, action)] += self.alpha * (
                    shanten_reward - 1 + self.gamma * max_next_q - self.q_table[(state, action)]
                )
                steps += 1
            self.q_table[(state, action)] += self.alpha * (reward - self.q_table[(state, action)])
            if (ep + 1) % 100 == 0:
                print(f"Completed {ep + 1} training episodes")

    def act_greedy(self, hand):
        possible_discards = list(set(hand))
        state = self.state_to_tuple(hand)
        q_values = [self.q_table[(state, a)] for a in possible_discards]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(possible_discards, q_values) if q == max_q]
        return random.choice(best_actions)

def main():
    # Import required functions here to avoid circular import
    from single_player_mahjong import is_win, calc_score
    agent = QLearningAgent(alpha=0.2, gamma=0.9, epsilon=0.2)
    print("Training Q-learning agent...")
    agent.learn(episodes=1000)
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
    main() 