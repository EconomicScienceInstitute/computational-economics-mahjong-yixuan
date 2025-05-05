from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
from config import TileType, ClaimType, config, TILE_NAMES

class Tile:
    def __init__(self, type: TileType, value: int, suit: Optional[str] = None):
        self.type = type
        self.value = value
        self.suit = suit
        
    @property
    def name(self) -> str:
        """Get the tile name from the mapping"""
        tile_id = self._get_tile_id()
        return TILE_NAMES.get(tile_id, "unknown")
    
    def _get_tile_id(self) -> int:
        """Convert tile attributes to tile ID for name lookup"""
        if self.type == TileType.BAMBOO:
            return self.value - 1
        elif self.type == TileType.CHARACTER:
            return self.value + 8
        elif self.type == TileType.DOT:
            return self.value + 17
        elif self.type == TileType.WIND:
            return self.value + 26  # 27-30 for winds
        elif self.type == TileType.DRAGON:
            return self.value + 30  # 31-33 for dragons
        elif self.type == TileType.FLOWER:
            return 34
        return 0

class Player:
    """Represents a player in the game"""
    def __init__(self, id: int):
        self.id = id
        self.hand: List[Tile] = []      # Tiles in hand
        self.discards: List[Tile] = []
        self.claimed_sets: List[List[Tile]] = []
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
        return self.claimed_sets

class Game:
    """Main game class that manages the game flow"""
    def __init__(self, players: List[Player]):
        if len(players) != 2:
            raise ValueError("This game only supports 2 players")
        self.players = players
        self.current_player = 0
        self.is_open_hand = True  # Open hand mode for debugging/learning
        self.wall: List[Tile] = []  # The wall of tiles
        self.discard_pile: List[Tile] = []  # Discarded tiles
        self.rules = config.RULES
        self.debug = config.DEBUG
        self._initialize_wall()

    def _initialize_wall(self) -> None:
        """Initialize the wall with all tiles for two-player mahjong"""
        self.wall = []
        
        # Character tiles (1-9, 4 of each)
        for value in range(1, 10):
            for _ in range(4):  # 4 of each tile
                self.wall.append(Tile(TileType.CHARACTER, value))
        print(f"Character tiles: {len([t for t in self.wall if t.type == TileType.CHARACTER])}")  # Should be 36
        
        # Wind tiles (East, South, West, North, 4 of each)
        winds = ["east", "south", "west", "north"]
        for value in range(4):
            for _ in range(4):
                self.wall.append(Tile(TileType.WIND, value, winds[value]))
        print(f"Wind tiles: {len([t for t in self.wall if t.type == TileType.WIND])}")  # Should be 16
        
        # Dragon tiles (Red, Green, White, 4 of each)
        dragons = ["green", "red", "white"]
        for value in range(3):
            for _ in range(4):  # 4 of each dragon tile
                self.wall.append(Tile(TileType.DRAGON, value, dragons[value]))
        print(f"Dragon tiles: {len([t for t in self.wall if t.type == TileType.DRAGON])}")  # Should be 12
        
        # Add flower tiles
        self.wall.append(Tile(TileType.FLOWER, 1))
        
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
        return self.players[self.current_player]

    def next_player(self) -> None:
        """Switch to next player"""
        self.current_player = (self.current_player + 1) % 2 

    def can_claim_tile(self, player: Player, tile: Tile) -> ClaimType:
        """Check if a player can claim a discarded tile"""
        result = ClaimType.IGNORE
        
        # Count how many matching tiles the player has
        matching_tiles = sum(1 for t in player.hand if t.type == tile.type and t.value == tile.value)
        
        # Check for Pung (3 of a kind)
        if matching_tiles >= 2:
            result |= ClaimType.PUNG
            
        # Check for Kong (4 of a kind)
        if matching_tiles >= 3:
            result |= ClaimType.KONG
            
        # Check for Chow (sequence of 3)
        if tile.type in [TileType.BAMBOO, TileType.CHARACTER, TileType.DOT]:
            # Check if we can form a sequence
            values_in_hand = [t.value for t in player.hand if t.type == tile.type]
            
            # Check CHOW1 (X**)
            if tile.value <= 7 and (tile.value + 1) in values_in_hand and (tile.value + 2) in values_in_hand:
                result |= ClaimType.CHOW1
                
            # Check CHOW2 (*X*)
            if tile.value >= 2 and tile.value <= 8 and (tile.value - 1) in values_in_hand and (tile.value + 1) in values_in_hand:
                result |= ClaimType.CHOW2
                
            # Check CHOW3 (**X)
            if tile.value >= 3 and (tile.value - 2) in values_in_hand and (tile.value - 1) in values_in_hand:
                result |= ClaimType.CHOW3
        
        return result 