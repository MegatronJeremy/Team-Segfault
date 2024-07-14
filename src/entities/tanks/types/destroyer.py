from abc import ABC

from src.entities.map_features.bonuses.catapult import get_catapult_bonus_range
from src.entities.tanks.tank import Tank
from src.game_map.hex import Hex
from src.parameters import TD_IMAGE_PATH


class TankDestroyer(Tank, ABC):
    __sp: int = 1  # Speed Points
    __dp: int = 2  # Destruction Points
    __max_range: int = 3  # Manhattan max range
    __min_range: int = 1  # Manhattan min range
    __catapult_range: int = __max_range + get_catapult_bonus_range()  # Manhattan max range when in catapult hex

    # Creates fire deltas normally but avoids adding coords which don't contain 0s creating the TDs fire pattern
    __fire_deltas = tuple(coord for coord in Hex.fire_deltas(__min_range, __max_range) if 0 in coord)
    __catapult_deltas = tuple(coord for coord in Hex.fire_deltas(__max_range, __catapult_range) if 0 in coord)

    __fire_corridor_deltas: tuple = Hex.td_fire_corridor_deltas(__max_range)
    __catapult_corridor_deltas: tuple = Hex.td_fire_corridor_deltas(__catapult_range)
    __all_deltas: tuple = __fire_deltas + __catapult_deltas

    def __init__(self, tank_id: int, tank_info: dict, colour: tuple, player_index: int):
        super().__init__(tank_id, tank_info, colour, player_index, TD_IMAGE_PATH)

    def coords_in_range(self) -> tuple:
        # Return all the coords in range of this tank taking into account if it has picked up the catapult bonus
        deltas = self.__all_deltas if self._catapult_bonus else self.__fire_deltas
        return tuple(Hex.coord_sum(delta, self._coord) for delta in deltas)

    def shot_moves(self, target: tuple) -> tuple:
        # returns coords to where "self" can move shoot "target", ordered from closest to furthest away from "self"
        deltas = self.__all_deltas if self._catapult_bonus else self.__fire_deltas
        fire_locs_around_enemy = Hex.possible_shots(target, deltas)
        sorted_fire_locs = sorted(fire_locs_around_enemy, key=lambda loc: Hex.manhattan_dist(self._coord, loc))
        return tuple(sorted_fire_locs)

    def fire_corridors(self) -> tuple:
        deltas_by_corridor = self.__catapult_corridor_deltas if self._catapult_bonus else self.__fire_corridor_deltas
        return tuple([
            tuple([
                Hex.coord_sum(self._coord, delta) for delta in corridor_deltas]
            ) for corridor_deltas in deltas_by_corridor])

    @property
    def speed(self) -> int:
        return self.__sp
