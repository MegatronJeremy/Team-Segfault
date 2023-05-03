
from local_constants import HEX_RADIUS_X, HEX_RADIUS_Y, SCREEN_HEIGHT, SCREEN_WIDTH
from local_entities.local_map_features.local_bonuses.local_catapult import LocalCatapult
from local_entities.local_map_features.local_bonuses.local_hard_repair import LocalHardRepair
from local_entities.local_map_features.local_bonuses.local_light_repair import LocalLightRepair
from local_entities.local_map_features.local_feature_factory import LocalFeatureFactory
from local_entities.local_map_features.local_landmarks.local_base import LocalBase
from local_entities.local_map_features.local_landmarks.local_empty import LocalEmpty
from local_entities.local_map_features.local_landmarks.local_obstacle import LocalObstacle
from local_entities.local_tanks.local_tank import LocalTank
from local_entities.local_tanks.local_tank_factory import LocalTankFactory
from local_map import local_a_star
from local_map.local_hex import LocalHex


class LocalMap:
    __max_players_in_base = 2
    __rounds_to_cap = 1

    def __init__(self, client_map: dict, game_state: dict, active_players: dict, current_turn: list[int]):
        HEX_RADIUS_X[0] = SCREEN_WIDTH // ((client_map['size'] - 1) * 2 * 2)
        HEX_RADIUS_Y[0] = SCREEN_HEIGHT // ((client_map['size'] - 1) * 2 * 2)

        self.__players: dict = self.__add_players(active_players)
        self.__tanks: dict[int, LocalTank] = {}
        self.__destroyed: list[LocalTank] = []
        self.__base_coords: tuple = ()
        self.__base_adjacent_coords: tuple = ()
        self.__spawn_coords: tuple = ()
        self.__catapult_coords: tuple = ()
        self.__light_repair_coords: tuple = ()
        self.__hard_repair_coords: tuple = ()

        self.__map: dict = {}
        self.__map_size = client_map['size']
        self.__make_map(client_map, game_state, active_players)
        self.__current_round: int = 0
        self.__rounds_in_base_by_player_index = [0 for _ in range(3)]
        self.__player_indexes_who_capped: set = set()

        self.__path_finding_algorithm: callable = _a_star.local_a_star

    """     MAP MAKING      """

    def __make_map(self, client_map: dict, game_state: dict, active_players: dict) -> None:
        # Make empty map
        rings = [LocalHex.make_ring(ring_num) for ring_num in range(client_map["size"])]
        self.__map = {coord: {'feature': LocalEmpty(coord), 'tank': None} for ring in rings for coord in ring}

        # Uncomment to save new maps to run in the local version
        # save_server_map(client_map)
        # save_game_state(game_state)

        # Make features, put them in map
        feature_factory = LocalFeatureFactory(client_map["content"], self.__map)
        self.__base_coords = feature_factory.base_coords
        self.__base_adjacent_coords = feature_factory.base_adjacents
        self.__catapult_coords = feature_factory.catapult_coords
        self.__light_repair_coords = feature_factory.light_repair_coords
        self.__hard_repair_coords = feature_factory.hard_repair_coords

        # Make local_tanks & spawns, put them in map
        tank_factory = LocalTankFactory(game_state["vehicles"], active_players, self.__map, self.__catapult_coords)
        self.__tanks = tank_factory.tanks

        del feature_factory, tank_factory

    @staticmethod
    def __add_players(active_players: dict) -> dict:
        return {player.index: player for player in active_players.values() if not player.is_observer}

    """     DRAWING     """

    def draw(self, screen: Surface) -> None:
        self.__map_drawer.draw(screen)

    """     SYNCHRONIZE SERVER AND LOCAL MAPS        """

    def update_turn(self, game_state: dict) -> None:
        # Local update of the new turn
        self.__new_turn(game_state["current_turn"])

        # At the beginning of each turn move the local_tanks that have been destroyed in the previous turn to their spawn
        for vehicle_id, vehicle_info in game_state["vehicles"].items():
            server_coord = (vehicle_info["position"]["x"], vehicle_info["position"]["y"], vehicle_info["position"]["z"])
            server_hp, server_cp = vehicle_info['health'], vehicle_info["capture_points"]

            tank = self.__tanks[int(vehicle_id)]
            if server_coord != tank.coord:
                print('server_coord', server_coord, 'tank.coord', tank.coord)
            if server_hp != tank.health_points:
                print('server_hp', server_hp, 'tank.health_points', tank.health_points, 'tank.player_index', tank.player_index)
            if server_cp != tank.capture_points:
                print(tank.type, tank.player_index, 'server_cp', server_cp, 'tank.cp', tank.capture_points)

            self.local_move(tank, server_coord) if server_coord != tank.coord else None
            tank.health_points = server_hp if server_hp != tank.health_points else tank.health_points
            tank.capture_points = server_cp if server_cp != tank.capture_points else tank.capture_points

    def __respawn_destroyed_tanks(self) -> None:
        while self.__destroyed:
            tank = self.__destroyed.pop()
            self.local_move(tank, tank.spawn_coord)
            tank.respawn()

    def __can_capture_base(self) -> bool:
        player_indexes_in_base = set(tank.player_index for tank in self.__tanks.values()
                                     if isinstance(self.__map[tank.coord]['feature'], LocalBase)
                                     and not tank.is_destroyed)
        return len(player_indexes_in_base) <= self.__max_players_in_base

    def __update_repairs_and_catapult_bonus(self):
        for tank in self.__tanks.values():
            if not tank.is_destroyed:
                feature = self.__map[tank.coord]['feature']
                if isinstance(feature, LocalLightRepair) and tank.type in LocalLightRepair.can_be_used_by:
                    tank.repair()
                elif isinstance(feature, LocalHardRepair) and tank.type in LocalHardRepair.can_be_used_by:
                    tank.repair()
                elif isinstance(feature, LocalCatapult) and feature.is_usable('all'):
                    feature.was_used()
                    tank.catapult_bonus = True
                elif not isinstance(feature, LocalBase) or tank.is_destroyed:
                    tank.capture_points = 0

    def __is_new_round(self, turn: int) -> int:
        new_round = turn // 3
        if new_round != self.__current_round:
            self.__current_round = new_round
            return True
        return False

    def __update_capture_points(self):
        can_cap = self.__can_capture_base()
        for tank in self.__tanks.values():
            base = self.__map[tank.coord]['feature']
            if not tank.is_destroyed and isinstance(base, LocalBase):
                if can_cap:
                    tank.capture_points += 1

    def __new_turn(self, turn: int):
        if self.__is_new_round(turn):
            self.__update_capture_points()
        self.__update_repairs_and_catapult_bonus()
        self.__respawn_destroyed_tanks()

    """     MOVE & FIRE CONTROL        """

    def local_move(self, tank: LocalTank, new_coord: tuple) -> None:
        self.__map[new_coord]['tank'] = tank  # New pos now has tank
        self.__map[tank.coord]['tank'] = None  # Old pos is now empty
        tank.coord = new_coord  # tank has new position
        tank.has_moved = True

    def local_shoot(self, tank: LocalTank, target: LocalTank) -> None:
        destroyed = target.register_hit_return_destroyed()
        if destroyed:
            # update player damage points
            self.__players[tank.player_index].register_destroyed_vehicle(target)

            # add to destroyed local_tanks
            self.__destroyed.append(target)

        self.__players[tank.player_index].register_shot(target.player_index)

    def local_shoot_tuple(self, tank: LocalTank, coord: tuple) -> None:
        entities = self.__map.get(coord)
        if entities and not isinstance(entities['feature'], LocalObstacle):
            enemy = self.__map[coord]['tank']
            if self.is_enemy(tank, enemy):
                self.local_shoot(tank, enemy)

    def td_shoot(self, td: LocalTank, target: tuple) -> None:
        danger_zone = LocalHex.danger_zone(td.coord, target)
        for coord in danger_zone:
            entities = self.__map.get(coord)
            if entities and not isinstance(entities['feature'], LocalObstacle):
                target_tank = self.__map[coord]['tank']
                # Target tank can be an ally or an enemy
                if target_tank:
                    self.local_shoot(td, target_tank)
            else:
                break

    def is_neutral(self, player_tank: LocalTank, enemy_tank: LocalTank) -> bool:
        # Neutrality rule logic implemented here, return True if neutral, False if not neutral
        player_index, enemy_index = player_tank.player_index, enemy_tank.player_index
        other_index = next(iter({0, 1, 2} - {player_index, enemy_index}))
        other_player, enemy_player = self.__players[other_index], self.__players[enemy_index]
        return not enemy_player.has_shot(player_index) and other_player.has_shot(enemy_index)

    def is_enemy(self, friend: LocalTank, enemy: LocalTank) -> bool:
        return enemy and not (friend.player_index == enemy.player_index or
                              self.is_neutral(friend, enemy) or enemy.is_destroyed)

    def __is_usable(self, bonus_coord: tuple, tank_type: str) -> bool:
        coord_dict = self.__map[bonus_coord]
        bonus, tank = coord_dict['feature'], coord_dict['tank']
        return not tank and bonus.is_usable(tank_type)

    def is_catapult_and_usable(self, coord: tuple) -> bool:
        catapult = self.__map[coord]['feature']
        if isinstance(catapult, LocalCatapult) and catapult.is_usable('any'):
            return True
        return False

    """     NAVIGATION    """

    @staticmethod
    def __features_by_dist(tank: LocalTank, feature_coords: tuple[tuple[int, int, int], ...]) -> list[tuple[int, int, int]]:
        return sorted(feature_coords, key=lambda coord: LocalHex.manhattan_dist(coord, tank.coord))

    def closest_usable_repair(self, tank: LocalTank) -> list[tuple[int, int, int]] | None:
        feature_coords = self.__hard_repair_coords
        if tank.type == 'medium_tank':
            feature_coords = self.__light_repair_coords
        closest_repair = self.__features_by_dist(tank, feature_coords)[0]
        if self.__is_usable(closest_repair, tank.type):
            return [closest_repair]

    def two_closest_catapults_if_usable(self, tank: LocalTank) -> list[tuple[int, int, int]]:
        two_closest = [coord for coord in self.__features_by_dist(tank, self.__catapult_coords)][:2]
        return [coord for coord in two_closest if self.__is_usable(coord, tank.type)]

    def tanks_in_range(self, tank: LocalTank) -> list[LocalTank]:
        is_on_catapult = isinstance(self.__map[tank.coord]['feature'], LocalCatapult)
        return [
            tank for coord in tank.coords_in_range(is_on_catapult)
            if (tank := self.__map.get(coord, {}).get('tank')) is not None and not tank.is_destroyed
        ]

    def enemies_in_range(self, tank: LocalTank) -> list[LocalTank]:
        return [
            enemy for enemy in self.tanks_in_range(tank)
            if self.is_enemy(tank, enemy)
        ]

    def closest_free_bases(self, to: tuple) -> list[tuple] | None:
        free_base_coords = tuple(c for c in self.__base_coords if self.__map[c]['tank'] is None or c == to)
        if free_base_coords:
            return sorted(free_base_coords, key=lambda coord: LocalHex.manhattan_dist(to, coord))

    def closest_free_base_adjacents(self, to: tuple) -> list[tuple] | None:
        free_base_adjacents = [c for c in self.__base_adjacent_coords if self.__map[c]['tank'] is None or c == to]
        if free_base_adjacents:
            return sorted(free_base_adjacents, key=lambda coord: LocalHex.manhattan_dist(to, coord))

    def closest_enemies(self, tank: LocalTank) -> list[LocalTank]:
        # Returns a sorted list by distance of enemy local_tanks
        tank_idx, tank_coord = tank.player_index, tank.coord
        enemies = [self.__players[player] for player in self.__players if player != tank_idx]
        return sorted((enemy_tank for enemy in enemies for enemy_tank in enemy.tanks),
                      key=lambda enemy_tank: LocalHex.manhattan_dist(enemy_tank.coord, tank_coord))

    def next_best_available_hex_in_path_to(self, tank: LocalTank, finish: tuple) -> tuple | None:
        return self.__path_finding_algorithm(self.__map, tank, finish)
