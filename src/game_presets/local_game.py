import random

from src.game import Game
from src.game_presets.game_preset_utils import setup_num_turns
from src.parameters import DEFAULT_NUM_TURNS
from src.parameters import PLAYER_NAMES


def local_game(num_players: int = 3, use_advanced_ai: bool = True, num_turns: int = DEFAULT_NUM_TURNS,
               is_full: bool = False) -> Game:
    seed: int = random.randint(0, 100000)

    game_name = 'Test game ' + str(seed)

    num_turns = setup_num_turns(num_turns, num_players)

    game = Game(game_name=game_name, max_players=num_players, num_turns=num_turns,
                is_full=is_full)

    bot_name: str
    if use_advanced_ai:
        bot_name = "Advanced bot"
    else:
        bot_name = PLAYER_NAMES[1]
    game.add_local_player(name=f"{bot_name}-{seed}", is_observer=False, is_backup=use_advanced_ai)

    for i in range(1, num_players):
        game.add_local_player(name=f"{PLAYER_NAMES[i + 1]}-{seed + i}", is_observer=False)

    return game
