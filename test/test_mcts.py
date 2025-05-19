import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.single_player_mahjong import (
    init_tiles,
    is_win,
    is_ready,
    mcts_decision,
    shanten
)

def test_must_win_hand():
    """Test a hand that must win in one step"""
    hand = [9, 10, 11, 12, 13, 14, 27, 27]  # 1-2-3, 4-5-6, East-East
    wall = [15]  # 7
    discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=1000)
    assert discard is not None, "Should find a winning move"
    assert avg_steps < float('inf'), "Should have finite steps to win"
    assert stats['win_rate'] > 0, "Should have positive win rate"

def test_no_win_possible():
    """Test a hand with no possible win"""
    hand = [9, 9, 10, 10, 11, 11, 12, 12]  # All pairs
    wall = [13, 14, 15]  # No useful tiles
    discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=1000)
    assert discard is None, "Should not find a winning move"
    assert avg_steps == float('inf'), "Should have infinite steps to win"
    assert stats['win_rate'] == 0, "Should have zero win rate"

def test_ready_hand():
    """Test a hand that is ready to win"""
    hand = [9, 10, 11, 12, 13, 14, 27, 27]  # 1-2-3, 4-5-6, East-East
    ready_tiles = is_ready(hand)
    assert len(ready_tiles) > 0, "Should be ready to win"
    assert 15 in ready_tiles, "Should be waiting for 7"

def test_shanten_calculation():
    """Test shanten number calculation"""
    # Ready hand
    hand1 = [9, 10, 11, 12, 13, 14, 27, 27]
    assert shanten(hand1) == 0, "Should be ready to win"
    
    # One step away
    hand2 = [9, 10, 11, 12, 13, 15, 27, 27]
    assert shanten(hand2) == 1, "Should be one step away"

def test_mcts_parallel():
    """Test MCTS with different simulation counts"""
    hand = [9, 10, 11, 12, 13, 14, 27, 27]
    wall = [15, 16, 17]
    
    # Test with different simulation counts
    for n_sim in [100, 1000, 10000]:
        discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=n_sim)
        assert discard is not None, f"Should find a move with {n_sim} simulations"
        assert avg_steps < float('inf'), f"Should have finite steps with {n_sim} simulations"

if __name__ == "__main__":
    # Run all tests
    test_must_win_hand()
    test_no_win_possible()
    test_ready_hand()
    test_shanten_calculation()
    test_mcts_parallel()
    print("All tests passed!") 