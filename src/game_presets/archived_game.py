from src.game import Game


def archived_game(file_name: str) -> Game:
    game = Game(is_archived_game=True, replay_file=file_name)

    return game
