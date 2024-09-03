import datetime
import json
import os.path
import random
import struct

from src.game_client.game_client import GameClient
from src.parameters import HOST_PORT, HOST_NAME, BYTES_IN_INT, REPLAYS_LOCATION, CURRENT_GAME_NAME
from src.remote.server_connection import ServerConnection
from src.remote.server_enum import Action
from src.remote.server_enum import Result


class RemoteGameClient(GameClient):
    def __init__(self, is_shadow_client: bool = False):
        super().__init__()
        self.__is_shadow_client = is_shadow_client
        self.__server_connection = ServerConnection()
        self.__server_connection.connect(HOST_NAME, HOST_PORT)
        self.__current_turn: int = 0
        self.__recorded_actions: dict = {}
        self.__recorded_for_current_turn: dict = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    def disconnect(self) -> None:
        if self.__is_shadow_client:
            self.__record_unrecorded_actions()

            # Generate a timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Replace whitespaces in the game name with underscores
            cleaned_game_name = CURRENT_GAME_NAME[0].replace(" ", "_")

            # Reset current game name
            CURRENT_GAME_NAME[0] = ''

            # Create a filename with the timestamp first
            filename = f"{timestamp}_{cleaned_game_name}.replay"
            save_path = os.path.join(REPLAYS_LOCATION, filename)

            # Save JSON to the generated filename
            with open(save_path, 'w') as fp:
                json.dump(self.__recorded_actions, fp, indent='\t')

            print(f"Replay saved as {filename}")

        self.__server_connection.disconnect()

    def login(self, name: str, password: str | None = None, game_name: str | None = None,
              num_turns: int | None = None, num_players: int | None = None,
              is_observer: bool | None = None, is_full: bool | None = None) -> dict:
        if password is None:
            seed = random.randint(0, 10000)
            name = f"{name}-{seed}"

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
        self.__send_action(Action.LOGOUT)
        self.__receive_response()

    def get_map(self) -> dict:
        self.__send_action(Action.MAP)

        response = self.__receive_response()
        if self.__is_shadow_client:
            self.__recorded_actions.setdefault(self.__current_turn, {})["map"] = response
            self.__recorded_for_current_turn["map"] = True

        return response

    def get_game_state(self) -> dict:
        self.__send_action(Action.GAME_STATE)

        response = self.__receive_response()
        if self.__is_shadow_client:
            self.__recorded_actions.setdefault(self.__current_turn, {})["game_state"] = response
            self.__recorded_for_current_turn["game_state"] = True

        return response

    def get_game_actions(self) -> dict:
        self.__send_action(Action.GAME_ACTIONS)

        response = self.__receive_response()
        if self.__is_shadow_client:
            self.__recorded_actions.setdefault(self.__current_turn, {})["game_actions"] = response
            self.__recorded_for_current_turn["game_actions"] = True

        return response

    def force_turn(self) -> bool:
        try:
            if self.__is_shadow_client:
                self.__record_unrecorded_actions()

            self.__send_action(Action.TURN)
            self.__receive_response()

            if self.__is_shadow_client:
                self.__current_turn += 1
        except TimeoutError:
            return False
        else:
            return True

    def chat(self, msg) -> None:
        self.__send_action(Action.CHAT, {"message": msg})
        self.__receive_response()

    def server_move(self, move_dict: dict) -> None:
        self.__send_action(Action.MOVE, move_dict)
        self.__receive_response()

    def server_shoot(self, shoot_dict: dict) -> None:
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

    def __record_unrecorded_actions(self):
        if not self.__recorded_for_current_turn.get("map"):
            self.get_map()
        if not self.__recorded_for_current_turn.get("game_state"):
            self.get_game_state()
        if not self.__recorded_for_current_turn.get("game_actions"):
            self.get_game_actions()
        self.__recorded_for_current_turn = {}
