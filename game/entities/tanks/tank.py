from abc import abstractmethod, ABC

from entities.entity import Entity, Entities


class Tank(Entity, ABC):
    """ Abstract Tank class """
    __damage = 1
    __rounds_to_cap = 1

    def __init__(self, tank_id: int, tank_info: dict, color: tuple[int, int, int] | str, player_index: int,
                 image_path: str, catapult_coords: tuple):
        self.__tank_id = tank_id
        self.__health_points: int = tank_info["health"]
        self.__max_health_points: int = self.__health_points
        self.__capture_points: int = tank_info["capture_points"]
        self.__spawn_coord: tuple = (tank_info["spawn_position"]["x"],
                                     tank_info["spawn_position"]["y"],
                                     tank_info["spawn_position"]["z"])
        self.__tank_color = color
        self.__player_index: int = player_index
        self.__destroyed: bool = False
        self._coord: tuple[int, int, int] = (tank_info["position"]["x"],
                                             tank_info["position"]["y"],
                                             tank_info["position"]["z"])

        self._catapult_coords: tuple = catapult_coords
        self.__image_path: str = image_path
        self.__num_rounds_in_base: int = 0

        super().__init__(Entities(tank_info["vehicle_type"]))

    def register_hit_return_destroyed(self) -> bool:
        self.__health_points -= Tank.__damage  # All tanks do 1 damage
        if self.__health_points < 1:
            self.__destroyed = True

        return self.__destroyed

    def respawn(self) -> None:
        self.__capture_points, self.__num_rounds_in_base, self.__destroyed = 0, 0, False
        self.repair()

    def repair(self) -> None:
        self.__health_points = self.__max_health_points

    def in_base(self, can_cap: bool) -> None:
        self.__num_rounds_in_base += 1
        if self.__num_rounds_in_base > self.__rounds_to_cap and can_cap:
            self.__capture_points += 1

    """     GETTERS AND SETTERS     """

    @property
    def coord(self) -> tuple[int, int, int]: return self._coord

    @coord.setter
    def coord(self, new_coord: tuple) -> None:
        self._coord = new_coord

    @property
    def player_index(self) -> int: return self.__player_index

    @property
    def tank_id(self) -> int: return self.__tank_id

    @property
    def color(self) -> str | tuple[int, int, int]: return self.__tank_color

    @property
    def health_points(self) -> int: return self.__health_points

    @health_points.setter
    def health_points(self, hp: int): self.__health_points = hp

    @property
    def max_health_points(self) -> int: return self.__max_health_points

    @property
    def is_destroyed(self) -> bool: return self.__destroyed

    @property
    def capture_points(self) -> int: return self.__capture_points

    @capture_points.setter
    def capture_points(self, capture_pts: int): self.__capture_points = capture_pts

    @property
    def spawn_coord(self) -> tuple: return self.__spawn_coord

    @property
    def image_path(self) -> str:
        return self.__image_path

    """     ABSTRACTS       """

    @abstractmethod
    def shot_moves(self, target: tuple) -> tuple: pass  # sorted coords to where "self" can move to shoot "target"

    @property
    @abstractmethod
    def speed(self) -> int: pass

    @abstractmethod
    def coords_in_range(self, is_on_catapult: bool) -> tuple: pass

    @abstractmethod
    def td_shooting_coord(self, target: tuple) -> tuple: pass

    @abstractmethod
    def fire_corridors(self) -> tuple: pass
