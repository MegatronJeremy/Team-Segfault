from enum import Enum
from threading import Semaphore, Event

from player.bot_player import BotPlayer
from player.observer import Observer
from player.player import Player
from player.remote_player import RemotePlayer


class PlayerTypes(Enum):
    Remote = 1
    Bot = 2
    Observer = 3


class PlayerMaker:
    __CLASS_MAPPING = {
        PlayerTypes.Remote: RemotePlayer,
        PlayerTypes.Bot: BotPlayer,
        PlayerTypes.Observer: Observer
    }

    @staticmethod
    def create_player(player_type: PlayerTypes,
                      turn_played_sem: Semaphore,
                      current_player_idx: list[1],
                      active: Event,
                      player_index: int,
                      name: str = None,
                      password: str = None,
                      is_observer: bool = None) -> Player:
        player_class = PlayerMaker.__CLASS_MAPPING[player_type]
        return player_class(name=name,
                            password=password,
                            is_observer=is_observer,
                            turn_played_sem=turn_played_sem,
                            current_player=current_player_idx,
                            player_index=player_index,
                            active=active)
