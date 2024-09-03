from src.game import Game
from src.settings_utils import get_original_game_name_from_filename


def archived_game(file_name: str) -> Game:
    game_name = get_original_game_name_from_filename(file_name)
    game = Game(is_archived_game=True, game_name=game_name, replay_file=file_name)

    return game
