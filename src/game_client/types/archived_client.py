import json
import time
from abc import ABC

from src.game_client.game_client import GameClient
from src.parameters import ARCHIVED_GAME_SPEED, MAX_ARCHIVED_GAME_DELAY, MIN_ARCHIVED_GAME_DELAY


class ArchivedGameClient(GameClient, ABC):
    def __init__(self, file_path: str):
        super().__init__()

        with open(file_path, 'r') as f:
            self.__archive_file = json.load(f)

        self.__current_turn: int = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        del self.__archive_file

    def disconnect(self) -> None:
        pass

    def login(self, name: str, password: str | None = None, game_name: str | None = None,
              num_turns: int | None = None, num_players: int | None = None,
              is_observer: bool | None = None, is_full: bool | None = None) -> dict:

        # Login should only be possible for the shadow client, no local players should exist here
        if not name.find("Team-Segfault-Shadow"):
            raise NameError

        return {}

    def logout(self) -> None:
        pass

    def get_map(self) -> dict:
        return self.__archive_file[str(self.__current_turn)]["map"]

    def get_game_state(self) -> dict:
        return self.__archive_file[str(self.__current_turn)]["game_state"]

    def get_game_actions(self) -> dict:
        return self.__archive_file[str(self.__current_turn)]["game_actions"]

    def force_turn(self) -> bool:
        try:
            time.sleep(
                ARCHIVED_GAME_SPEED * MAX_ARCHIVED_GAME_DELAY + (1 - ARCHIVED_GAME_SPEED) * MIN_ARCHIVED_GAME_DELAY)
            self.__current_turn += 1
        except TimeoutError:
            return False
        else:
            return True

    def chat(self, msg) -> None:
        pass

    def server_move(self, move_dict: dict) -> None:
        raise NotImplementedError

    def server_shoot(self, shoot_dict: dict) -> None:
        raise NotImplementedError
