from threading import Semaphore

from pygame.event import Event

from src.entities.entity_enum import Entities
from src.game_map.hex import Hex
from src.parameters import DISABLE_ANIMATIONS_GLOBAL
from src.players.types.remote_player import RemotePlayer
from src.remote.server_enum import Action


class ArchivedPlayer(RemotePlayer):
    def __init__(self, turn_played_sem: Semaphore, current_player: list[int], current_turn: list[int],
                 over: Event, game_exited: Event,
                 name: str | None = None, password: str | None = None,
                 is_observer: bool | None = None):
        super().__init__(turn_played_sem=turn_played_sem,
                         current_player=current_player, current_turn=current_turn,
                         over=over, game_exited=game_exited,
                         name=name, password=password,
                         is_observer=is_observer)

    def _place_actions(self) -> None:
        # force the turn end first to make sure the game actions are correct
        if self._current_player[0] == self.idx:
            if not self._game_client.force_turn():
                self._map.update_game_state(self._game_client.get_previous_game_state())

        game_actions: dict = self._game_client.get_game_actions()
        action_dict = {}

        for game_action in game_actions["actions"]:
            action: Action = game_action["action_type"]
            data: dict = game_action["data"]
            vehicle_id: int = int(data["vehicle_id"])
            action_dict[vehicle_id] = data, action

        for tank in self._tanks:
            if tank.tank_id not in action_dict:
                continue

            data = action_dict[tank.tank_id][0]
            action = action_dict[tank.tank_id][1]
            target: tuple = Hex.unpack_coords(data["target"])

            if action == Action.SHOOT:
                if tank.type == Entities.TANK_DESTROYER:
                    fire_corridors: tuple[list[tuple]] = tank.fire_corridors()
                    for fire_corridor in fire_corridors:
                        if target == fire_corridor[0]:
                            self._map.td_shoot(tank, fire_corridor)
                            break
                else:
                    self._map.local_shoot_tuple(tank, target)
            else:
                self._map.local_move(tank, target)

        DISABLE_ANIMATIONS_GLOBAL[0] = False
