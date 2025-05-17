import csv
from single_player_mahjong import mcts_decision, calc_score, is_win

def generate_typical_hands():
    """Generate typical hands for 8-tile single player mahjong"""
    hands = []
    
    # 1. One tile away from winning
    hands.append({
        'name': 'One-Tile-Away',
        'hand': [9, 9, 10, 11, 12, 13, 14, 16],  # 需要15万
        'wall': [15, 15, 15, 17, 17, 28, 29, 30, 31, 32, 33],
        'description': 'One tile away from winning (needs 15)'
    })
    
    # 2. Two tiles away from winning
    hands.append({
        'name': 'Two-Tiles-Away',
        'hand': [9, 9, 10, 11, 12, 13, 14, 17],  # 需要15和16
        'wall': [15, 15, 16, 16, 28, 29, 30, 31, 32, 33],
        'description': 'Two tiles away from winning (needs 15 and 16)'
    })
    
    # 3. Mixed tiles with potential
    hands.append({
        'name': 'Mixed-Potential',
        'hand': [9, 10, 11, 27, 27, 28, 29, 30],  # 需要形成顺子
        'wall': [12, 13, 14, 15, 16, 17, 31, 32, 33],
        'description': 'Mixed tiles with potential to form chows'
    })
    
    # 4. Dragon pair with mixed tiles
    hands.append({
        'name': 'Dragon-Mixed',
        'hand': [31, 31, 9, 10, 11, 27, 28, 29],  # 需要形成顺子
        'wall': [12, 13, 14, 15, 16, 17, 30, 32, 33],
        'description': 'Dragon pair with mixed tiles'
    })
    
    return hands  # Return all hands for analysis

def simulate_mcts_games_for_hand(hand, wall, n_sim=100):
    results = []
    for _ in range(n_sim):
        temp_hand = hand.copy()
        temp_wall = wall.copy()
        steps = 0
        while len(temp_hand) == 8 and not is_win(temp_hand) and temp_wall:
            discard, _, _ = mcts_decision(temp_hand, temp_wall, n_sim=10)
            if discard is None or discard not in temp_hand:
                break
            temp_hand.remove(discard)
            temp_hand.append(temp_wall.pop(0))
            steps += 1
        if is_win(temp_hand):
            final_score, base_score, combo_bonus, details = calc_score(temp_hand, steps)
            win = 1
        else:
            final_score, base_score, combo_bonus, details = 0, 0, 0, []
            win = 0
        results.append((steps, final_score, base_score, combo_bonus, "; ".join(details), win))
    return results

def analyze_mcts_for_typical_hands(typical_hands, n_sim=100):
    with open("mcts_simulation_results.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "HandName", "Hand", "Wall", "Steps", "FinalScore", "BaseScore", "ComboBonus", "Details", "Win", "Description"
        ])
        for hand_info in typical_hands:
            hand = hand_info['hand']
            wall = hand_info['wall']
            name = hand_info.get('name', '')
            desc = hand_info.get('description', '')
            sim_results = simulate_mcts_games_for_hand(hand, wall, n_sim=n_sim)
            for steps, final_score, base_score, combo_bonus, details, win in sim_results:
                writer.writerow([
                    name, hand, wall, steps, final_score, base_score, combo_bonus, details, win, desc
                ])
            print(f"Simulated {n_sim} games for {name}")

if __name__ == '__main__':
    typical_hands = generate_typical_hands()
    analyze_mcts_for_typical_hands(typical_hands, n_sim=100) 