from src.game import Game
from src.parameters import DEFAULT_NUM_TURNS


def online_game(game_name: str, player_name: str, num_players: int = 1, use_advanced_ai: bool = True,
                num_turns: int = DEFAULT_NUM_TURNS,
                is_full: bool = False, is_observer: bool = False, password: str = '') -> Game:
    # Maybe have an option of either creating a game or joining an already made one? (with None parameters
    # it will be overridden by the server values,
    # and if the optional parameters don't match when creating a game that already exists a connection will be returned)
    if num_turns < 1:
        num_turns = DEFAULT_NUM_TURNS
    game = Game(game_name=game_name, max_players=num_players, num_turns=num_turns,
                is_full=is_full)

    game.add_local_player(name=player_name, password=password, is_observer=is_observer, is_backup=use_advanced_ai)

    return game
