from abc import ABC

from src.entities.map_features.bonuses.catapult import get_catapult_bonus_range
from src.entities.tanks.tank import Tank
from src.game_map.hex import Hex
from src.parameters import MT_IMAGE_PATH


class MediumTank(Tank, ABC):
    __sp: int = 2  # Speed Points
    __dp: int = 2  # Destruction Points
    __max_range: int = 2  # Manhattan max range
    __min_range: int = 2  # Manhattan min range
    __catapult_range: int = __max_range + get_catapult_bonus_range()  # Manhattan max range when in catapult hex

    __fire_deltas: tuple = Hex.fire_deltas(__min_range, __max_range)
    __catapult_deltas: tuple = Hex.fire_deltas(__max_range, __catapult_range)
    __all_deltas: tuple = __fire_deltas + __catapult_deltas

    def __init__(self, tank_id: int, tank_info: dict, colour: tuple, player_index: int):
        super().__init__(tank_id, tank_info, colour, player_index, MT_IMAGE_PATH)

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
        return ()

    @property
    def speed(self) -> int:
        return self.__sp
