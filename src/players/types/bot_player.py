import time
from threading import Semaphore, Event

from mab.data.data_io import DataIO
from src.entities.entity_enum import Entities
from src.entities.tanks.tank import Tank
from src.parameters import GAME_SPEED
from src.players.player import Player


class BotPlayer(Player):
    __actions = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    __tank_names_can_repair = {
        'spg': False, 'light_tank': False, 'heavy_tank': True, 'medium_tank': True, 'at_spg': True
    }
    __short_by_longs = {
        's': 'spg', 'l': 'light_tank', 'h': 'heavy_tank', 'm': 'medium_tank', 'a': 'at_spg'
    }

    def __init__(self, turn_played_sem: Semaphore, current_player: list[int], current_turn: list[int],
                 over: Event, game_exited: Event,
                 name: str | None = None, password: str | None = None,
                 is_observer: bool | None = None):

        super().__init__(turn_played_sem=turn_played_sem,
                         current_player=current_player, current_turn=current_turn,
                         over=over, game_exited=game_exited,
                         name=name, password=password,
                         is_observer=is_observer)

        self.__actions: dict[int, dict[str, list[str]]] | None = None
        self.__order = None

    def __format_actions(self, actions: dict[int, str]) -> dict[int, dict[str, list[str]]]:
        formatted_actions = {i: {name: [] for name in self.__tank_names_can_repair} for i in range(len(actions))}

        for player_index, tank_action_combo in actions.items():
            current_name = None
            for letter in tank_action_combo:
                tank_name = self.__short_by_longs.get(letter)
                if tank_name:
                    current_name = tank_name
                elif current_name:
                    formatted_actions[int(player_index)][current_name].append(letter)

        return formatted_actions

    def set_actions(self, action_file: str):
        actions: dict[int, str] = DataIO.load_best_actions(action_file)
        self.__actions: dict[int, dict[str, list[str]]] = self.__format_actions(actions)

    def register_round(self) -> None:
        # reset round actions
        super().register_round()

    def _make_turn_plays(self) -> None:
        try:
            # play your move if you are the current player
            if self._current_player[0] == self.idx:
                delay = 1.0 - GAME_SPEED[0]
                if delay > 0:
                    time.sleep(delay)  # comment/uncomment this for a turn delay effect
                self.__place_actions()
        finally:
            # end your turn
            self._game_client.force_turn()

    def _logout(self) -> None:
        # manage your own connection
        self._game_client.logout()
        self._game_client.disconnect()

    def __place_actions(self) -> None:
        if self._current_turn[0] < self._num_players:
            self._map.set_order_by_idx(self._current_turn[0], self.idx)
            self.__order = self._current_turn[0]

        # Types: spg, light_tank, heavy_tank, medium_tank, at_spg
        if self.__actions is not None:
            this_bots_actions = self.__actions.get(self.__order)
        else:
            this_bots_actions = None

        if this_bots_actions is not None:
            for tank in self._tanks:
                this_rounds_action = this_bots_actions[tank.type][self._current_turn[0] // self._num_players]
                self.__do(this_rounds_action, tank)
        else:
            # Default model just in case
            for tank in self._tanks:
                if tank.type == 'spg':
                    self.__do('E', tank)
                elif tank.type == 'light_tank':
                    self.__do('D', tank)
                elif tank.type == 'heavy_tank':
                    self.__do('D', tank)
                elif tank.type == 'medium_tank':
                    self.__do('A', tank)
                elif tank.type == 'at_spg':
                    self.__do('D', tank)

    def __do(self, action: str, tank: Tank) -> None:
        # ML actions
        if action == 'A':
            base_action = 'move and camp in base'
            self.__repair_else_base(base_action, tank)
        elif action == 'B':
            base_action = 'move and camp close to base'
            self.__repair_else_base(base_action, tank)
        elif action == 'C':
            base_action = 'shoot else move close to enemy'
            self.__repair_else_base(base_action, tank)
        elif action == 'D':
            base_action = 'shoot else move in base'
            self.__repair_else_base(base_action, tank)
        elif action == 'E':
            base_action = 'shoot else move close to base'
            self.__repair_else_base(base_action, tank)
        elif action == 'F':
            base_action = 'shoot else move close to enemy'
            self.__catapult_else(tank, base_action)
        elif action == 'G':
            base_action = 'shoot else move close to base'
            self.__catapult_else(tank, base_action)

        # Base actions
        elif action == 'move and camp in base':
            # Move into the closest free base and from then on shoot enemies in range without moving
            self.__move_and_camp(tank, 'in base')
        elif action == 'move and camp close to base':
            # Move into the closest free hex adjacent to the base and shoot enemies in range
            self.__move_and_camp(tank, 'close to base')
        elif action == 'shoot else move close to enemy':
            # Shoot enemies in range, else move in range
            self.__shoot_else_move(tank, 'close enemy')
        elif action == 'shoot else move in base':
            # If there are enemies in range shoot them, else, move towards the closest free base
            self.__shoot_else_move(tank, 'in base')
        elif action == 'shoot else move close to base':
            # If there are enemies in range shoot them, else, move towards the closest free hex adjacent to the base
            self.__shoot_else_move(tank, 'close to base')

    def __repair_else_base(self, base_action: str, tank: Tank) -> None:
        if self.__tank_names_can_repair[tank.type]:
            self.__repair_if_low_hp_else(tank, base_action)
        else:
            self.__do(base_action, tank)

    def __repair_if_low_hp_else(self, tank: Tank, action: str) -> None:
        if tank.health_points == 1 and self.__tank_names_can_repair[tank.type] \
                and self.__move_return_has_moved('repair', tank):
            return
        self.__do(action, tank)

    def __catapult_else(self, tank: Tank, action: str) -> None:
        enemies_in_range = self._map.enemies_in_range(tank)
        if enemies_in_range:
            self.__camp(tank, enemies_in_range)
        else:
            if tank.catapult_bonus:
                self.__do(action, tank)
            elif not self.__move_return_has_moved('catapult', tank):
                if self._map.is_catapult_and_usable(tank.coord):
                    return
                cats = self._map.two_closest_catapults_if_usable(tank)
                if len(cats) == 0:
                    self.__do(action, tank)

    def __move_return_has_moved(self, where: str, who: Tank) -> bool:
        who_coord, go_to = who.coord, None
        if where == 'close to base':
            go_to = self._map.closest_free_base_adjacents(who_coord)
        elif where == 'in base':
            go_to = self._map.closest_free_bases(who_coord)
        elif where == 'close enemy':
            if self._map.closest_enemies(who):
                go_to = who.shot_moves(self._map.closest_enemies(who)[0].coord)
        elif where == 'repair':
            go_to = self._map.closest_usable_repair(who)
        elif where == 'catapult':
            go_to = self._map.two_closest_catapults_if_usable(who)

        if go_to:  # TODO: Find out why 'go_to' is None in edge cases
            for coord in go_to:
                if who_coord == coord:
                    return False
                if self.__move_to_if_possible(who, coord):
                    return True
        return False

    def __move_and_camp(self, tank: Tank, where: str) -> None:
        if not self.__move_return_has_moved(where, tank):
            enemies_in_range = self._map.enemies_in_range(tank)
            if enemies_in_range:
                self.__camp(tank, enemies_in_range)

    def __shoot_else_move(self, tank: Tank, where: str) -> None:
        enemies_in_range = self._map.enemies_in_range(tank)
        if not enemies_in_range:
            self.__move_return_has_moved(where, tank)
        else:
            self.__camp(tank, enemies_in_range)

    def __camp(self, tank: Tank, enemies_in_range: list[Tank]) -> None:
        if tank.type != Entities.TANK_DESTROYER:
            self.__update_maps_with_tank_shot(tank, self.__best_shooting_target(enemies_in_range))
        else:
            self.__td_camp(tank, self._map.enemies_in_range(tank))

    def __td_camp(self, td: Tank, enemy_tanks: list[Tank]) -> bool:
        # Shoot the fire corridor with the largest damage potential, if no damage potential in any get the
        # corridor with the most enemies, if no enemies return False, is has shot return True
        td_fire_corridors = td.fire_corridors()
        tanks_by_corridor = [
            [tank for tank in enemy_tanks if tank.coord in corridor]
            for corridor in td_fire_corridors]

        most_damage_index, most_damage_potential = max(
            ((i, sum(tank.max_health_points for tank in corridor if tank.health_points == 1))
             for i, corridor in enumerate(tanks_by_corridor)), key=lambda x: x[1], default=(None, 0))

        if most_damage_index:
            self.__update_maps_with_td_shot(td, td_fire_corridors[most_damage_index])
            return True

        most_enemies_index, most_enemies = max(((i, len(corridor)) for i, corridor in enumerate(tanks_by_corridor)),
                                               key=lambda x: x[1], default=(None, 0))
        if most_enemies_index:
            self.__update_maps_with_td_shot(td, td_fire_corridors[most_enemies_index])
            return True

        return False

    def __move_to_if_possible(self, tank: Tank, where: tuple) -> bool:
        next_best = self._map.next_best_available_hex_in_path_to(tank, where)

        if next_best is not None:
            self.__update_maps_with_move(tank, next_best)
            return True
        return False

    def __update_maps_with_move(self, tank: Tank, action_coord: tuple) -> None:
        x, y, z = action_coord
        self._map.local_move(tank, action_coord)
        self._game_client.server_move({"vehicle_id": tank.tank_id, "target": {"x": x, "y": y, "z": z}})

    def __update_maps_with_tank_shot(self, tank: Tank, enemy: Tank) -> None:
        self._map.local_shoot(tank, enemy)
        x, y, z = enemy.coord
        self._game_client.server_shoot({"vehicle_id": tank.tank_id, "target": {"x": x, "y": y, "z": z}})

    def __update_maps_with_td_shot(self, tank: Tank, td_fire_corridor: list[tuple]) -> None:
        x, y, z = td_fire_corridor[0]
        self._map.td_shoot(tank, td_fire_corridor)
        self._game_client.server_shoot({"vehicle_id": tank.tank_id, "target": {"x": x, "y": y, "z": z}})

    @staticmethod
    def __best_shooting_target(enemies_in_range: list[Tank]) -> Tank:
        """Returns the tank with the lowest health points and the most max health points in enemies_in_range"""
        target: Tank | None = None
        for tank in enemies_in_range:
            if target is None or tank.health_points < target.health_points or \
                    (tank.health_points == target.health_points and target.max_health_points < tank.max_health_points):
                target = tank
        return target
