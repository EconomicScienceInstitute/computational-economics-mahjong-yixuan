from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

class TileType(Enum):
    """Types of mahjong tiles"""
    CHARACTER = "character"  # Number tiles (wan)
    WIND = "wind"          # Wind tiles
    DRAGON = "dragon"      # Dragon tiles

@dataclass
class Tile:
    """Represents a single mahjong tile"""
    type: TileType
    value: int    # Numerical value for character tiles, 0 for others
    suit: str     # "wan" for characters, direction for winds, color for dragons

class Player:
    """Represents a player in the game"""
    def __init__(self, player_id: int):
        self.id = player_id
        self.hand: List[Tile] = []      # Tiles in hand
        self.melds: List[List[Tile]] = []  # Completed melds (chow/pung/kong)
        self.score = 0

    def add_tile(self, tile: Tile) -> None:
        """Add a tile to player's hand and sort it"""
        self.hand.append(tile)
        self.hand.sort(key=lambda x: (x.type.value, x.value))

    def show_hand(self) -> List[Tile]:
        """Return the tiles in player's hand"""
        return self.hand

    def get_melds(self) -> List[List[Tile]]:
        """Return the completed melds"""
        return self.melds

class Game:
    """Main game class that manages the game flow"""
    def __init__(self, players: List[Player]):
        if len(players) != 2:
            raise ValueError("This game only supports 2 players")
        self.players = players
        self.current_player_id = 0
        self.is_open_hand = True  # Open hand mode for debugging/learning
        self.wall: List[Tile] = []  # The wall of tiles
        self.discard_pile: List[Tile] = []  # Discarded tiles
        self._initialize_wall()

    def _initialize_wall(self) -> None:
        """Initialize the wall with all tiles for two-player mahjong"""
        self.wall = []
        
        # Character tiles (1-9, 4 of each)
        for value in range(1, 10):
            for _ in range(4):  # 4 of each tile
                self.wall.append(Tile(TileType.CHARACTER, value, "wan"))
        print(f"Character tiles: {len([t for t in self.wall if t.type == TileType.CHARACTER])}")  # Should be 36
        
        # Wind tiles (East, South, West, North, 4 of each)
        winds = ["east", "south", "west", "north"]
        for wind in winds:
            for _ in range(4):  # 4 of each wind tile
                self.wall.append(Tile(TileType.WIND, 0, wind))
        print(f"Wind tiles: {len([t for t in self.wall if t.type == TileType.WIND])}")  # Should be 16
        
        # Dragon tiles (Red, Green, White, 4 of each)
        dragons = ["red", "green", "white"]
        for dragon in dragons:
            for _ in range(4):  # 4 of each dragon tile
                self.wall.append(Tile(TileType.DRAGON, 0, dragon))
        print(f"Dragon tiles: {len([t for t in self.wall if t.type == TileType.DRAGON])}")  # Should be 12
        
        print(f"Total tiles: {len(self.wall)}")  # Should be 64

    def deal_tiles(self) -> None:
        """Deal initial tiles to players"""
        import random
        random.shuffle(self.wall)
        
        # Deal 13 tiles to each player
        for player in self.players:
            for _ in range(13):
                if self.wall:
                    tile = self.wall.pop()
                    player.add_tile(tile)
            
            # Show hands in open hand mode
            if self.is_open_hand:
                print(f"Player {player.id} hand: {[f'{tile.suit}{tile.value}' for tile in player.hand]}")

    def start_game(self) -> None:
        """Start the game"""
        self.deal_tiles()
        print("Game started!")

    def get_current_player(self) -> Player:
        """Get the current player"""
        return self.players[self.current_player_id]

    def next_player(self) -> None:
        """Switch to next player"""
        self.current_player_id = (self.current_player_id + 1) % 2 