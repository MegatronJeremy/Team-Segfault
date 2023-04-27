from abc import abstractmethod
from typing import Dict

from ..entity.tanks.tank import Tank
from ..map.map import Map


class Player:
    __type_order = ('spg', 'light_tank', 'heavy_tank', 'medium_tank', 'at_spg')

    def __init__(self, idx: int):

        self._idx: int = idx
        self._map: Map | None = None

        self._damage_points = 0
        self._capture_points = 0
        self.__winner: bool = False

        self._tanks: list[Tank] = []
        self.__has_shot = []  # Holds a list of enemies this player has shot last turn

    def add_tank(self, new_tank: Tank) -> None:
        # Adds the tank in order of who gets priority movement
        new_tank_priority = Player.__type_order.index(new_tank.get_type())
        for i, old_tank in enumerate(self._tanks):
            old_tank_priority = Player.__type_order.index(old_tank.get_type())
            if new_tank_priority <= old_tank_priority:
                self._tanks.insert(i, new_tank)
                return
        self._tanks.append(new_tank)

    def add_map(self, game_map: Map):
        self._map = game_map

    def run(self) -> None: self._make_turn_plays()

    def get_index(self): return self._idx

    def get_tanks(self): return self._tanks

    def has_shot(self, player_index: int) -> bool: return player_index in self.__has_shot

    def get_capture_points(self) -> int: return sum(tank.get_cp() for tank in self._tanks)

    def get_damage_points(self) -> int: return self._damage_points

    def register_shot(self, enemy_index: int) -> None: self.__has_shot.append(enemy_index)

    def register_turn(self) -> None: self.__has_shot = []

    def register_destroyed_vehicle(self, tank: Tank) -> None:
        self._damage_points += tank.get_max_hp()

    def is_winner(self) -> bool: return self.__winner

    @abstractmethod
    def _make_turn_plays(self) -> None: pass