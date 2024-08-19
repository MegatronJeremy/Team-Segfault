import traceback
from abc import abstractmethod, ABC
from dataclasses import dataclass
from threading import Thread, Semaphore, Event

from src.entities.tanks.tank import Tank
from src.game_client.game_client import GameClient
from src.game_map.map import Map
from src.parameters import PLAYER_COLORS


@dataclass
class Player(Thread, ABC):
    """ Abstract base player class """
    __type_order = ('spg', 'light_tank', 'heavy_tank', 'medium_tank', 'at_spg')

    def __init__(self, turn_played_sem: Semaphore, current_player: list[int], current_turn: list[int],
                 over: Event, game_exited: Event,
                 name: str | None = None, password: str | None = None,
                 is_observer: bool | None = None):
        super().__init__()

        self.idx: int = -1
        self.player_name: str | None = name
        self.password: str | None = password
        self.is_observer: bool | None = is_observer

        self.next_turn_sem = Semaphore(0)
        self._current_player = current_player
        self._current_turn = current_turn
        self._num_players: int = 0
        self.__turn_played_sem = turn_played_sem
        self.__over = over
        self.__game_exited = game_exited

        # Check if player was interrupted
        self.__interrupted = False

        self._game_client: GameClient | None = None
        self._map: Map | None = None

        self._damage_points: int = 0
        self._capture_points: int = 0
        self._tanks: list[Tank] = []
        self.__player_color: tuple | None = None
        self.__has_shot: list[int] = []  # Holds a list of enemies this player has shot last turn

    def __hash__(self):
        return super.__hash__(self)

    def __str__(self):
        out = str.format(f'Player {self.idx}: {self.player_name}')
        if self.is_observer:
            out += ', observer'

        return out

    def add_to_game(self, player_info: dict, game_client: GameClient) -> None:
        self.player_name = player_info["name"]
        self.idx = player_info["idx"]
        self.is_observer = player_info["is_observer"]
        self._game_client = game_client

    def add_tank(self, new_tank: Tank) -> None:
        # Adds the tank in order of who gets priority movement
        new_tank_priority = Player.__type_order.index(new_tank.type)
        for i, old_tank in enumerate(self._tanks):
            old_tank_priority = Player.__type_order.index(old_tank.type)
            if new_tank_priority <= old_tank_priority:
                self._tanks.insert(i, new_tank)
                return
        self._tanks.append(new_tank)

    def add_map(self, game_map: Map) -> None:
        self._map = game_map

    def run(self) -> None:
        while not self.__over.is_set():
            # wait for condition
            self.next_turn_sem.acquire()

            try:
                # check if the game ended
                if self.__over.is_set():
                    break

                self._make_turn_plays()

            except (ConnectionError, TimeoutError) as err:
                print(err)
            except Exception:
                traceback.print_exc()
            finally:
                # notify condition
                self.__turn_played_sem.release()

        # wait for the game to finalize
        self.__game_exited.wait()

        if not self.__interrupted:
            self._logout()

    """     GETTERS AND SETTERS    """

    @property
    def color(self) -> tuple:
        return self.__player_color

    @property
    def tanks(self) -> list[Tank]:
        return self._tanks

    @property
    def capture_points(self) -> int:
        return sum([tank.capture_points for tank in self._tanks])

    @capture_points.setter
    def capture_points(self, capture_points: int) -> None:
        self._capture_points = capture_points

    @property
    def damage_points(self) -> int:
        return self._damage_points

    @damage_points.setter
    def damage_points(self, damage_points: int) -> None:
        self._damage_points = damage_points

    def set_color_index(self, player_index: int) -> None:
        # set and update player index if player is not an observer
        self.__player_color = PLAYER_COLORS[player_index]

    @property
    def num_players(self) -> int:
        return self._num_players

    @num_players.setter
    def num_players(self, num_players: int) -> None:
        self._num_players = num_players

    @property
    def interrupted(self) -> bool:
        return self.__interrupted

    @interrupted.setter
    def interrupted(self, interrupted: bool) -> None:
        self.__interrupted = interrupted

    """     MISC        """

    def register_shot(self, enemy_index: int) -> None:
        self.__has_shot.append(enemy_index)

    def register_round(self) -> None:
        self._damage_points = 0
        self._tanks = []

    def register_turn(self) -> None:
        self.__has_shot = []

    def register_destroyed_vehicle(self, tank: Tank) -> None:
        self._damage_points += tank.max_health_points

    def has_shot(self, player_index: int) -> bool:
        return player_index in self.__has_shot

    """     ABSTRACTS       """

    @abstractmethod
    def _logout(self) -> None:
        pass

    @abstractmethod
    def _make_turn_plays(self) -> None:
        pass
