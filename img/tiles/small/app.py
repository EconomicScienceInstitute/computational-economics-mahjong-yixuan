import plotly.graph_objects as go
from game import Game, Player, Tile, TileType
import os
from PIL import Image
import base64
from io import BytesIO

def get_tile_image(tile):
    """Get the image for a specific tile"""
    # Map tile to image number
    if tile.type == TileType.CHARACTER:
        # Characters 1-9 map to images 0-8
        img_num = tile.value - 1
    else:
        # Map other tiles to specific numbers
        suit_map = {
            'east': 9,
            'south': 10,
            'west': 11,
            'north': 12,
            'white': 13,
            'green': 14,
            'red': 15
        }
        img_num = suit_map.get(tile.suit.lower(), 0)
    
    # Load image
    img_path = os.path.join(os.path.dirname(__file__), "..", "img", "tiles", "small", f"{img_num}.jpg")
    if os.path.exists(img_path):
        img = Image.open(img_path)
        # Convert image to base64 string
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    return None

def create_game_board():
    # Create game instance
    players = [Player(0), Player(1)]
    game = Game(players)
    game.start_game()
    
    # Create figure
    fig = go.Figure()
    
    # Add player hands
    for i, player in enumerate(game.players):
        y_pos = 0.8 if i == 0 else 0.2  # Player 0 at top, Player 1 at bottom
        
        # Add player label
        fig.add_annotation(
            x=0,
            y=y_pos + 0.1,
            text=f"Player {i+1}",
            showarrow=False,
            font=dict(size=16, color='black'),
        )
        
        # Add tiles
        for j, tile in enumerate(player.hand):
            # Get tile image
            img_src = get_tile_image(tile)
            if img_src:
                fig.add_layout_image(
                    source=img_src,
                    x=0.1 + j*0.065,  # Reduced spacing between tiles
                    y=y_pos,        # Vertical position
                    xref="paper",
                    yref="paper",
                    sizex=0.06,     # Slightly smaller tiles
                    sizey=0.1,      # Slightly smaller tiles
                    xanchor="center",
                    yanchor="middle"
                )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Two-Player Mahjong",
            font=dict(size=24),
            y=0.95
        ),
        showlegend=False,
        plot_bgcolor='#E8F5E9',  # Light green background
        width=1500,  # Increase width
        height=800,  # Increase height
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[-0.1, 1.0]  # Adjusted x-axis range
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[0, 1]  # Keep y-axis range
        )
    )
    
    return fig

def show_game():
    fig = create_game_board()
    fig.show(renderer="browser") 