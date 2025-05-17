import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))
from single_player_mahjong import init_tiles, is_win, mcts_decision, calc_score

def integration_test_game():
    hand, wall = init_tiles()
    steps = 0
    print(f"Initial hand: {hand}")
    while True:
        if len(hand) == 8 and is_win(hand):
            print(f"Win! Final hand: {hand} in {steps} steps.")
            total_score, base_score, combo_bonus, details = calc_score(hand, steps)
            print(f"Score: {total_score} (base: {base_score}, bonus: {combo_bonus}, details: {details})")
            break
        if not wall:
            print("Game Over: No more tiles in the wall. Could not form a winning hand.")
            print(f"Final hand: {hand}")
            break
        draw = wall.pop(0)
        hand.append(draw)
        print(f"Draw: {draw}, hand: {hand}")
        discard, avg_steps, stats = mcts_decision(hand, wall, n_sim=100)
        assert discard in hand, f"AI suggested discarding {discard}, which is not in hand {hand}"
        hand.remove(discard)
        print(f"Discard: {discard} (expected avg steps to win: {avg_steps:.2f})")
        steps += 1

if __name__ == '__main__':
    integration_test_game() 