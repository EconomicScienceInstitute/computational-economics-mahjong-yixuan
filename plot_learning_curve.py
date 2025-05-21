import pandas as pd
import matplotlib.pyplot as plt

# Read the results CSV file
results_path = 'results/q_learning_single_hand_results.csv'
df = pd.read_csv(results_path)

# Remove duplicate rows based on Training Episodes (if any)
df = df.drop_duplicates(subset=['Training Episodes'])

# Extract data for plotting
x = df['Training Episodes']
y_steps = df['Average Steps']
y_score = df['Average Total Score']

# Create the plot
plt.figure(figsize=(10, 5))
plt.plot(x, y_steps, marker='o', label='Average Steps to Win')
plt.plot(x, y_score, marker='s', label='Average Total Score')
plt.xlabel('Training Episodes')
plt.ylabel('Value')
plt.title('Q-learning Performance vs Training Episodes')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot as a PNG file
output_path = 'results/learning_curve.png'
plt.savefig(output_path)
plt.show()

print(f'Plot saved to {output_path}') 