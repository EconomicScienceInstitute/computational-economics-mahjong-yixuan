from sys import path
from os.path import abspath, dirname, join
path.append(abspath(join(dirname(__file__), '../src/backend')))
from auto_train_mcts import dp, dp_calls, calc_score
from collections import Counter
import csv
import os

def run_qingyise_dp_analysis(n_runs=20):
    """
    Run DP analysis for Qingyise (all manzu) hand multiple times
    """
    results = []
    print(f"\nRunning DP analysis for Qingyise hand {n_runs} times...")
    
    for run in range(n_runs):
        # Hand: 1-8 manzu (9-16), wall: remaining manzu tiles (9-17, each 2 copies, minus hand)
        hand = [9, 10, 11, 12, 13, 14, 15, 16]  # 1-8 manzu
        wall = [i for i in range(9, 18)] * 2  # 1-9 manzu, 2 copies each
        for t in hand:
            wall.remove(t)
        
        hand_tuple = tuple(sorted(hand))
        wall_counter_tuple = tuple(sorted(Counter(wall).items()))
        min_steps = dp(hand_tuple, wall_counter_tuple)
        score, base_score, combo_bonus, details = calc_score(hand, min_steps)
        
        print(f"\nRun {run + 1}/{n_runs}:")
        print(f"Hand: {hand}")
        print(f"Wall: {wall}")
        print(f"Minimal steps to win (DP): {min_steps}")
        print(f"Optimal score (DP): {score} (Base: {base_score}, Bonus: {combo_bonus}, Details: {details})")
        
        results.append({
            'run': run + 1,
            'hand': hand,
            'wall': wall,
            'min_steps': min_steps,
            'score': score,
            'base_score': base_score,
            'combo_bonus': combo_bonus,
            'details': details
        })
    
    # Save results to CSV
    results_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'qingyise_dp_results.csv')
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(results_path)
    
    with open(results_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Run', 'Hand', 'Wall', 'MinSteps', 'Score', 'BaseScore', 'Bonus', 'Details'])
        
        for result in results:
            writer.writerow([
                result['run'],
                ' '.join(map(str, result['hand'])),
                ' '.join(map(str, result['wall'])),
                result['min_steps'],
                result['score'],
                result['base_score'],
                result['combo_bonus'],
                '; '.join(result['details'])
            ])
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("=" * 50)
    min_steps_list = [r['min_steps'] for r in results]
    score_list = [r['score'] for r in results]
    print(f"Average minimal steps: {sum(min_steps_list)/len(min_steps_list):.2f}")
    print(f"Average score: {sum(score_list)/len(score_list):.2f}")
    print(f"Minimal steps range: {min(min_steps_list)} to {max(min_steps_list)}")
    print(f"Score range: {min(score_list)} to {max(score_list)}")
    print(f"\nResults saved to: {results_path}")

if __name__ == "__main__":
    run_qingyise_dp_analysis(20) 