from typing import List, Union, Callable

from pygame import Surface

from ..entity.map_features.base import Base
from ..entity.map_features.empty import Empty
from ..entity.map_features.obstacle import Obstacle
from ..entity.tanks.tank import Tank
from ..entity.tanks.tank_factory import TankFactory
from . import _a_star
from .hex import Hex
from ..server_data.data_io import *


class Map:
    def __init__(self, active_players: dict):

        self.__players: dict = Map.__add_players(active_players)
        self.__tanks: dict[int, Tank] = {}

        self.__map: dict = {}
        self.__map_size: int = 0
        self.__base_coords: tuple = ()
        self.__base_adjacent_coords: tuple = ()
        self.__spawn_coords: tuple = ()
        self.__make_map(active_players)
        self.__destroyed: List[Tank] = []

        self.__path_finding_algorithm: Callable = _a_star.a_star

    """     MAP MAKING      """

    def __make_map(self, players: dict) -> None:
        client_map = load_server_map()
        game_state = load_game_state()

        self.__map_size = client_map['size']
        # Make empty map
        rings = [Hex.make_ring(ring_num) for ring_num in range(self.__map_size)]
        self.__map = {coord: {'feature': Empty(coord), 'tank': None} for ring in rings for coord in ring}

        player_idxs = {player_dict['idx']: i for i, player_dict in enumerate(game_state['players'])}

        # put tanks in tanks & map & put spawns in map
        for vehicle_id, vehicle_info in game_state["vehicles"].items():
            player = players[player_idxs[vehicle_info['player_id']]]
            tank, spawn = TankFactory.create_tank_and_spawn(int(vehicle_id), vehicle_info, player.get_index())
            tank_coord = tank.get_coord()
            self.__map[tank_coord]['tank'] = tank
            self.__map[tank.get_spawn_coord()]['feature'] = spawn
            self.__tanks[int(vehicle_id)] = tank
            player.add_tank(tank)

        # Put entities in map
        for entity, info in client_map["content"].items():
            if entity == "base":
                self.__make_bases(info)
            elif entity == 'obstacle':
                self.__make_obstacles(info)
            else:
                print(f"Support for {entity} needed")

    @staticmethod
    def __add_players(active_players: dict) -> dict:
        players = {}
        for player_id, player in active_players.items():
            players[player.get_index()] = player
        return players

    def __make_bases(self, coords: dict) -> None:
        self.__base_coords = tuple([tuple(coord.values()) for coord in coords])
        for coord in self.__base_coords:
            self.__map[coord]['feature'] = Base(coord)
        self.__make_base_adjacents()

    def __make_base_adjacents(self):
        adjacent_deltas = Hex.make_ring(1)
        self.__base_adjacent_coords = list({Hex.coord_sum(delta, base_coord) for base_coord in self.__base_coords
                                            for delta in adjacent_deltas} - set(self.__base_coords))

    def __make_obstacles(self, obstacles: []) -> None:
        for d in obstacles:
            coord = (d['x'], d['y'], d['z'])
            self.__map[coord]['feature'] = Obstacle(coord)

    """     DRAWING     """

    def draw(self, screen: Surface):
        self.__map_drawer.draw(screen)


    """     MOVE & FIRE CONTROL        """

    def local_move(self, tank: Tank, new_coord: tuple) -> None:
        self.__map[new_coord]['tank'] = tank  # New pos now has tank
        self.__map[tank.get_coord()]['tank'] = None  # Old pos is now empty
        tank.set_coord(new_coord)  # tank has new position

    def local_shoot(self, tank: Tank, target: Tank) -> None:
        destroyed = target.register_hit_return_destroyed()
        if destroyed:
            # update player damage points
            self.__players[tank.get_player_index()].register_destroyed_vehicle(target)

            # add to destroyed tanks
            self.__destroyed.append(target)

        self.__players[tank.get_player_index()].register_shot(target.get_player_index())

    def local_shoot_tuple(self, tank: Tank, coord: tuple):
        entities = self.__map.get(coord)
        if entities and not isinstance(entities['feature'], Obstacle):
            enemy = self.__map[coord]['tank']
            if self.is_enemy(tank, enemy):
                self.local_shoot(tank, enemy)

    def td_shoot(self, td: Tank, target: tuple) -> None:
        danger_zone = Hex.danger_zone(td.get_coord(), target)
        for coord in danger_zone:
            entities = self.__map.get(coord)
            if entities and not isinstance(entities['feature'], Obstacle):
                target_tank = self.__map[coord]['tank']
                # Target tank can be an ally or an enemy
                if target_tank:
                    self.local_shoot(td, target_tank)
            else:
                break

    def is_neutral(self, player_tank: Tank, enemy_tank: Tank) -> bool:
        # Neutrality rule logic implemented here, return True if neutral, False if not neutral
        player_index, enemy_index = player_tank.get_player_index(), enemy_tank.get_player_index()
        other_index = next(iter({0, 1, 2} - {player_index, enemy_index}))
        other_player, enemy_player = self.__players[other_index], self.__players[enemy_index]
        return not enemy_player.has_shot(player_index) and other_player.has_shot(enemy_index)

    def is_enemy(self, friend: Tank, enemy: Tank) -> bool:
        return enemy and not (friend.get_player_index() == enemy.get_player_index() or
                              self.is_neutral(friend, enemy) or enemy.is_destroyed())

    """     NAVIGATION    """

    def tanks_in_range(self, tank: Tank) -> List[Tank]:
        return [tank for coord in tank.coords_in_range() if
                (tank := self.__map.get(coord, {}).get('tank')) is not None and not tank.is_destroyed()]

    def enemies_in_range(self, tank: Tank) -> List[Tank]:
        return [enemy for enemy in self.tanks_in_range(tank) if self.is_enemy(tank, enemy)]

    def closest_free_bases(self, to: tuple) -> Union[List[tuple], None]:
        free_base_coords = tuple(c for c in self.__base_coords if self.__map[c]['tank'] is None or c == to)
        if free_base_coords:
            return sorted(free_base_coords, key=lambda coord: Hex.manhattan_dist(to, coord))

    def closest_free_base_adjacents(self, to: tuple) -> Union[List[tuple], None]:
        free_base_adjacents = [c for c in self.__base_adjacent_coords if self.__map[c]['tank'] is None or c == to]
        if free_base_adjacents:
            return sorted(free_base_adjacents, key=lambda coord: Hex.manhattan_dist(to, coord))

    def closest_enemies(self, tank: Tank) -> List[Tank]:
        # Returns a sorted list by distance of enemy tanks
        tank_idx, tank_coord = tank.get_player_index(), tank.get_coord()
        enemies = [self.__players[player] for player in self.__players if player != tank_idx]
        return sorted((enemy_tank for enemy in enemies for enemy_tank in enemy.get_tanks()),
                      key=lambda enemy_tank: Hex.manhattan_dist(enemy_tank.get_coord(), tank_coord))

    def next_best_available_hex_in_path_to(self, tank: Tank, finish: tuple) -> Union[tuple, None]:
        return self.__path_finding_algorithm(self.__map, tank, finish)

    """     GETTERS     """

    def get_map_size(self) -> int:
        return self.__map_size

    def get_players(self) -> dict:
        return self.__players

    def get_map(self) -> dict:
        return self.__map

    def get_tank_color(self, tank_id: int):
        return self.__tanks[tank_id].get_color()