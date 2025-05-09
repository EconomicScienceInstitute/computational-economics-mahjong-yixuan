import random
from collections import Counter, defaultdict # Import Counter for tile counting and defaultdict for MCTS statistics

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
    Check if the hand (8 tiles) is a winning hand.
    Winning pattern requires:
    - Exactly 8 tiles
    - Two sequences (chows: three consecutive man tiles each)
    - One pair (two identical tiles)
    
    Args:
        hand (list): List of 8 tiles to check
        
    Returns:
        bool: True if hand is winning, False otherwise
    """
    # Validate hand size
    if len(hand) != 8:
        return False

    # Count occurrences of each tile
    c = Counter(hand)
    tiles = sorted(hand)
    
    # Try each possible pair from the hand
    for pair in set(tiles):
        # Skip if we don't have at least 2 of this tile
        if c[pair] < 2:
            continue
        # Remove the pair from consideration
        temp = tiles.copy()
        temp.remove(pair)
        temp.remove(pair)
        
        # Get remaining man (number) tiles for sequences
        # Only man tiles (9-17) can form sequences
        man_tiles = [t for t in temp if 9 <= t <= 17]
        
        # Check if we have exactly 6 man tiles (for two sequences)
        if len(man_tiles) == 6:
            man_tiles_sorted = sorted(man_tiles)
            # Try to find first sequence (123, 234, etc.)
            for i in range(9, 16):  # 9~15
                if (man_tiles_sorted.count(i) >= 1 and 
                    man_tiles_sorted.count(i+1) >= 1 and 
                    man_tiles_sorted.count(i+2) >= 1):
                    # Found first sequence, remove it
                    t2 = man_tiles_sorted.copy()
                    t2.remove(i)
                    t2.remove(i+1)
                    t2.remove(i+2)
                    # Try to find second sequence
                    for j in range(9, 16):
                        if (t2.count(j) >= 1 and 
                            t2.count(j+1) >= 1 and 
                            t2.count(j+2) >= 1):
                            # Found second sequence
                            t3 = t2.copy()
                            t3.remove(j)
                            t3.remove(j+1)
                            t3.remove(j+2)
                            # If all tiles used, we have a winning hand
                            if not t3:
                                return True
    # No winning combination found
    return False


def mcts_decision(hand, wall, n_sim=10000):
    """
    Monte Carlo Tree Search for single-player mahjong.
    Simulates multiple games for each possible discard to find the best move.
    
    Args:
        hand (list): Current hand of tiles
        wall (list): Remaining tiles in the wall
        n_sim (int): Number of simulations to run for each discard (default: 10000)
        
    Returns:
        tuple: A tuple containing three elements:
            best_discard (int or None): 
                - The recommended tile to discard
                - None if no winning path is found
            
            best_avg (float): 
                - Average steps needed to win if discarding best_discard
                - float('inf') if no winning path is found
            
            best_stats (dict): Statistics about the recommended move
                - 'min_steps' (int): Minimum steps to win in simulations
                - 'max_steps' (int): Maximum steps to win in simulations
                - 'win_rate' (float): Percentage of simulations that led to a win
    """
    # If no tiles left in wall, can't win
    if not wall:
        return None, float('inf'), {'min_steps': float('inf'), 'max_steps': float('inf'), 'win_rate': 0}
    
    # Initialize statistics tracking
    results = defaultdict(list)  # discard -> list of steps to win
    stats = defaultdict(lambda: {'wins': 0, 'total_steps': 0, 'min_steps': float('inf'), 'max_steps': 0})
    
    # Try each possible discard
    for discard in set(hand):
        # Run multiple simulations for this discard
        for _ in range(n_sim):
            # Setup simulation
            sim_hand = hand.copy()
            sim_hand.remove(discard)
            sim_wall = wall.copy()
            random.shuffle(sim_wall)
            steps = 0
            temp_hand = sim_hand.copy()
            temp_wall = sim_wall.copy()
            
            # Run simulation until win or timeout (30 steps)
            while temp_wall and steps < 30:
                # Draw a tile
                draw = temp_wall.pop(0)
                temp_hand.append(draw)
                steps += 1
                
                # Check if we can win by discarding any tile
                for possible_discard in temp_hand:
                    test_hand = temp_hand.copy()
                    test_hand.remove(possible_discard)
                    if is_win(test_hand):
                        # Record statistics for this winning path
                        stats[discard]['wins'] += 1
                        stats[discard]['total_steps'] += steps
                        stats[discard]['min_steps'] = min(stats[discard]['min_steps'], steps)
                        stats[discard]['max_steps'] = max(stats[discard]['max_steps'], steps)
                        break
                else:
                    # If no winning move, discard randomly
                    if len(temp_hand) > 8:
                        temp_hand.remove(random.choice(temp_hand))
            
            # If simulation timed out (took too many steps), mark as infinite
            if steps >= 30:
                results[discard].append(float('inf'))
            
    # Find the best discard based on statistics
    best_discard = None
    best_avg = float('inf')
    best_stats = {'min_steps': float('inf'), 'max_steps': 0, 'win_rate': 0}
    
    # Calculate average steps and win rate for each discard
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
    
    # If no winning path found, return None
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