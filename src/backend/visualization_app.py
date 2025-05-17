from flask import Flask, jsonify, render_template, request
import pandas as pd
import os
import numpy as np

app = Flask(__name__, template_folder='../../templates')

@app.route('/')
def index():
    return render_template('visualization.html')

@app.route('/api/mcts_results')
def mcts_results():
    csv_path = os.path.join(os.path.dirname(__file__), '../../mcts_simulation_results.csv')
    df = pd.read_csv(csv_path)
    
    # Add additional statistics
    df['WinRate'] = df.groupby('HandName')['Win'].transform('mean') * 100
    
    # Calculate average steps for winning hands
    winning_hands = df[df['Win'] == 1]
    avg_steps = winning_hands.groupby('HandName')['Steps'].mean()
    df['AvgSteps'] = df['HandName'].map(avg_steps)
    
    # Remove simulation_stats calculation (no Simulations column)
    result = {
        'raw_data': df.to_dict(orient='records'),
        'hand_stats': df.groupby('HandName').agg({
            'Win': ['count', 'mean'],
            'Steps': ['mean', 'std']
        }).reset_index().to_dict(orient='records')
    }
    
    return jsonify(result)

@app.route('/api/hand_stats')
def hand_stats():
    csv_path = os.path.join(os.path.dirname(__file__), '../../mcts_simulation_results.csv')
    df = pd.read_csv(csv_path)
    
    # Calculate hand stats and flatten columns
    hand_stats_df = df.groupby('HandName').agg({
        'Win': ['count', 'mean'],
        'Steps': ['mean', 'std']
    }).reset_index()
    hand_stats_df.columns = ['HandName', 'Win_count', 'Win_mean', 'Steps_mean', 'Steps_std']

    result = {
        'raw_data': df.to_dict(orient='records'),
        'hand_stats': hand_stats_df.to_dict(orient='records')
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5002, debug=True) 