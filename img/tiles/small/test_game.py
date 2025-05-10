from game import Game, Player, Tile, TileType

def test_game_initialization():
    # Create two players
    players = [Player(0), Player(1)]
    game = Game(players)
    
    # Test wall initialization
    assert len(game.wall) == 64  # Total 64 tiles for two-player mahjong
    
    # Test character tiles count
    character_tiles = [t for t in game.wall if t.type == TileType.CHARACTER]
    assert len(character_tiles) == 36  # 36 character tiles (1-9, 4 each)
    
    # Test wind tiles count
    wind_tiles = [t for t in game.wall if t.type == TileType.WIND]
    assert len(wind_tiles) == 16  # 16 wind tiles (4 types, 4 each)
    
    # Test dragon tiles count
    dragon_tiles = [t for t in game.wall if t.type == TileType.DRAGON]
    assert len(dragon_tiles) == 12  # 12 dragon tiles (3 types, 4 each)
    
    # Test dealing
    game.deal_tiles()
    for player in players:
        assert len(player.hand) == 13  # Each player gets 13 tiles

def test_player_hand():
    player = Player(0)
    tile1 = Tile(TileType.CHARACTER, 1, "wan")
    tile2 = Tile(TileType.CHARACTER, 2, "wan")
    tile3 = Tile(TileType.WIND, 0, "east")
    
    player.add_tile(tile2)
    player.add_tile(tile1)
    player.add_tile(tile3)
    
    # Test hand sorting
    hand = player.show_hand()
    assert hand[0] == tile1  # Character tiles should come first
    assert hand[1] == tile2
    assert hand[2] == tile3  # Wind tiles should come after characters

if __name__ == "__main__":
    test_game_initialization()
    test_player_hand()
    print("All tests passed!") 