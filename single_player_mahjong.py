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
    """Initialize the tile wall and draw a random 7-tile hand."""
    tiles = []
    for v in TILE_VALUES:
        tiles.extend([v] * TILE_COPIES)  # Each number appears 2 times
    random.shuffle(tiles)
    hand = tiles[:7]  # Draw 7 tiles for initial hand
    wall = tiles[7:]  # Remaining tiles go to the wall
    return hand, wall


def is_ready(hand):
    """
    Check if the hand (7 tiles) is ready to win (tingpai).
    Returns a list of tiles that would complete the hand.
    """
    if len(hand) != 7:
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
    Winning patterns:
    - 123 + 333 + pair
    - 222 + 333 + pair
    - 4444
    """
    if len(hand) != 8:
        return False
    
    # Check for four of a kind
    c = Counter(hand)
    for tile, count in c.items():
        if count == 4:
            remaining = [t for t in hand if t != tile]
            if len(remaining) == 4:  # Should have exactly 4 tiles remaining
                return True
    
    # Check for 123 + 333 + pair or 222 + 333 + pair
    tiles = sorted(hand)
    # Try all possible pairs
    for pair in set(tiles):
        if c[pair] < 2:
            continue
        temp = tiles.copy()
        temp.remove(pair)
        temp.remove(pair)
        # Try 123 + 333
        for i in range(1, 8):
            if i in temp and i+1 in temp and i+2 in temp:
                t2 = temp.copy()
                t2.remove(i)
                t2.remove(i+1)
                t2.remove(i+2)
                # Check for 333
                for trip in set(t2):
                    if t2.count(trip) == 3:
                        return True
        # Try 222 + 333
        for trip1 in set(temp):
            if temp.count(trip1) >= 3:
                t2 = temp.copy()
                t2.remove(trip1)
                t2.remove(trip1)
                t2.remove(trip1)
                for trip2 in set(t2):
                    if t2.count(trip2) == 3:
                        return True
    return False


def mcts_decision(hand, wall, n_sim=1000):
    """
    Monte Carlo Tree Search skeleton for single-player mahjong.
    For each possible discard, simulate n_sim random playouts and pick the discard with the lowest average steps to win.
    """
    if not wall:
        return None, float('inf')  # No more tiles to draw
    
    results = defaultdict(list)  # discard -> list of steps to win
    for discard in set(hand):
        wins = 0
        total_steps = 0
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
                        wins += 1
                        total_steps += steps
                        break
                else:
                    # If no winning discard found, continue with random discard
                    if len(temp_hand) > 8:
                        temp_hand.remove(random.choice(temp_hand))
            
            if wins == 0:
                results[discard].append(float('inf'))
            else:
                results[discard].append(total_steps / wins)
    
    # Find the discard with the lowest average steps to win
    best_discard = None
    best_avg = float('inf')
    for discard, steps_list in results.items():
        avg = sum(steps_list) / len(steps_list)
        if avg < best_avg:
            best_avg = avg
            best_discard = discard
    
    # Only return None if absolutely no path to victory
    if best_avg == float('inf'):
        return None, float('inf')
    return best_discard, best_avg


def main():
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
        discard, avg_steps = mcts_decision(hand, wall, n_sim=100)
        if discard is None:
            print("Game Over: No valid moves available.")
            print(f"Final hand: {hand}")
            break
        hand.remove(discard)
        print(f"Discard: {discard} (expected avg steps to win: {avg_steps:.2f})")
        steps += 1

if __name__ == "__main__":
    main() 