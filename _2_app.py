from flask import Flask, render_template, jsonify, request, session
from _1_single_player_mahjong import init_tiles, is_win, mcts_decision, TOTAL_TILES
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
    return render_template('_3_index.html')

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
        'message': 'Game started! Choose a tile to discard (you need 8 tiles to win).'
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
    # Check hand size (allow 8, to be robust)
    if len(game_state['hand']) != 8:
        return jsonify({'error': 'Invalid hand size. Should be 8 tiles before discard.'})
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
    game_state['hand'].sort(key=lambda x: x['number'])
    game_state['wall'].sort(key=lambda x: x['number'])
    game_state['discarded'].sort(key=lambda x: x['number'])
    # Draw a new tile if possible (always try to keep 8 tiles after discard, unless wall is empty or game over)
    if not game_state['game_over'] and game_state['wall']:
        new_tile_idx = random.randrange(len(game_state['wall']))
        new_tile = game_state['wall'].pop(new_tile_idx)
        game_state['hand'].append(new_tile)
        game_state['hand'].sort(key=lambda x: x['number'])
        game_state['wall'].sort(key=lambda x: x['number'])
        game_state['steps'] += 1
        # Check for win ONLY when hand has 8 tiles
        current_tiles = [t['number'] for t in game_state['hand']]
        if len(current_tiles) == 8 and is_win(current_tiles):
            game_state['game_over'] = True
            score = calc_score(game_state['hand'], game_state['steps'])
            game_state['score'] = score
            game_state['message'] = f"Congratulations! You've won in {game_state['steps']} steps! Score: {score}"
        else:
            game_state['message'] = "Choose a tile to discard."
    else:
        # No more tiles to draw, just update message
        if not game_state['wall']:
            game_state['game_over'] = True
            game_state['message'] = "Game Over: No more tiles in the wall."
    session['game_state'] = game_state
    return jsonify(game_state)

@app.route('/api/ai_suggest', methods=['POST'])
def ai_suggest():
    if 'game_state' not in session:
        return jsonify({'error': 'No game in progress. Please start a new game.'})
    game_state = session['game_state']
    if game_state['game_over']:
        return jsonify({'error': 'Game is over. Start a new game.'})
    current_tiles = [t['number'] for t in game_state['hand']]
    wall_numbers = [t['number'] for t in game_state['wall']]
    suggested_discard, avg_steps, stats = mcts_decision(current_tiles, wall_numbers, n_sim=10000)
    if suggested_discard is not None:
        return jsonify({
            'suggested_discard': suggested_discard, 
            'avg_steps': avg_steps,
            'min_steps': stats['min_steps'],
            'max_steps': stats['max_steps'],
            'win_rate': stats['win_rate']
        })
    else:
        return jsonify({
            'suggested_discard': None, 
            'avg_steps': None, 
            'message': 'No clear winning path found.'
        })

def calc_score(hand, steps):
    score = 100 - steps
    # All manzu (characters): tile numbers 9-17
    if all(9 <= t['number'] <= 17 for t in hand):
        score += 10
    return max(score, 0)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0') 