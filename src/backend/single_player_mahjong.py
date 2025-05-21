import random
from collections import Counter, defaultdict # Import Counter for tile counting and defaultdict for MCTS statistics
import math
from concurrent.futures import ThreadPoolExecutor

# Define the tile set
# Character tiles (1-9 man, but numbered 9-17 in images)
MAN_VALUES = list(range(9, 18))  # 9-17 for 1-9 man
# Winds: East=27, South=28, West=29, North=30
WIND_VALUES = [27, 28, 29, 30]
# Dragons: Green=31, Red=32, White=33
DRAGON_VALUES = [31, 32, 33]

# Combine all tile types
TILE_VALUES = MAN_VALUES + WIND_VALUES + DRAGON_VALUES
TILE_COPIES = 2  # Each tile appears 2 times
TOTAL_TILES = TILE_COPIES * len(TILE_VALUES)  # Total: (9+4+3)*2 = 32 tiles


def init_tiles():
    """Initialize the tile wall and draw a random 8-tile hand."""
    tiles = []
    for v in TILE_VALUES:
        tiles.extend([v] * TILE_COPIES)  # Each number appears 2 times
    random.shuffle(tiles)
    hand = tiles[:8]  # Draw 8 tiles for initial hand
    wall = tiles[8:]  # Remaining tiles go to the wall
    return hand, wall


def is_ready(hand):
    """
    Check if the hand (8 tiles) is ready to win (tingpai).
    Returns a list of tiles that would complete the hand.
    
    Args:
        hand (list): Current hand of 8 tiles
        
    Returns:
        list: List of tiles that would complete the hand for a win.
              Empty list if not ready or invalid hand size.
    """
    # Validate hand size - must be exactly 8 tiles
    if len(hand) != 8:
        return []
    
    winning_tiles = []
    # Test each possible tile in the game
    for tile in TILE_VALUES:
        # Create a copy of hand to avoid modifying original
        test_hand = hand.copy()
        # Add the test tile to make it 9 tiles
        test_hand.append(tile)
        # Check if this tile completes a winning hand
        if is_win(test_hand):
            winning_tiles.append(tile)
    
    return winning_tiles


def is_win(hand):
    """
    Check if the hand is a winning hand.
    Winning pattern requires:
    - Exactly 8 or 9 tiles
    - One pair (exactly two identical tiles, only one allowed)
    - Two sequences (chows: three consecutive man tiles each, only in Characters 9-17)
    - No tile is used more than once
    """
    if len(hand) not in [8, 9]:
        return False

    tile_count = Counter(hand)
    # There must be exactly one pair (no more, no less)
    pairs = [t for t in tile_count if tile_count[t] == 2]
    if len(pairs) != 1:
        return False

    pair_tile = pairs[0]
    # Remove the pair from the hand
    temp_count = tile_count.copy()
    temp_count[pair_tile] -= 2

    # The remaining tiles must all be man tiles (Characters 9-17)
    remaining_tiles = list(temp_count.elements())
    if any(t < 9 or t > 17 for t in remaining_tiles):
        return False
    # There must be no other pair or triplet in the remaining tiles
    if any(temp_count[t] > 1 for t in temp_count if 9 <= t <= 17):
        return False

    # Try to form two chows (sequences of three consecutive man tiles)
    def can_form_chows(counter, chows_left):
        if chows_left == 0:
            return sum(counter.values()) == 0
        # Find the smallest tile with at least one left
        for t in range(9, 16):
            if counter[t] >= 1 and counter[t+1] >= 1 and counter[t+2] >= 1:
                counter[t] -= 1
                counter[t+1] -= 1
                counter[t+2] -= 1
                if can_form_chows(counter, chows_left - 1):
                    return True
                # backtrack
                counter[t] += 1
                counter[t+1] += 1
                counter[t+2] += 1
        return False

    c = Counter()
    for t in range(9, 18):
        c[t] = temp_count[t]
    return can_form_chows(c, 2)


def get_qingyise_tingpai():
    # 8 tiles, all in the same suit (Manzu 9-17), one tile away from winning
    hand = [9, 10, 11, 12, 13, 14, 15, 16]  # 1-8 Manzu
    wall = [i for i in range(9, 18)] * 4     # 1-9 Manzu
    for t in hand:
        wall.remove(t)
    random.shuffle(wall)
    return hand.copy(), wall


def q_greedy_discard(hand, q_agent):
    # Import QLearningAgent here to avoid circular import
    from q_learning import QLearningAgent
    # Use Q-table to select the best discard
    state = q_agent.state_to_tuple(hand)
    possible_discards = list(set(hand))
    q_values = [q_agent.q_table.get((state, a), 0) for a in possible_discards]
    max_q = max(q_values)
    best_actions = [a for a, q in zip(possible_discards, q_values) if q == max_q]
    return random.choice(best_actions)


def mcts_decision(hand, wall, n_sim=1000, q_agent=None):
    """
    Monte Carlo Tree Search for single-player mahjong.
    If q_agent is provided, use Q-learning policy for rollout; otherwise, use original strategy.
    """
    if not wall:
        return None, float('inf'), {'min_steps': float('inf'), 'max_steps': float('inf'), 'win_rate': 0}
    stats = defaultdict(lambda: {'wins': 0, 'total_steps': 0, 'min_steps': float('inf'), 'max_steps': 0, 'visits': 0})
    C = 1.414
    max_depth = 30

    def uct_value(node_stats, parent_visits):
        # Avoid math domain error: log(0) is undefined
        if node_stats['visits'] == 0 or parent_visits <= 0:
            return float('inf')
        if node_stats['wins'] > 0:
            avg_steps = node_stats['total_steps'] / node_stats['wins']
            exploitation = (node_stats['wins'] / node_stats['visits']) * (1.0 / (1.0 + avg_steps/100.0))
        else:
            exploitation = 0
        exploration = C * math.sqrt(math.log(parent_visits) / node_stats['visits'])
        return exploitation + exploration

    def simulate_game(discard):
        sim_hand = hand.copy()
        sim_hand.remove(discard)
        sim_wall = wall.copy()
        random.shuffle(sim_wall)
        steps = 0
        temp_hand = sim_hand.copy()
        temp_wall = sim_wall.copy()
        while temp_wall and steps < max_depth:
            draw = temp_wall.pop(0)
            temp_hand.append(draw)
            steps += 1
            # Check win
            if is_win(temp_hand):
                return steps
            # Discard selection
            if len(temp_hand) > 8:
                if q_agent is not None:
                    next_discard = q_greedy_discard(temp_hand, q_agent)
                else:
                    best_uct = float('-inf')
                    best_next_discard = None
                    for next_discard in set(temp_hand):
                        if next_discard not in stats:
                            stats[next_discard] = {'wins': 0, 'total_steps': 0, 'min_steps': float('inf'), 'max_steps': 0, 'visits': 0}
                        uct = uct_value(stats[next_discard], stats[discard]['visits'])
                        if uct > best_uct:
                            best_uct = uct
                            best_next_discard = next_discard
                    if best_next_discard is None:
                        break
                    next_discard = best_next_discard
                temp_hand.remove(next_discard)
                stats[next_discard]['visits'] += 1
        return float('inf')

    for discard in set(hand):
        for _ in range(n_sim):
            steps = simulate_game(discard)
            if steps != float('inf'):
                stats[discard]['wins'] += 1
                stats[discard]['total_steps'] += steps
                stats[discard]['min_steps'] = min(stats[discard]['min_steps'], steps)
                stats[discard]['max_steps'] = max(stats[discard]['max_steps'], steps)
            stats[discard]['visits'] += 1
    best_discard = None
    best_avg = float('inf')
    best_stats = {'min_steps': float('inf'), 'max_steps': 0, 'win_rate': 0}
    for discard, discard_stats in stats.items():
        if discard_stats['wins'] > 0:
            avg = discard_stats['total_steps'] / discard_stats['wins']
            win_rate = discard_stats['wins'] / n_sim
            if avg < best_avg:
                best_avg = avg
                best_discard = discard
                best_stats = {
                    'min_steps': discard_stats['min_steps'],
                    'max_steps': discard_stats['max_steps'],
                    'win_rate': win_rate
                }
    if best_avg == float('inf'):
        return None, float('inf'), {'min_steps': float('inf'), 'max_steps': float('inf'), 'win_rate': 0}
    return best_discard, best_avg, best_stats


def shanten(hand):
    """
    Calculate the shanten number (number of steps away from winning).
    In our 8-tile game:
    - 0 = Ready to win (just need the right tile)
    - 1 = Need one more step
    
    Args:
        hand (list): List of tiles to check
        
    Returns:
        int: Shanten number
            - 0: Ready to win (tenpai)
            - 1: One step away from ready
    """
    # For 8-tile hands, we're either ready (0) or one step away (1)
    if len(hand) == 8:
        return 0 if is_win(hand) else 1
    
    # Count occurrences of each tile
    c = Counter(hand)
    
    # Count how many pairs we have
    pairs = sum(1 for v in c.values() if v >= 2)
    
    # Get and sort the man (number) tiles for finding sequences
    man_tiles = [t for t in hand if 9 <= t <= 17]
    man_tiles = sorted(man_tiles)
    
    # Track which tiles we've used in sequences
    used = [False]*len(man_tiles)
    chows = 0  # Count of complete sequences found
    
    # Look for sequences (123, 234, etc.)
    for i in range(len(man_tiles)-2):
        if not used[i]:  # If first tile not used yet
            for j in range(i+1, len(man_tiles)-1):
                if not used[j] and man_tiles[j] == man_tiles[i]+1:  # Found second tile
                    for k in range(j+1, len(man_tiles)):
                        if not used[k] and man_tiles[k] == man_tiles[j]+1:  # Found third tile
                            # Found a complete sequence
                            chows += 1
                            used[i] = used[j] = used[k] = True
                            break
                    break
    
    # Calculate what we still need
    need_chows = max(0, 2-chows)    # We need 2 sequences total
    need_pair = 1 if pairs == 0 else 0   # We need 1 pair
    
    # Return total number of patterns we still need
    return need_chows + need_pair


# Scoring Rules:
# 1. Base Score: 100 - steps (minimum 0)
#    - Start with 100 points
#    - Subtract the number of steps taken
#    - Cannot go below 0
#
# 2. Combination Bonus:
#    - All Manzu (Characters) +20
#      * All tiles are number tiles (9-17)
#      * Encourages focused number tile strategy

def calc_score(hand, steps):
    """
    Calculate the score for a winning hand based on both steps taken and tile combinations.
    Args:
        hand (list): The winning hand of 8 tiles
        steps (int): Number of steps taken to win
    Returns:
        tuple: (total_score, base_score, combination_bonus, details)
            total_score (int): Final score (base + bonus)
            base_score (int): Score based on steps (100 - steps)
            combination_bonus (int): Points from special combinations
            details (list): List of strings explaining each bonus
    """
    # Calculate base score: 100 - steps (minimum 0)
    base_score = max(100 - steps, 0)
    combination_bonus = 0
    details = []

    # Check for All Manzu (all tiles are numbers 9-17)
    if all(9 <= t <= 17 for t in hand):
        combination_bonus += 20
        details.append("All Manzu +20")
    
    # Calculate final score
    total_score = base_score + combination_bonus
    return total_score, base_score, combination_bonus, details


def get_man_wind_tingpai():
    """
    Generate a 'tenpai' (one-away from win) hand: wind pair + 6 manzu tiles forming two chows, but missing one tile to win.
    Example: [27, 27, 9, 10, 11, 12, 13, 15] (East East + 1-5,7 manzu), needs 14 (6 manzu) to win.
    """
    hand = [27, 27, 9, 10, 11, 12, 13, 15]  # East East + 1-5,7 manzu
    wall = []
    for v in MAN_VALUES + WIND_VALUES + DRAGON_VALUES:
        wall.extend([v] * TILE_COPIES)
    for t in hand:
        wall.remove(t)
    # Ensure the winning tile (14, 6 manzu) is in the wall
    if 14 in wall:
        pass
    else:
        # If not, replace a random tile in wall with 14
        wall[random.randrange(len(wall))] = 14
    random.shuffle(wall)
    return hand.copy(), wall


def get_man_dragon_tingpai():
    """
    Generate a 'tenpai' (one-away from win) hand: dragon pair + 6 manzu tiles forming two chows, but missing one tile to win.
    Example: [31, 31, 9, 10, 11, 12, 13, 15] (Red Red + 1-5,7 manzu), needs 14 (6 manzu) to win.
    """
    hand = [31, 31, 9, 10, 11, 12, 13, 15]  # Red Red + 1-5,7 manzu
    wall = []
    for v in MAN_VALUES + WIND_VALUES + DRAGON_VALUES:
        wall.extend([v] * TILE_COPIES)
    for t in hand:
        wall.remove(t)
    # Ensure the winning tile (14, 6 manzu) is in the wall
    if 14 in wall:
        pass
    else:
        wall[random.randrange(len(wall))] = 14
    random.shuffle(wall)
    return hand.copy(), wall


def main():
    # Must-win test case
    test_hand = [9, 10, 11, 12, 13, 14, 27, 27]  # C1, C2, C3, C4, C5, C6, East, East
    print(f"Test hand: {test_hand}")
    print(f"is_win(test_hand): {is_win(test_hand)}")
    # Original main logic
    hand, wall = init_tiles()
    print(f"Initial hand: {hand}")
    print(f"Wall: {wall}")
    steps = 0
    while True:
        if len(hand) == 8 and is_win(hand):
            print(f"Win! Final hand: {hand} in {steps} steps.")
            break
        if not wall:
            print("Game Over: No more tiles in the wall. Could not form a winning hand.")
            print(f"Final hand: {hand}")
            break
        draw = wall.pop(0)
        hand.append(draw)
        print(f"Draw: {draw}, hand: {hand}")
        # Use MCTS to decide which tile to discard
        discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=1000)
        if discard is None:
            print("Game Over: No valid moves available.")
            print(f"Final hand: {hand}")
            break
        hand.remove(discard)
        print(f"Discard: {discard} (expected avg steps to win: {avg_steps:.2f})")
        steps += 1

if __name__ == "__main__":
    main() 