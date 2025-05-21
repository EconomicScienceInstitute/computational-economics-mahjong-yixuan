"""
Flask web application for Single Player Mahjong game.
Provides web interface and API endpoints for game operations.
Integrates with AI decision making using MCTS algorithm.
"""

from flask import Flask, render_template, jsonify, request, session
from single_player_mahjong import init_tiles, is_win, mcts_decision, TOTAL_TILES
from flask_session import Session
import os
from PIL import Image
import base64
from io import BytesIO
import random

# Initialize Flask application
app = Flask(__name__, template_folder='../frontend')

# Flask session configuration
# Uses filesystem to store session data
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# MCTS (Monte Carlo Tree Search) configuration
# Controls the number of simulations for AI decision making
DEFAULT_MCTS_SIMS = 10000  # Default number of simulations
MIN_MCTS_SIMS = 1000      # Minimum allowed simulations
MAX_MCTS_SIMS = 50000     # Maximum allowed simulations

def get_tile_image(tile_number):
    """Convert mahjong tile image to base64 string for web display
    
    Args:
        tile_number: Integer ID of the tile
        
    Returns:
        str: Base64 encoded image data with data URI scheme
        None: If image file not found
    """
    img_path = os.path.join(os.path.dirname(__file__), "..", "..", "img", "tiles", "small", f"{tile_number}.jpg")
    if os.path.exists(img_path):
        img = Image.open(img_path)
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    return None

@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Initialize a new game session
    
    Creates new hand and wall, converts tile images to base64,
    and initializes game state in session.
    
    Returns:
        JSON: Initial game state including hand and wall tiles
    """
    # Initialize new game tiles
    hand, wall = init_tiles()
    
    # Process hand tiles: sort and add image data
    hand_with_images = []
    for tile in sorted(hand):  # Sort hand tiles
        img_data = get_tile_image(tile)
        if img_data:
            hand_with_images.append({
                'number': tile,
                'image': img_data
            })
    
    # Process wall tiles: sort and add image data
    wall_with_images = []
    for tile in sorted(wall):  # Sort wall tiles
        img_data = get_tile_image(tile)
        if img_data:
            wall_with_images.append({
                'number': tile,
                'image': img_data
            })
    
    # Create initial game state
    game_state = {
        'hand': hand_with_images,
        'wall': wall_with_images,
        'discarded': [],          # Track discarded tiles
        'total_tiles': TOTAL_TILES, #
        'steps': 0,
        'game_over': False,
        'message': 'Game started! Choose a tile to discard (you need 8 tiles to win).'
    }
    session['game_state'] = game_state
    return jsonify(game_state)

def validate_game_state(game_state):
    """Validate game state integrity and rules
    
    Checks:
    - State completeness
    - Hand size limits
    - Tile duplicates
    - Tile format
    
    Args:
        game_state: Current game state dictionary
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not game_state:
        return False, "Invalid game state"
        
    # Check required state components
    required_keys = ['hand', 'wall', 'discarded', 'steps', 'game_over']
    if not all(key in game_state for key in required_keys):
        return False, "Incomplete game state"
        
    # Validate hand size (max 8 tiles)
    if len(game_state['hand']) > 8:
        return False, "Hand size exceeds maximum"
        
    # Validate tile format and count duplicates
    all_tiles = []
    for tile in game_state['hand'] + game_state['wall'] + game_state['discarded']:
        if not isinstance(tile, dict) or 'number' not in tile:
            return False, "Invalid tile format"
        all_tiles.append(tile['number'])
    
    # Each tile should appear at most twice (per game rules)
    for tile_num in set(all_tiles):
        if all_tiles.count(tile_num) > 2:
            return False, f"Tile {tile_num} appears more than twice"
            
    return True, None

@app.route('/api/discard/<int:tile>', methods=['POST'])
def discard_tile(tile):
    """Process player's tile discard action
    
    Workflow:
    1. Validate game state
    2. Remove discarded tile
    3. Draw new tile
    4. Check win condition
    5. Update game state
    
    Args:
        tile: Tile number to discard
        
    Returns:
        JSON: Updated game state or error message
    """
    # Validate session and game state
    if 'game_state' not in session:
        return jsonify({'error': 'No game in progress. Please start a new game.'})
        
    game_state = session['game_state']
    is_valid, error_msg = validate_game_state(game_state)
    if not is_valid:
        return jsonify({'error': error_msg})
    
    # Game state validation
    if game_state['game_over']:
        return jsonify({'error': 'Game is over. Start a new game.'})
        
    # Hand size check
    if len(game_state['hand']) != 8:
        return jsonify({'error': 'Invalid hand size. Should be 8 tiles before discard.'})
    if not 9 <= tile <= 33:  # Valid tile range check
        return jsonify({'error': 'Invalid tile number.'})
        
    try:
        # Process tile discard
        tile_found = False
        discarded_tile = None
        new_hand = []
        removed = False
        
        # Remove discarded tile from hand
        for t in game_state['hand']:
            if t['number'] == tile and not removed:
                discarded_tile = t
                removed = True
                tile_found = True
                continue
            new_hand.append(t)
            
        if not tile_found:
            return jsonify({'error': 'Tile not in hand.'})
            
        # Update game state
        game_state['hand'] = new_hand
        game_state['discarded'].append(discarded_tile)
        
        # Sort all tile collections
        game_state['hand'].sort(key=lambda x: x['number'])
        game_state['wall'].sort(key=lambda x: x['number'])
        game_state['discarded'].sort(key=lambda x: x['number'])
        
        # Draw new tile if available
        if not game_state['game_over'] and game_state['wall']:
            new_tile_idx = random.randrange(len(game_state['wall']))
            new_tile = game_state['wall'].pop(new_tile_idx)
            game_state['hand'].append(new_tile)
            game_state['hand'].sort(key=lambda x: x['number'])
            game_state['steps'] += 1
            
            # Immediately check win condition after drawing
            current_tiles = [t['number'] for t in game_state['hand']]
            if len(current_tiles) == 8 and is_win(current_tiles):
                game_state['game_over'] = True
                score = calc_score(game_state['hand'], game_state['steps'])
                game_state['score'] = score
                game_state['message'] = f"Congratulations! You've won in {game_state['steps']} steps! Score: {score}"
                session['game_state'] = game_state
                return jsonify(game_state)
            else:
                game_state['message'] = "Choose a tile to discard."
        else:
            if not game_state['wall']:
                game_state['game_over'] = True
                game_state['message'] = "Game Over: No more tiles in the wall."
                
        # Final state validation
        is_valid, error_msg = validate_game_state(game_state)
        if not is_valid:
            return jsonify({'error': f'Invalid game state after move: {error_msg}'})
            
        session['game_state'] = game_state
        return jsonify(game_state)
        
    except Exception as e:
        return jsonify({'error': f'Error processing move: {str(e)}'})

@app.route('/api/ai_suggest', methods=['POST'])
def ai_suggest():
    """Get AI move suggestion using MCTS
    
    Uses Monte Carlo Tree Search to simulate possible game outcomes
    and suggest the best tile to discard.
    
    Query params:
        n_sims: Number of MCTS simulations to run (optional)
        
    Returns:
        JSON: Suggested move and statistics
    """
    # Validate game session
    if 'game_state' not in session:
        return jsonify({'error': 'No game in progress. Please start a new game.'})
        
    game_state = session['game_state']
    if game_state['game_over']:
        return jsonify({'error': 'Game is over. Start a new game.'})
        
    # Validate hand size
    if len(game_state['hand']) != 8:
        return jsonify({'error': 'Invalid hand size. Should be 8 tiles.'})
        
    # Get and validate simulation count
    try:
        n_sims = int(request.args.get('n_sims', DEFAULT_MCTS_SIMS))
        n_sims = max(MIN_MCTS_SIMS, min(n_sims, MAX_MCTS_SIMS))
    except ValueError:
        n_sims = DEFAULT_MCTS_SIMS
        
    # Prepare data for AI
    current_tiles = [t['number'] for t in game_state['hand']]
    wall_numbers = [t['number'] for t in game_state['wall']]
    
    try:
        # Get AI suggestion
        suggested_discard, avg_steps, stats = mcts_decision(current_tiles, wall_numbers, n_sim=n_sims)
        
        if suggested_discard is not None:
            return jsonify({
                'suggested_discard': suggested_discard, 
                'avg_steps': avg_steps,
                'min_steps': stats['min_steps'],
                'max_steps': stats['max_steps'],
                'win_rate': stats['win_rate'],
                'simulations': n_sims
            })
        else:
            return jsonify({
                'suggested_discard': None, 
                'avg_steps': None, 
                'message': 'No clear winning path found.',
                'simulations': n_sims
            })
    except Exception as e:
        return jsonify({
            'error': f'Error during AI calculation: {str(e)}',
            'simulations': n_sims
        })

def calc_score(hand, steps):
    """Calculate final game score
    
    Scoring rules:
    - Base score = 100 - steps taken
    - Bonus +20 for all Character tiles (numbers 9-17)
    - Minimum score is 0
    
    Args:
        hand: List of tiles in winning hand
        steps: Number of steps taken to win
        
    Returns:
        int: Final score (base score + bonus, minimum 0)
    """
    base_score = 100 - steps
    bonus = 0
    
    # All Character tiles bonus
    if all(9 <= t['number'] <= 17 for t in hand):
        bonus += 20  # match README
        
    return max(base_score + bonus, 0)

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, port=8080, host='0.0.0.0') 