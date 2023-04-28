import random
from threading import Semaphore, Thread, Event
from typing import Dict

from client.game_client import GameClient
from gui.display_manager import DisplayManager
from map.map import Map
from player.player import Player
from player.player_factory import PlayerFactory, PlayerTypes
from player.remote_player import RemotePlayer


class Game(Thread):
    def __init__(self, game_name: str = None, num_turns: int = None,
                 max_players: int = 1, graphics: bool = True) -> None:
        super().__init__()

        self.game_map = None
        self.__game_name: str = game_name

        # create an active event
        self.over: Event = Event()

        self.lobby_players: int = 0
        self.__num_turns: int = num_turns
        self.__max_players: int = max_players
        self.__num_players: int = 0
        self.__winner = None
        self.__winner_index = None
        self.__started: bool = False

        self.__players_queue: [Player] = []
        self.__current_turn: [] = [-1]
        self.__current_player = None

        # Observer connection that is used for collecting data
        self.__shadow_client = GameClient()

        self.__active_players: dict[int, Player] = {}

        self.__turn_played_sem: Semaphore = Semaphore(0)
        self.__current_player_idx: list[1] = [-1]

        self.__graphics: bool = graphics

    def __str__(self):
        out: str = ""
        out += str.format(f'Game name: {self.__game_name}, '
                          f'number of players: {self.__max_players}, '
                          f'number of turns: {self.__num_turns}.')

        for player in self.__active_players.values():
            out += "\n" + str(player)

        return out

    def add_local_player(self, name: str, password: str = None, is_observer: bool = None) -> None:
        """
        Will connect the player if game has started.
        If the game is full, player will be connected as an observer.
        """
        if self.lobby_players >= self.__max_players:
            is_observer = True

        if not is_observer:
            self.lobby_players += 1

        self.__num_players += 1

        player: Player
        player_type: PlayerTypes
        if is_observer:
            player_type = PlayerTypes.Observer
        else:
            player_type = PlayerTypes.Bot

        player = PlayerFactory.create_player(player_type=player_type,
                                             name=name,
                                             password=password,
                                             is_observer=is_observer,
                                             turn_played_sem=self.__turn_played_sem,
                                             current_player_idx=self.__current_player_idx,
                                             player_index=self.lobby_players - 1,
                                             over=self.over)

        if self.__started:
            self.__connect_local_player(player)
        else:
            self.__players_queue.append(player)

    def __add_remote_player(self, user_info: dict) -> None:
        if not user_info["is_observer"]:
            self.lobby_players += 1

        self.__num_players += 1

        player: Player = PlayerFactory.create_player(player_type=PlayerTypes.Remote,
                                                     turn_played_sem=self.__turn_played_sem,
                                                     current_player_idx=self.__current_player_idx,
                                                     player_index=self.lobby_players - 1,
                                                     over=self.over)

        self.__connect_remote_player(player, user_info)

    def start_game(self) -> None:
        # Set the state to started
        self.__started = True

        # start the game loop
        self.start()

    def set_game_actions(self, game_actions: Dict[int, Dict[str, str]]):
        for player in self.__players_queue:
            player.set_turn_actions(game_actions[player.get_index()])

    def start_menu(self) -> None:
        try:
            # initialize and start the pygame display manager from the main thread
            DisplayManager(self).run()
        finally:
            # in case the main thread is interrupted
            self.over.set()

    def get_winner_index(self):
        # wait for game end event
        self.over.wait()
        return self.__winner_index

    def run(self) -> None:
        self.__init_game_state()

        while not self.over.is_set():
            # start the next turn
            self.__start_next_turn()

            # handshake with players
            self.__handle_players()

        self.__end_game()

    def __notify_all_players(self):
        # release all players using their private semaphores
        for player in self.__active_players.values():
            player.next_turn_sem.release()

    def __handle_players(self):
        self.__notify_all_players()

        # if current player isn't a remote player, end the turn
        if not isinstance(self.__current_player, RemotePlayer) and not self.over.is_set():
            self.__shadow_client.force_turn()

        # wait for everyone to finish their turns
        for _ in range(self.__num_players):
            self.__turn_played_sem.acquire()

    def __connect_local_player(self, player: Player) -> None:
        game_client: GameClient = GameClient()
        user_info: dict = game_client.login(player.name, player.password,
                                            self.__game_name, self.__num_turns,
                                            self.__max_players, player.is_observer)

        player.add_to_game(user_info, game_client)
        player.start()

        self.__active_players[player.idx] = player

    def __connect_remote_player(self, player: Player, user_info: dict) -> None:
        player.add_to_game(user_info, self.__shadow_client)
        player.start()

        self.__active_players[player.idx] = player

    def __wait_for_full_lobby(self) -> dict | None:
        """ Return game state if the lobby is full, else None if the game was interrupted """
        game_state: dict = self.__shadow_client.get_game_state()

        while not self.over.is_set() and game_state["num_players"] != len(game_state["players"]):
            # wait for all the players to join
            game_state = self.__shadow_client.get_game_state()

        if self.over.is_set():
            # the game was interrupted - return
            self.__notify_all_players()
            return None

        return game_state

    def __init_game_state(self) -> None:
        self.__shadow_client.login(name=f"{self.__game_name}-Team-Segfault-Shadow-{random.randint(0, 100000)}",
                                   game_name=self.__game_name,
                                   num_turns=self.__num_turns,
                                   num_players=self.__max_players,
                                   is_observer=True)

        # Add the queued local players to the game
        for player in self.__players_queue:
            self.__connect_local_player(player)

        game_state: dict = self.__wait_for_full_lobby()

        if not game_state:
            # the game was interrupted
            return

        client_map: dict = self.__shadow_client.get_map()

        # add all remote players
        for player in game_state["players"]:
            if player["idx"] not in self.__active_players and not player["is_observer"]:
                self.__add_remote_player(player)

        # initialize the game map (now adds tanks to players & game_map too)
        self.game_map = Map(client_map, game_state, self.__active_players, self.__current_turn)

        self.__num_turns = game_state["num_turns"]
        self.__max_players = game_state["num_players"]

        # pass Map reference to players
        for player in self.__active_players.values():
            player.add_map(self.game_map)

        # output the game info to console
        print(self)

    def __start_next_turn(self) -> None:

        # start the next turn
        game_state = self.__shadow_client.get_game_state()

        self.__current_turn[0] = game_state["current_turn"]
        self.__current_player_idx[0] = game_state["current_player_idx"]
        self.__current_player = self.__active_players[self.__current_player_idx[0]]

        # Reset current player attacks
        self.__current_player.register_turn()

        print(f"Current turn: {self.__current_turn[0]}, "
              f"current player: {self.__current_player.name}")

        self.game_map.update_turn(game_state)

        if game_state["winner"] or self.__current_turn[0] == self.__num_turns:
            self.__winner = game_state["winner"]
            self.over.set()

    def __end_game(self):
        if self.__winner:
            winner = self.__active_players[self.__winner]
            self.__winner_index = winner.get_index()
            print(f'The winner is: {winner.name}.')
        else:
            print('The game is a draw.')

        self.__logout()

    def __logout(self):
        # end by logging out of the shadow observer
        self.__shadow_client.logout()
        self.__shadow_client.disconnect()
