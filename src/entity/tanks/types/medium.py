from abc import ABC

from map.hex import Hex
from entity.tanks.tank import Tank


class MediumTank(Tank, ABC):
    __sp: int = 2  # Speed Points
    __dp: int = 2  # Destruction Points
    __fire_deltas: tuple = Hex.rings[1]  # Fires only in ring2
    __possible_shot_num: int = len(__fire_deltas)

    def __init__(self, tank_id: int, tank_info: dict, colour: str):
        super().__init__(tank_id, tank_info, colour)

    def get_possible_shots(self, position: tuple) -> tuple:
        x, y, z = position
        return tuple([(dx+x, dy+y, dz+z) for (dx, dy, dz) in MediumTank.__fire_deltas])

    def get_speed(self) -> int:
        return self.__sp


