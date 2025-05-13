from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../src/backend')))
from auto_train_mcts import dp, dp_calls
from collections import Counter

# 8 tiles in hand, all Manzu (Characters), wall has 1 Manzu tile
hand = [9, 10, 11, 12, 13, 14, 15, 16]  # Manzu 1~8
wall = [17]  # Manzu 9

print("Test: 8 Manzu in hand, 1 Manzu in wall")
wall_counter_tuple = tuple(sorted(Counter(wall).items()))
result = dp(tuple(sorted(hand)), wall_counter_tuple)
print(f"Minimal steps to win from this state: {result}")
print(f"DP calls in this test: {dp_calls}") 