import json
import struct

from src.game_client.game_client import GameClient
from src.parameters import HOST_PORT, HOST_NAME, BYTES_IN_INT
from src.remote.server_connection import ServerConnection
from src.remote.server_enum import Action
from src.remote.server_enum import Result


class RemoteGameClient(GameClient):
    def __init__(self):
        super().__init__()
        self.__server_connection = ServerConnection()
        self.__server_connection.connect(HOST_NAME, HOST_PORT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    def disconnect(self) -> None:
        self.__server_connection.disconnect()

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

        d: dict = {
            "name": name,
            "password": password,
            "game": game_name,
            "num_turns": num_turns,
            "num_players": num_players,
            "is_observer": is_observer,
            "is_full": is_full
        }

        d = {k: v for k, v in d.items() if v is not None}

        self.__send_action(Action.LOGIN, d)
        return self.__receive_response()

    def logout(self) -> None:
        """
        User logout
        :param
        """
        self.__send_action(Action.LOGOUT)
        self.__receive_response()

    def get_map(self) -> dict:
        """
        Map request, return all map data in a dict
        :param
        :return: map dict
        """
        self.__send_action(Action.MAP)
        return self.__receive_response()

    def get_game_state(self) -> dict:
        """
        Game state request, returns the current game state
        :param
        :return: game state dict
        """
        self.__send_action(Action.GAME_STATE)
        return self.__receive_response()

    def get_game_actions(self) -> dict:
        """
        Game actions request, returns the actions that happened in the previous turn.
        Represent changes between turns.
        :return: game actions dict
        """
        self.__send_action(Action.GAME_ACTIONS)
        return self.__receive_response()

    def force_turn(self) -> bool:
        """
        Needed to force the next turn of the game instead of waiting for the game's time slice.
        :param
        :return: 0 if turn has happened, -1 otherwise (TIMEOUT error)
        """
        try:
            self.__send_action(Action.TURN)
            self.__receive_response()
        except TimeoutError:
            return False
        else:
            return True

    def chat(self, msg) -> None:
        """
        Chat, just for fun and testing
        :param msg: message sent
        """
        self.__send_action(Action.CHAT, {"message": msg})
        self.__receive_response()

    def server_move(self, move_dict: dict) -> None:
        """
        Changes vehicle position
        """
        self.__send_action(Action.MOVE, move_dict)
        self.__receive_response()

    def server_shoot(self, shoot_dict: dict) -> None:
        """
        Shoot at a hex position
        """
        self.__send_action(Action.SHOOT, shoot_dict)
        self.__receive_response()

    @staticmethod
    def __unpack_header(data: bytes) -> tuple[int, int]:
        resp_code, msg_len = struct.unpack('ii', data[:8])
        return resp_code, msg_len

    @staticmethod
    def __unpack(data: bytes) -> dict:
        return json.loads(data)

    @staticmethod
    def __pack(act: Action, dct: dict) -> bytes:
        msg: bytes = b''
        if dct:
            msg = bytes(json.dumps(dct), 'utf-8')
        return struct.pack('ii', act, len(msg)) + msg

    def __send_action(self, act: Action, dct: dict | None = None) -> None:
        if not dct:
            dct = {}

        out: bytes = self.__pack(act, dct)

        if not self.__server_connection.send_data(out):
            raise ConnectionError("Error: Data was not sent correctly.")

    def __receive_response(self) -> dict:
        resp_code: int
        msg_len: int

        try:
            data: bytes = self.__server_connection.receive_data(message_size=BYTES_IN_INT * 2)
        except EOFError:
            raise ConnectionError("Error: Could not receive message header.")

        resp_code, msg_len = self.__unpack_header(data)

        if msg_len <= 0:
            return {}

        try:
            msg: bytes = self.__server_connection.receive_data(message_size=msg_len)
        except EOFError:
            raise ConnectionError("Error: Could not receive message body.")

        dct: dict = self.__unpack(msg)

        if resp_code == Result.TIMEOUT:
            raise TimeoutError(f"Error {resp_code}: {dct['error_message']}")
        elif resp_code != Result.OKEY:
            raise ConnectionError(f"Error {resp_code}: {dct['error_message']}")

        return dct
