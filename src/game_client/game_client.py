from abc import ABC, abstractmethod


class GameClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def login(self, name: str, password: str | None = None, game_name: str | None = None,
              num_turns: int | None = None, num_players: int | None = None,
              is_observer: bool | None = None, is_full: bool | None = None) -> dict:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    @abstractmethod
    def get_map(self) -> dict:
        pass

    @abstractmethod
    def get_game_state(self) -> dict:
        pass

    @abstractmethod
    def get_game_actions(self) -> dict:
        pass

    @abstractmethod
    def force_turn(self) -> bool:
        pass

    @abstractmethod
    def chat(self, msg) -> None:
        pass

    @abstractmethod
    def server_move(self, move_dict: dict) -> None:
        pass

    @abstractmethod
    def server_shoot(self, shoot_dict: dict) -> None:
        pass
