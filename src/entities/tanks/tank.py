from abc import abstractmethod, ABC

from src.entities.entity import Entity, Entities


class Tank(Entity, ABC):
    """ Abstract Tank class """
    __damage = 1
    __rounds_to_cap = 1

    def __init__(self, tank_id: int, tank_info: dict, color: tuple[int, int, int] | str,
                 player_idx: int, image_path: str):
        self.__tank_id = tank_id
        self.__health_points: int = tank_info["health"]
        self.__max_health_points: int = self.__health_points
        self.__capture_points: int = tank_info["capture_points"]
        self.__spawn_coord: tuple = (tank_info["spawn_position"]["x"],
                                     tank_info["spawn_position"]["y"],
                                     tank_info["spawn_position"]["z"])
        self.__tank_color = color
        self.player_idx: int = player_idx
        self.__destroyed: bool = False
        self.__used_repair: bool = False
        self._coord: tuple[int, int, int] = (tank_info["position"]["x"],
                                             tank_info["position"]["y"],
                                             tank_info["position"]["z"])

        self.__image_path: str = image_path
        self._catapult_bonus: bool = False

        super().__init__(Entities(tank_info["vehicle_type"]))

    def register_hit_return_destroyed(self) -> bool:
        self.__health_points -= Tank.__damage  # All tanks do 1 damage
        if self.__health_points < 1:
            self.__destroyed = True

        return self.__destroyed

    def respawn(self) -> None:
        self.__capture_points, self.__destroyed = 0, False
        self.repair()

    def repair(self) -> None:
        # If repair was used, it cannot be used again while on the same hex!
        if not self.__used_repair:
            self.__used_repair = True
            self.__health_points = self.__max_health_points

    """     GETTERS AND SETTERS     """

    @property
    def coord(self) -> tuple[int, int, int]:
        return self._coord

    @coord.setter
    def coord(self, new_coord: tuple) -> None:
        # Reset this flag when moving
        self.__used_repair = False
        self._coord = new_coord

    @property
    def player_id(self) -> int:
        return self.player_idx

    @property
    def tank_id(self) -> int:
        return self.__tank_id

    @property
    def color(self) -> str | tuple[int, int, int]:
        return self.__tank_color

    @property
    def health_points(self) -> int:
        return self.__health_points

    @health_points.setter
    def health_points(self, hp: int):
        self.__health_points = hp

    @property
    def max_health_points(self) -> int:
        return self.__max_health_points

    @property
    def is_destroyed(self) -> bool:
        return self.__destroyed

    @property
    def capture_points(self) -> int:
        return self.__capture_points

    @capture_points.setter
    def capture_points(self, capture_pts: int):
        self.__capture_points = capture_pts

    @property
    def spawn_coord(self) -> tuple:
        return self.__spawn_coord

    @property
    def image_path(self) -> str:
        return self.__image_path

    @property
    def catapult_bonus(self) -> bool:
        return self._catapult_bonus

    @catapult_bonus.setter
    def catapult_bonus(self, catapult_bonus: bool):
        self._catapult_bonus = catapult_bonus

    @property
    def used_repair(self) -> bool:
        return self.__used_repair

    @used_repair.setter
    def used_repair(self, used_repair: bool) -> None:
        self.__used_repair = used_repair

    """     ABSTRACTS       """

    @abstractmethod
    def shot_moves(self, target: tuple) -> tuple:
        pass  # sorted coords to where "self" can move to shoot "target"

    @property
    @abstractmethod
    def speed(self) -> int:
        pass

    @abstractmethod
    def coords_in_range(self) -> tuple:
        pass

    @abstractmethod
    def fire_corridors(self) -> tuple:
        pass
