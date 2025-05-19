import pandas as pd
import os

# Get absolute path to results file
results_path = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'mcts_q_compare_results.csv')
results_path = os.path.abspath(results_path)

# Load the results CSV file
df = pd.read_csv(results_path)

# Filter only winning games
df_win = df[df['Win'] == 1]

# Print details for each method
for method in ['MCTS', 'MCTS+Q']:
    print(f"\n{method} Results (winning games):")
    sub = df_win[df_win['Method'] == method]
    for idx, row in sub.iterrows():
        print(f"Game {int(row['Game'])}: Steps = {int(row['Steps'])}, Total Score = {int(row['Total Score'])}")

# Print average comparison at the end
print("\nAverage Comparison:")
for method in ['MCTS', 'MCTS+Q']:
    sub = df_win[df_win['Method'] == method]
    avg_steps = sub['Steps'].mean()
    avg_score = sub['Total Score'].mean()
    print(f"{method}: Average Steps = {avg_steps:.2f}, Average Total Score = {avg_score:.2f}") 