from flask import Flask, render_template, jsonify, request, session
from single_player_mahjong import init_tiles, is_win, mcts_decision, TOTAL_TILES
from flask_session import Session
import os
from PIL import Image
import base64
from io import BytesIO
import random

app = Flask(__name__)
# Configure Flask-Session
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def get_tile_image(tile_number):
    """Convert tile image to base64 string"""
    img_path = os.path.join(os.path.dirname(__file__), "img", "tiles", "small", f"{tile_number}.jpg")
    if os.path.exists(img_path):
        img = Image.open(img_path)
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    hand, wall = init_tiles()
    # Convert hand tiles to include image data
    hand_with_images = []
    for tile in sorted(hand):  # Sort hand tiles
        img_data = get_tile_image(tile)
        if img_data:
            hand_with_images.append({
                'number': tile,
                'image': img_data
            })
    
    # Convert wall tiles to include image data
    wall_with_images = []
    for tile in sorted(wall):  # Sort wall tiles
        img_data = get_tile_image(tile)
        if img_data:
            wall_with_images.append({
                'number': tile,
                'image': img_data
            })
    
    game_state = {
        'hand': hand_with_images,
        'wall': wall_with_images,
        'discarded': [],  # Track discarded tiles
        'total_tiles': TOTAL_TILES,  # Add total tiles count
        'steps': 0,
        'game_over': False,
        'message': 'Game started! Choose a tile to discard.'
    }
    session['game_state'] = game_state
    return jsonify(game_state)

@app.route('/api/discard/<int:tile>', methods=['POST'])
def discard_tile(tile):
    if 'game_state' not in session:
        return jsonify({'error': 'No game in progress. Please start a new game.'})
    
    game_state = session['game_state']
    if game_state['game_over']:
        return jsonify({'error': 'Game is over. Start a new game.'})
    
    # Check hand size
    if len(game_state['hand']) != 7:
        return jsonify({'error': 'Invalid hand size. Should be 7 tiles.'})
    
    # Find tile in hand and remove it
    tile_found = False
    discarded_tile = None
    new_hand = []
    removed = False
    
    for t in game_state['hand']:
        if t['number'] == tile and not removed:
            discarded_tile = t
            removed = True
            tile_found = True
            continue
        new_hand.append(t)
    
    if not tile_found:
        return jsonify({'error': 'Invalid tile.'})
    
    # Update hand and add to discarded list
    game_state['hand'] = new_hand
    game_state['discarded'].append(discarded_tile)
    
    # Sort all tile arrays by number
    game_state['hand'].sort(key=lambda x: x['number'])
    game_state['wall'].sort(key=lambda x: x['number'])
    game_state['discarded'].sort(key=lambda x: x['number'])
    
    # Draw a new tile if possible
    if game_state['wall']:
        # Randomly select a tile from wall
        new_tile_idx = random.randrange(len(game_state['wall']))
        new_tile = game_state['wall'].pop(new_tile_idx)
        game_state['hand'].append(new_tile)
        
        # Verify hand size after drawing
        if len(game_state['hand']) != 7:
            print(f"Warning: Hand size is {len(game_state['hand'])} after draw")
        
        # Sort again after drawing new tile
        game_state['hand'].sort(key=lambda x: x['number'])
        game_state['wall'].sort(key=lambda x: x['number'])
        
        game_state['steps'] += 1
        
        # Check for win
        current_tiles = [t['number'] for t in game_state['hand']]
        if len(current_tiles) == 8 and is_win(current_tiles):
            game_state['game_over'] = True
            game_state['message'] = f"Congratulations! You've won in {game_state['steps']} steps!"
        else:
            # Get AI suggestion
            wall_numbers = [t['number'] for t in game_state['wall']]
            suggested_discard, avg_steps = mcts_decision(current_tiles, wall_numbers, n_sim=1000)
            if suggested_discard is not None:
                game_state['message'] = f"AI suggests discarding {suggested_discard} (expected {avg_steps:.1f} steps to win)"
            else:
                game_state['message'] = "No clear winning path found. Try your best!"
    else:
        game_state['game_over'] = True
        game_state['message'] = "Game Over: No more tiles in the wall."
    
    session['game_state'] = game_state
    return jsonify(game_state)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0') 