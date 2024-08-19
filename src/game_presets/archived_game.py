from src.game import Game


def archived_game(file_name: str) -> Game:
    game = Game(game_name=file_name, is_archived_game=True)

    return game
