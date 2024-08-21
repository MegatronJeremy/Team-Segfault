from pygame import Surface

from mab.data.data_io import DataIO
from src.entities.map_features.bonuses.catapult import Catapult
from src.entities.map_features.bonuses.hard_repair import HardRepair
from src.entities.map_features.bonuses.light_repair import LightRepair
from src.entities.map_features.feature_factory import FeatureFactory
from src.entities.map_features.landmarks.base import Base
from src.entities.map_features.landmarks.empty import Empty
from src.entities.map_features.landmarks.obstacle import Obstacle
from src.entities.tanks.tank import Tank
from src.entities.tanks.tank_factory import TankFactory
from src.game_map import _a_star
from src.game_map.hex import Hex
from src.gui.map_utils.map_drawer import MapDrawer
from src.parameters import HEX_RADIUS_X, HEX_RADIUS_Y, SCREEN_HEIGHT, SCREEN_WIDTH


class Map:
    __max_players_in_base = 2

    def __init__(self, client_map: dict, game_state: dict, active_players: dict, num_turns: int, num_rounds: int,
                 current_turn: list[int], graphics=True):

        HEX_RADIUS_X[0] = SCREEN_WIDTH // ((client_map['size'] - 1) * 2 * 2)
        HEX_RADIUS_Y[0] = SCREEN_HEIGHT // ((client_map['size'] - 1) * 2 * 2)

        self.__players: dict = self.__add_players(active_players)
        self.__num_players: int = len(self.__players)
        self.__player_order: int = 0
        self.__max_players_in_base = self.__num_players - 1

        self.__tanks: dict[int, Tank] = {}
        self.__destroyed: list[Tank] = []
        self.__base_coords: tuple = ()
        self.__base_adjacent_coords: tuple = ()
        self.__spawn_coords: tuple = ()
        self.__catapult_coords: tuple = ()
        self.__light_repair_coords: tuple = ()
        self.__hard_repair_coords: tuple = ()

        self.__map: dict = {}
        self.__map_size = client_map['size']
        self.__make_map(client_map, game_state, active_players)
        self.__path_finding_algorithm: callable = _a_star.a_star

        self.__current_turn: list[int] = current_turn
        self.__player_order_by_idx: dict = {}

        if graphics:
            self.__map_drawer: MapDrawer = MapDrawer(client_map["size"], self.__players, self.__map, current_turn,
                                                     num_turns, num_rounds)

        # self.__save(client_map, game_state)  # Uncomment to save to run locally (only needed when server data changes)

    """     MAP MAKING      """

    def __make_map(self, client_map: dict, game_state: dict, active_players: dict) -> None:
        # Make empty map
        rings = [Hex.make_ring(ring_num) for ring_num in range(client_map["size"])]
        self.__map = {coord: {'feature': Empty(coord), 'tank': None} for ring in rings for coord in ring}

        # Make features, put them in map
        feature_factory = FeatureFactory(client_map["content"], self.__map)
        self.__base_coords = feature_factory.base_coords
        self.__base_adjacent_coords = feature_factory.base_adjacents
        self.__catapult_coords = feature_factory.catapult_coords
        self.__light_repair_coords = feature_factory.light_repair_coords
        self.__hard_repair_coords = feature_factory.hard_repair_coords

        # Make tanks & spawns, put them in map
        tank_factory = TankFactory(game_state["vehicles"], active_players, self.__map, self.__catapult_coords)
        self.__tanks = tank_factory.tanks

        del feature_factory, tank_factory

    @staticmethod
    def __add_players(active_players: dict) -> dict:
        return {player.idx: player for player in active_players.values() if not player.is_observer}

    """     DRAWING     """

    def draw(self, screen: Surface, current_round: int) -> None:
        self.__map_drawer.draw(screen, current_round)

    """     SYNCHRONIZE SERVER AND LOCAL MAPS        """

    def update_turn(self, game_state: dict) -> None:
        # Local update of the new turn
        self.__new_turn()

        # At the beginning of each turn move the tanks that have been destroyed in the previous turn to their spawn
        for vehicle_id, vehicle_info in game_state["vehicles"].items():
            server_coord = (vehicle_info["position"]["x"], vehicle_info["position"]["y"], vehicle_info["position"]["z"])
            server_hp, server_cp = vehicle_info['health'], vehicle_info["capture_points"]

            tank = self.__tanks[int(vehicle_id)]

            # Ignore this for now
            # Used to test discrepancies between server and local data
            # if server_coord != tank.coord:
            #     print('server_coord', server_coord, 'tank.coord', tank.coord)
            # if server_hp != tank.health_points:
            #     print('server_hp', server_hp, 'tank.health_points', tank.health_points, 'tank.player_id'
            #           , tank.type, tank.player_id)
            # if server_cp != tank.capture_points:
            #     print(tank.type, tank.player_id, 'server_cp', server_cp, 'tank.cp', tank.capture_points)

            self.local_move(tank, server_coord) if server_coord != tank.coord else None

            # Server hp and cp will always be correct
            tank.health_points = server_hp
            tank.capture_points = server_cp

        for player_id, points in game_state["win_points"].items():
            player = self.__players[int(player_id)]

            # capture points and kill points
            server_cp, server_dp = points["capture"], points["kill"]

            # Server cp and dp will always be correct
            player.damage_points = server_dp
            player.capture_points = server_cp

    def __update_repairs_and_catapult_bonus(self):
        for tank in self.__tanks.values():
            feature = self.__map[tank.coord]['feature']

            if not tank.is_destroyed:
                if (isinstance(feature, LightRepair) or isinstance(feature, HardRepair)) \
                        and feature.is_usable(tank.type):
                    # the repair won't happen if the tank is stationary
                    tank.repair()

                if isinstance(feature, Catapult) and feature.is_usable() and not tank.catapult_bonus:
                    # the feature won't be used again if the tank has the bonus applied
                    feature.was_used()
                    tank.catapult_bonus = True

            if not isinstance(feature, Base) or tank.is_destroyed:
                tank.capture_points = 0

    def __can_capture_base(self) -> bool:
        player_ids_in_base = set(tank.player_id for tank in self.__tanks.values()
                                 if isinstance(self.__map[tank.coord]['feature'], Base)
                                 and not tank.is_destroyed)
        return len(player_ids_in_base) <= self.__max_players_in_base

    def __update_capture_points(self):
        pass
        # for coord in self.__base_coords:
        # tank = self.__map[coord]['tank']
        # if tank and not tank.is_destroyed:
        #     tank.capture_points += 1

    def __respawn_destroyed_tanks(self) -> None:
        while self.__destroyed:
            tank = self.__destroyed.pop()
            self.local_move(tank, tank.spawn_coord)
            tank.respawn()

    def __new_turn(self):
        self.__current_player_index = self.__current_turn[0] % self.__num_players
        if self.__current_player_index == 0 and self.__can_capture_base():
            self.__update_capture_points()
        self.__update_repairs_and_catapult_bonus()
        self.__respawn_destroyed_tanks()

    def set_order_by_idx(self, turn: int, idx: int) -> None:
        self.__player_order_by_idx[turn] = idx

    """     MOVE & FIRE CONTROL        """

    def local_move(self, tank: Tank, new_coord: tuple) -> None:
        self.__map[new_coord]['tank'] = tank  # New pos now has tank
        self.__map[tank.coord]['tank'] = None  # Old pos is now empty
        tank.coord = new_coord  # tank has new position

    def local_shoot(self, tank: Tank, target: Tank) -> None:
        destroyed = target.register_hit_return_destroyed()
        self.__map_drawer.add_shot(Hex.make_center(tank.coord), Hex.make_center(target.coord), tank.color)

        if destroyed:
            # update player damage points
            self.__players[tank.player_id].register_destroyed_vehicle(target)

            # add explosion
            self.__map_drawer.add_explosion(tank, target)

            # add to destroyed tanks
            self.__destroyed.append(target)
        else:
            self.__map_drawer.add_hitreg(self.__map[target.coord]['feature'].center, target.image_path)
        self.__players[tank.player_id].register_shot(target.player_id)

        tank.catapult_bonus = False  # If had catapult bonus remove

    def local_shoot_tuple(self, tank: Tank, coord: tuple) -> None:
        # Used to place remote player shots
        entities = self.__map.get(coord)
        if entities and not isinstance(entities['feature'], Obstacle):
            enemy = self.__map[coord]['tank']
            if self.is_enemy(tank, enemy):
                self.local_shoot(tank, enemy)

    def td_shoot(self, td: Tank, target_corridor: list[tuple]) -> None:
        for coord in target_corridor:
            entities = self.__map.get(coord)
            if entities and not isinstance(entities['feature'], Obstacle):
                target_tank = self.__map[coord]['tank']
                # Tank that violates neutrality rule or is an ally or is not a tank is skipped
                if self.is_enemy(td, target_tank):
                    self.local_shoot(td, target_tank)
            else:
                break

    def is_neutral(self, player_index: int, enemy_index: int) -> bool:
        # Neutrality rule logic implemented here, return True if neutral, False if not neutral
        player_indexes: set = {i for i in self.__players}

        viable_indexes: set = (player_indexes - {player_index, enemy_index})

        # Set is empty
        if not viable_indexes:
            return False

        other_index = next(iter(viable_indexes))
        other_player, enemy_player = self.__players[other_index], self.__players[enemy_index]
        return not enemy_player.has_shot(player_index) and other_player.has_shot(enemy_index)

    def is_enemy(self, friend: Tank, enemy: Tank) -> bool:
        return enemy and not (friend.player_id == enemy.player_id or
                              self.is_neutral(friend.player_id, enemy.player_id) or enemy.is_destroyed)

    def __is_usable(self, bonus_coord: tuple, by: Tank) -> bool:
        coord_dict = self.__map[bonus_coord]
        bonus, tank = coord_dict['feature'], coord_dict['tank']
        return bonus.is_usable(by.type) and (not tank or tank is by)

    def is_catapult_and_usable(self, coord: tuple) -> bool:
        catapult = self.__map[coord]['feature']
        if isinstance(catapult, Catapult) and catapult.is_usable():
            return True
        return False

    """     NAVIGATION    """

    @staticmethod
    def __features_by_dist(tank: Tank, feature_coords: tuple[tuple[int, int, int], ...]) -> list[tuple[int, int, int]]:
        return sorted(feature_coords, key=lambda coord: Hex.manhattan_dist(coord, tank.coord))

    def closest_usable_repair(self, tank: Tank) -> list[tuple[int, int, int]] | None:
        if tank.type in HardRepair.can_be_used_by:
            feature_coords = self.__hard_repair_coords
        elif tank.type in LightRepair.can_be_used_by:
            feature_coords = self.__light_repair_coords
        else:
            return None

        closest_repair = self.__features_by_dist(tank, feature_coords)[0]
        if self.__is_usable(closest_repair, tank):
            return [closest_repair]

    def two_closest_catapults_if_usable(self, tank: Tank) -> list[tuple[int, int, int]]:
        two_closest = [coord for coord in self.__features_by_dist(tank, self.__catapult_coords)][:2]
        return [coord for coord in two_closest if self.__is_usable(coord, tank)]

    def tanks_in_range(self, tank: Tank) -> list[Tank]:
        # Returns all tanks, enemies and friends in range of 'tank' taking into account if 'tank' has catapult bonus
        return [
            tank for coord in tank.coords_in_range()
            if (tank := self.__map.get(coord, {}).get('tank')) is not None and not tank.is_destroyed
        ]

    def enemies_in_range(self, tank: Tank) -> list[Tank]:
        return [
            enemy for enemy in self.tanks_in_range(tank)
            if self.is_enemy(tank, enemy)
        ]

    def closest_free_bases(self, to: tuple) -> list[tuple] | None:
        free_base_coords = tuple(c for c in self.__base_coords if self.__map[c]['tank'] is None or c == to)
        if free_base_coords:
            return sorted(free_base_coords, key=lambda coord: Hex.manhattan_dist(to, coord))

    def closest_free_base_adjacents(self, to: tuple) -> list[tuple] | None:
        free_base_adjacents = [c for c in self.__base_adjacent_coords if self.__map[c]['tank'] is None or c == to]
        if free_base_adjacents:
            return sorted(free_base_adjacents, key=lambda coord: Hex.manhattan_dist(to, coord))

    def closest_enemies(self, tank: Tank) -> list[Tank]:
        # Returns a sorted list by distance of enemy tanks
        friend_index, tank_coord = tank.player_id, tank.coord
        enemies = [self.__players[other_index] for other_index in self.__players if other_index != friend_index]
        return sorted((enemy_tank for enemy in enemies for enemy_tank in enemy.tanks),
                      key=lambda enemy_tank: Hex.manhattan_dist(enemy_tank.coord, tank_coord))

    def next_best_available_hex_in_path_to(self, tank: Tank, finish: tuple) -> tuple | None:
        return self.__path_finding_algorithm(self.__map, tank, finish)

    """     NO GRAPHICS METHODS     """

    def local_shoot_no_graphics(self, tank: Tank, target: Tank) -> None:
        destroyed = target.register_hit_return_destroyed()
        if destroyed:
            self.__players[tank.player_id].register_destroyed_vehicle(target)
            self.__destroyed.append(target)
        self.__players[tank.player_id].register_shot(target.player_id)

        tank.catapult_bonus = False

    def td_shoot_no_graphics(self, td: Tank, target_corridor: list[tuple]) -> None:
        for coord in target_corridor:
            entities = self.__map.get(coord)
            if entities and not isinstance(entities['feature'], Obstacle):
                target_tank = self.__map[coord]['tank']
                # Tank that violates neutrality rule or is an allay or no tank there is skipped
                if self.is_enemy(td, target_tank):
                    self.local_shoot_no_graphics(td, target_tank)
            else:
                break

    """     MAP INFO       """

    def base_is_being_captured(self, player_idx: int) -> bool:
        for player in self.__players.values():
            if player.idx != player_idx and player.capture_points > 3:
                return True

        return False

    def get_unsafe_hexes(self, player_idx: int) -> dict:
        # coordinate -> list of player ids who can attack that coordinate
        safe_hexes: dict[tuple[int, int, int], list[int]] = {}
        for tank in self.__tanks.values():
            enemy_id = tank.player_id
            if enemy_id != player_idx:
                for coord in tank.coords_in_range():
                    safe_hexes[coord] = [enemy_id] if coord not in safe_hexes else safe_hexes[coord] + [enemy_id]
        return safe_hexes

    """     RUNNING LOCALLY      """

    def register_new_turn(self) -> None:
        self.__new_turn()

    @staticmethod
    def __save(client_map: dict, game_state: dict) -> None:
        DataIO.save_client_map(client_map)
        DataIO.save_game_state(game_state)
