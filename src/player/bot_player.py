from abc import ABC
from threading import Semaphore

from src.entity.tanks.tank import Tank
from src.player.player import Player


class BotPlayer(Player, ABC):
    def __init__(self, name: str, password: str, is_observer: bool,
                 turn_played_sem: Semaphore, current_player: list[1], player_index: int):
        super().__init__(name, password, is_observer, turn_played_sem, current_player, player_index)

    def __move(self, who: Tank, where: tuple):
        pass

    def __move_to_base(self, tank: Tank):
        closest_base_coord = self._map.get_closest_base_coord(tank)
        path = self._game_map.shortest_path(tank.get_coord(), closest_base_coord)
        if path is None:
            return
        speed = tank.get_speed()
        for i in range(speed, -1, -1):
            if len(path) >= i + 1:
                if self._map.get_tank_at((path[i])) is not None:
                    continue
                next_move = {"vehicle_id": tank.get_id(), "target": {"x": path[i][0], "y": path[i][1], "z": path[i][2]}}
                self._game_client.move(next_move)
                self._game_map.update({"actions": [{"action_type": 101, "data": next_move}]})
                break

        # print(path)

    def __shoot(self, who, target):
        pass

    def _play(self) -> None:
        for tank in self._tanks:
            break
        pass

    def _make_turn_plays(self) -> None:
        for tank in self._tanks:
            self.__move_to_base(tank)
        # free_base_coords = list(self._map.get_base_coords())
        #
        # for tank in self._tanks:
        #     if self._map.is_base(tank.get_coord()):
        #         continue
        #
        #     tank_coord = tank.get_coord()
        #     closest_base_coord, closest_base_dist = None, float('inf')
        #
        #     for coord in free_base_coords:
        #         dist = Hex.abs_dist(coord, tank_coord)
        #         if dist <= closest_base_dist:
        #             closest_base_dist = dist
        #             closest_base_coord = coord
        #
        #     if closest_base_coord is not None:
        #         free_base_coords.remove(closest_base_coord)
        #         path = self._game_map.shortest_path(tank_coord, closest_base_coord)
        #
        #         if len(path) >= 2 and not self._map.get_tank_at(path[1]):
        #             x, y, z = path[1]
        #         else:
        #             continue
        #
        #         next_move = {"vehicle_id": tank.get_id(), "target": {"x": x, "y": y, "z": z}}
        #
        #         self._game_client.move(next_move)
        #         self._game_map.update({"actions": [{"action_type": 101, "data": next_move}]})
