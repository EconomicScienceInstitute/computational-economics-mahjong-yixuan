import random
from collections import Counter, defaultdict

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
    """
    if len(hand) != 8:
        return []
    
    winning_tiles = []
    # Try each possible tile
    for tile in TILE_VALUES:
        test_hand = hand.copy()
        test_hand.append(tile)
        if is_win(test_hand):
            winning_tiles.append(tile)
    
    return winning_tiles


def is_win(hand):
    """
    Check if the hand (8 tiles) is a winning hand.
    Winning pattern:
    - Any two sequences (chows, i.e., three consecutive man tiles) + a pair
    """
    if len(hand) != 8:
        return False

    c = Counter(hand)
    tiles = sorted(hand)
    # Try all possible pairs
    for pair in set(tiles):
        if c[pair] < 2:
            continue
        temp = tiles.copy()
        temp.remove(pair)
        temp.remove(pair)
        # Try two sequences (any two chows) + pair
        # Only consider man tiles for chows (9-17)
        man_tiles = [t for t in temp if 9 <= t <= 17]
        if len(man_tiles) == 6:
            man_tiles_sorted = sorted(man_tiles)
            # Enumerate the first sequence
            for i in range(9, 16):  # 9~15
                if man_tiles_sorted.count(i) >= 1 and man_tiles_sorted.count(i+1) >= 1 and man_tiles_sorted.count(i+2) >= 1:
                    t2 = man_tiles_sorted.copy()
                    t2.remove(i)
                    t2.remove(i+1)
                    t2.remove(i+2)
                    # Enumerate the second sequence
                    for j in range(9, 16):
                        if t2.count(j) >= 1 and t2.count(j+1) >= 1 and t2.count(j+2) >= 1:
                            t3 = t2.copy()
                            t3.remove(j)
                            t3.remove(j+1)
                            t3.remove(j+2)
                            if not t3:  # All tiles used
                                return True
    return False


def mcts_decision(hand, wall, n_sim=10000):
    """
    Monte Carlo Tree Search for single-player mahjong.
    For each possible discard, simulate n_sim random playouts and pick the discard with the lowest average steps to win.
    Returns:
    - suggested_discard: the tile to discard
    - avg_steps: average steps to win
    - stats: dictionary containing min_steps, max_steps, and win_rate
    """
    if not wall:
        return None, float('inf'), {'min_steps': float('inf'), 'max_steps': float('inf'), 'win_rate': 0}
    
    results = defaultdict(list)  # discard -> list of steps to win
    stats = defaultdict(lambda: {'wins': 0, 'total_steps': 0, 'min_steps': float('inf'), 'max_steps': 0})
    
    for discard in set(hand):
        for _ in range(n_sim):
            sim_hand = hand.copy()
            sim_hand.remove(discard)
            sim_wall = wall.copy()
            random.shuffle(sim_wall)
            steps = 0
            temp_hand = sim_hand.copy()
            temp_wall = sim_wall.copy()
            
            # Run simulation until we win or run out of tiles
            while temp_wall and steps < 30:  # Add maximum steps limit
                draw = temp_wall.pop(0)
                temp_hand.append(draw)
                steps += 1
                
                # Try each possible discard
                for possible_discard in temp_hand:
                    test_hand = temp_hand.copy()
                    test_hand.remove(possible_discard)
                    if is_win(test_hand):
                        stats[discard]['wins'] += 1
                        stats[discard]['total_steps'] += steps
                        stats[discard]['min_steps'] = min(stats[discard]['min_steps'], steps)
                        stats[discard]['max_steps'] = max(stats[discard]['max_steps'], steps)
                        break
                else:
                    # If no winning discard found, continue with random discard
                    if len(temp_hand) > 8:
                        temp_hand.remove(random.choice(temp_hand))
            
            if steps >= 30:
                results[discard].append(float('inf'))
            
    # Find the discard with the lowest average steps to win
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
    
    # Only return None if absolutely no path to victory
    if best_avg == float('inf'):
        return None, float('inf'), {'min_steps': float('inf'), 'max_steps': float('inf'), 'win_rate': 0}
    
    return best_discard, best_avg, best_stats


def shanten(hand):
    """
    Calculate the shanten number (number of tiles away from winning).
    Only supports the two chows + pair pattern for 8-tile hands.
    For 7-tile hands, returns the number of tiles away from winning.
    """
    from collections import Counter
    if len(hand) == 8:
        return 0 if is_win(hand) else 1
    c = Counter(hand)
    # Count pairs
    pairs = sum(1 for v in c.values() if v >= 2)
    # Count chow (sequence) blocks
    man_tiles = [t for t in hand if 9 <= t <= 17]
    man_tiles = sorted(man_tiles)
    chows = 0
    used = [False]*len(man_tiles)
    for i in range(len(man_tiles)-2):
        if not used[i]:
            for j in range(i+1, len(man_tiles)-1):
                if not used[j] and man_tiles[j] == man_tiles[i]+1:
                    for k in range(j+1, len(man_tiles)):
                        if not used[k] and man_tiles[k] == man_tiles[j]+1:
                            chows += 1
                            used[i] = used[j] = used[k] = True
                            break
                    break
    # Need two chows and one pair
    need_chows = max(0, 2-chows)
    need_pair = 1 if pairs == 0 else 0
    return need_chows + need_pair


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