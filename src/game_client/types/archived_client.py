import json
import time
from abc import ABC

from src.game_client.game_client import GameClient
from src.parameters import ARCHIVED_GAME_SPEED, MAX_ARCHIVED_GAME_DELAY, MIN_ARCHIVED_GAME_DELAY, ARCHIVED_GAME_TURN, \
    ARCHIVED_GAME_PAUSED


class ArchivedGameClient(GameClient, ABC):
    def __init__(self, file_path: str):
        super().__init__()

        with open(file_path, 'r') as f:
            self.__archive_file = json.load(f)

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
        return self.__archive_file[str(self.__current_turn[0])]["map"]

    def get_game_state(self) -> dict:
        return self.__archive_file[str(self.__current_turn[0])]["game_state"]

    def get_game_actions(self) -> dict:
        return self.__archive_file[str(self.__current_turn[0])]["game_actions"]

    def force_turn(self) -> bool:
        if ARCHIVED_GAME_PAUSED[0]:
            return False

        # Split sleep_time into smaller intervals
        interval: float = 0.01  # Check every 10 milliseconds
        elapsed: float = 0

        while elapsed < self.__get_sleep_time():
            if ARCHIVED_GAME_PAUSED[0]:
                return False

            time.sleep(interval)
            elapsed += interval

        self.__current_turn[0] += 1

        return True

    @property
    def __current_turn(self) -> list[int]:
        max_turn: int = self.__archive_file["0"]["game_state"]["num_turns"]

        if ARCHIVED_GAME_TURN[0] < 0:
            ARCHIVED_GAME_TURN[0] = 0
        if ARCHIVED_GAME_TURN[0] > max_turn:
            ARCHIVED_GAME_TURN[0] = max_turn

        return ARCHIVED_GAME_TURN

    def chat(self, msg) -> None:
        pass

    def server_move(self, move_dict: dict) -> None:
        raise NotImplementedError

    def server_shoot(self, shoot_dict: dict) -> None:
        raise NotImplementedError

    @staticmethod
    def __get_sleep_time() -> float:
        return ((1 - ARCHIVED_GAME_SPEED[0]) * MAX_ARCHIVED_GAME_DELAY +
                (ARCHIVED_GAME_SPEED[0]) * MIN_ARCHIVED_GAME_DELAY)
