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
        """
        User login
        :param name: player username
        :param password: player password
        :param game_name: define the game player_name to create or join if it already exists
        :param num_turns: number of game turns (if creating a game)
        :param num_players: number of game players (if creating a game)
        :param is_observer: define if joining as an observer
        :param is_full: define if you want to play the full game with all combinations of player order
        :return: user dict
        """
        pass

    @abstractmethod
    def logout(self) -> None:
        """
        User logout
        :param
        """
        pass

    @abstractmethod
    def get_map(self) -> dict:
        """
        Map request, return all map data in a dict
        :param
        :return: map dict
        """
        pass

    @abstractmethod
    def get_game_state(self) -> dict:
        """
        Game state request, returns the current game state
        :param
        :return: game state dict
        """
        pass

    @abstractmethod
    def get_game_actions(self) -> dict:
        """
        Game actions request, returns the actions that happened in the previous turn.
        Represent changes between turns.
        :return: game actions dict
        """
        pass

    @abstractmethod
    def force_turn(self) -> bool:
        """
        Needed to force the next turn of the game instead of waiting for the game's time slice.
        :param
        :return: 0 if turn has happened, -1 otherwise (TIMEOUT error)
        """
        pass

    @abstractmethod
    def chat(self, msg) -> None:
        """
        Chat, just for fun and testing
        :param msg: message sent
        """
        pass

    @abstractmethod
    def server_move(self, move_dict: dict) -> None:
        """
        Changes vehicle position
        """
        pass

    @abstractmethod
    def server_shoot(self, shoot_dict: dict) -> None:
        """
        Shoot at a hex position
        """
        pass
