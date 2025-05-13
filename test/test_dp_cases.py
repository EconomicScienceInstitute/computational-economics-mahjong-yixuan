import sys
import os
from collections import Counter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))
from auto_train_mcts import dp

# Test hands that cannot win immediately
hands = [
    [9, 10, 11, 12, 13, 14, 15, 16],
    [9, 9, 9, 10, 11, 12, 13, 14],
    [27, 27, 28, 28, 29, 29, 30, 30],
    [9, 10, 11, 12, 13, 14, 15, 27],
    [9, 9, 10, 10, 11, 11, 12, 12],
    [9, 10, 11, 12, 13, 14, 15, 17],
    [9, 10, 11, 12, 13, 14, 15, 9],
    [9, 10, 11, 12, 13, 14, 15, 10],
    [9, 10, 11, 12, 13, 14, 15, 11],
    [9, 10, 11, 12, 13, 14, 15, 12],
    [9, 10, 11, 12, 13, 14, 15, 13],
    [9, 10, 11, 12, 13, 14, 15, 14],
]

# All possible tiles (2 of each)
all_tiles = [i for i in range(9, 18)] * 2 + [i for i in range(27, 34)] * 2

def make_wall(hand):
    wall = all_tiles.copy()
    for t in hand:
        wall.remove(t)
    return wall

for hand in hands:
    wall = make_wall(hand)
    wall_counter_tuple = tuple(sorted(Counter(wall).items()))
    result = dp(tuple(sorted(hand)), wall_counter_tuple)
    print(f"Hand: {hand} | Minimal steps to win: {result}") 