import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))
from single_player_mahjong import is_win

# Test cases: (hand, expected_result)
test_cases = [
    ([9, 10, 11, 12, 13, 14, 27, 27], True),   # Win: two sequences + a pair
    ([9, 10, 11, 12, 13, 14, 15, 16], False),   # Only sequences, no pair
    ([9, 9, 9, 10, 11, 12, 13, 14], False),     # Three of a kind, not valid
    ([9, 10, 11, 12, 13, 14, 15, 15], True),    # Two sequences + a pair
    ([27, 27, 28, 28, 29, 29, 30, 30], False),  # All winds, no sequences
    ([9, 10, 11, 12, 13, 14, 15, 27], False),   # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 16], False),   # Only sequences, no pair
    ([9, 10, 11, 12, 13, 14, 15, 15], True),    # Two sequences + a pair
    ([9, 9, 10, 10, 11, 11, 12, 12], False),    # All pairs, not valid
    ([9, 10, 11, 12, 13, 14, 15, 17], False),   # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 9], False),    # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 10], False),   # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 11], False),   # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 12], False),   # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 13], False),   # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 14], False),   # One sequence + others
    ([9, 10, 11, 12, 13, 14, 15, 15], True),    # Two sequences + a pair
]

for hand, expected in test_cases:
    result = is_win(hand)
    print(f"Hand: {hand} | is_win: {result} | Expected: {expected} | {'PASS' if result == expected else 'FAIL'}") 