import queue
from threading import Semaphore

from src.game_client import GameClient
from src.players.player import Player
from src.players.player_factory import PlayerFactory, PlayerTypes
from src.players.types.bot_player import BotPlayer
from src.players.types.remote_player import RemotePlayer


class PlayerManager:
    """" Manages player connections and synchronization """

    def __init__(self, game):
        # game container
        self.__game = game
        self.__shadow_client = self.__game.shadow_client

        self.__num_players: int = 0
        self.__current_turn: list[int] = self.__game.current_turn

        self.__turn_played_sem: Semaphore = Semaphore(0)

        # Thread safe queue for connecting local players
        self.__player_queue: queue = queue.Queue()

    def login(self) -> None:
        self.__shadow_client.login(name=f"{self.__game.game_name}-Team-Segfault-Shadow",
                                   game_name=self.__game.game_name,
                                   num_turns=self.__game.num_turns,
                                   num_players=self.__game.max_players,
                                   is_observer=True,
                                   is_full=self.__game.is_full)

    def logout(self) -> None:
        # end by logging out of the shadow observer
        try:
            self.__shadow_client.logout()
        except ConnectionError:
            # ignore the double logout error
            pass

        self.__shadow_client.disconnect()

    def set_players_interrupted(self) -> None:
        # set interrupted status for all players
        for player in self.__game.active_players.values():
            player.interrupted = True

    def notify_all_players(self) -> None:
        # release all players using their private semaphores
        for player in self.__game.active_players.values():
            player.next_turn_sem.release()

    def handle_player_turns(self) -> None:
        self.notify_all_players()

        # if current player isn't a remote player, end the turn
        if (not isinstance(self.__game.current_player, RemotePlayer)
                and not self.__game.over.is_set()):
            self.__shadow_client.force_turn()

        # wait for everyone to finish their turns
        for _ in range(self.__num_players):
            self.__turn_played_sem.acquire()

    def start_players(self) -> None:
        # add players in order sorted by their idx
        ind: int = 0
        for idx, player in sorted(self.__game.active_players.items(), key=lambda x: x[0]):
            if not player.is_observer:
                # set the num players parameter and the player index
                player.num_players = self.__game.max_players
                player.set_color_index(ind)
                ind += 1

            # do not start remote observers - there is no need
            if not isinstance(player, RemotePlayer) or not player.is_observer:
                player.start()

    def add_remote_players(self, players: dict) -> None:
        for player in players:
            if player["idx"] not in self.__game.active_players:
                self.__add_remote_player(player)

    def add_local_player(self, name: str, password: str | None, is_observer: bool | None, is_backup: bool,
                         action_file: str) -> None:
        """
        Will connect the local bot player to the game if a player with the same id is not connected.
        """
        self.__num_players += 1

        player: Player
        player_type: PlayerTypes
        if is_observer:
            player_type = PlayerTypes.Observer
        elif is_backup:
            player_type = PlayerTypes.BackupBot
        else:
            player_type = PlayerTypes.Bot

        player = PlayerFactory.create_player(player_type=player_type,
                                             name=name,
                                             password=password,
                                             is_observer=is_observer,
                                             turn_played_sem=self.__turn_played_sem,
                                             current_player_idx=self.__game.current_player_idx,
                                             over=self.__game.over, game_exited=self.__game.game_exited,
                                             current_turn=self.__current_turn)

        if isinstance(player, BotPlayer):
            player.set_actions(action_file)

        self.__player_queue.put(player)

    def connect_queued_players(self):
        while not self.__player_queue.empty():
            player: Player = self.__player_queue.get()
            self.__connect_local_player(player)

    def __add_remote_player(self, user_info: dict) -> None:
        # Do not start remote observers later on, just keep their info as read-only data
        if not user_info["is_observer"]:
            self.__num_players += 1

        player: Player = PlayerFactory.create_player(player_type=PlayerTypes.Remote,
                                                     turn_played_sem=self.__turn_played_sem,
                                                     current_player_idx=self.__game.current_player_idx,
                                                     over=self.__game.over, game_exited=self.__game.game_exited)

        player.add_to_game(user_info, self.__shadow_client)

        self.__game.active_players[player.idx] = player

    def __connect_local_player(self, player: Player) -> None:
        game_client: GameClient = GameClient()
        user_info: dict = game_client.login(name=player.player_name, password=player.password,
                                            game_name=self.__game.game_name,
                                            num_turns=self.__game.num_turns,
                                            num_players=self.__game.max_players,
                                            is_observer=player.is_observer,
                                            is_full=self.__game.is_full)

        player.add_to_game(user_info, game_client)

        self.__game.active_players[player.idx] = player
