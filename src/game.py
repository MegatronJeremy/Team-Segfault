import time
from threading import Thread, Event

from src.game_client.game_client import GameClient
from src.game_client.types.archived_client import ArchivedGameClient
from src.game_client.types.remote_client import RemoteGameClient
from src.game_map.map import Map
from src.parameters import DEFAULT_ACTION_FILE, CURRENT_GAME_NAME, ARCHIVED_GAME_TURN, ARCHIVED_GAME_PAUSED
from src.players.player import Player
from src.players.player_manager import PlayerManager


class Game(Thread):
    def __init__(self, game_name: str | None = None, num_turns: int | None = None,
                 max_players: int = 1, is_full: bool = False, use_ml_actions: bool = True,
                 is_archived_game: bool = False, replay_file: str | None = None) -> None:
        super().__init__()

        self.game_map: Map | None = None
        self.__game_name: str | None = game_name
        CURRENT_GAME_NAME[0] = game_name

        # create an active event
        self.over: Event = Event()
        self.__game_exited: Event = Event()

        self.__num_turns: int | None = num_turns
        self.__max_players: int = max_players
        self.__is_full: bool = is_full
        self.__num_rounds: int | None = None
        self.__next_round: bool = False
        self.__next_turn: bool = False
        self.__game_finished: bool = False

        self.__round_winner_index: int | None = None
        self.__game_winner_index: int | None = None
        self.__game_is_draw: bool = False

        # The game was interrupted
        self.__interrupted = False

        self.__error: Exception | None = None

        self.__current_turn: list[int] = [-1]
        self.__current_round: int = 0
        self.__current_player: Player | None = None

        self.__is_archived_game = is_archived_game

        # Observer connection that is used for collecting data
        self.__shadow_client = ArchivedGameClient(replay_file) if is_archived_game \
            else RemoteGameClient(is_shadow_client=True)

        self.__active_players: dict[int, Player] = {}
        self.__player_wins: dict[int, int] = {}
        self.__current_player_idx: list[int] = [-1]

        self.__use_ml_actions = use_ml_actions

        self.__player_manager: PlayerManager = PlayerManager(self)

        # Login with the player manager to be able to access game info
        try:
            self.__player_manager.login()
        except (ConnectionError, TimeoutError) as err:
            self.__error = err
            self.over.set()

    def __str__(self) -> str:
        out: str = ""
        out += str.format(f'Game: {self.__game_name}, '
                          f'number of players: {self.__max_players}, '
                          f'number of turns: {self.__num_turns}.')

        for player in self.__active_players.values():
            out += "\n" + str(player)

        return out

    """     GETTERS     """

    @property
    def max_players(self) -> int:
        return self.__max_players

    @property
    def current_player_idx(self) -> list[int]:
        return self.__current_player_idx

    @property
    def game_name(self) -> str | None:
        return self.__game_name

    @property
    def num_turns(self) -> int | None:
        return self.__num_turns

    @property
    def active_players(self) -> dict[int, Player]:
        return self.__active_players

    @property
    def current_player(self) -> Player:
        return self.__current_player

    @property
    def error(self) -> Exception | None:
        return self.__error

    @property
    def game_is_draw(self) -> bool:
        return self.__game_is_draw

    @property
    def is_full(self) -> bool:
        return self.__is_full

    @property
    def num_rounds(self) -> int | None:
        return self.__num_rounds

    @property
    def current_round(self) -> int | None:
        return self.__current_round

    @property
    def current_turn(self) -> list[int] | None:
        return self.__current_turn

    @property
    def shadow_client(self) -> GameClient:
        return self.__shadow_client

    @property
    def player_wins(self) -> dict[int, int]:
        return self.__player_wins

    @property
    def game_exited(self) -> Event:
        return self.__game_exited

    @property
    def is_archived(self) -> bool:
        return self.__is_archived_game

    @property
    def player_wins_and_info(self) -> list[tuple[str | None, tuple, int]]:
        return [(self.__active_players[idx].player_name, self.__active_players[idx].color, self.__player_wins[idx])
                for idx in self.__active_players if idx in self.__player_wins]

    """     GAME LOGIC      """

    def run(self) -> None:
        try:
            self.__init_game_state()

            while not self.over.is_set():
                if self.__next_round:
                    # start next round if need be
                    self.__start_next_round()
                elif self.__next_turn:
                    # just start the next turn
                    self.__start_next_turn()

                if self.__game_finished:
                    if not (self.__is_archived_game and ARCHIVED_GAME_PAUSED[0]):
                        # regular state
                        time.sleep(1)
                        self.over.set()
                    else:
                        # enter paused state for archived game in last turn
                        while ARCHIVED_GAME_PAUSED[0] and ARCHIVED_GAME_TURN[0] == self.__current_turn[0]:
                            time.sleep(0.01)

                        # check if turn changed after exiting paused state
                        if ARCHIVED_GAME_TURN[0] != self.__current_turn[0]:
                            self.__game_finished = False

                # handshake with players
                self.__player_manager.handle_player_turns()

                # set next turn
                self.__next_turn = True

        except (ConnectionError, TimeoutError) as err:
            # an error happened
            self.over.set()
            self.__error = err

        finally:
            self.__end_game()

    def add_local_player(self, name: str, password: str | None = None, is_observer: bool | None = None,
                         is_backup: bool = False,
                         action_file: str = DEFAULT_ACTION_FILE) -> None:
        self.__player_manager.add_local_player(name, password, is_observer, is_backup, action_file)

    def get_winner_index(self) -> int | None:
        # wait for game end event
        self.over.wait()
        return self.__game_winner_index

    def __wait_for_full_lobby(self) -> dict | None:
        """ Return game state if the lobby is full, else None if the game was interrupted """
        game_state: dict = self.__shadow_client.get_game_state()

        # connect queued players
        self.__player_manager.connect_queued_players()

        # add initial remote players and observers
        self.__player_manager.add_remote_players(game_state["players"])
        self.__player_manager.add_remote_players(game_state["observers"])

        while not self.over.is_set() and game_state["num_players"] != len(game_state["players"]):
            # wait for all the players to join
            game_state = self.__shadow_client.get_game_state()

            # add new remote players and observers
            self.__player_manager.add_remote_players(game_state["players"])
            self.__player_manager.add_remote_players(game_state["observers"])

        if self.over.is_set():
            return None

        return game_state

    def __init_game_state(self) -> None:
        # Check if an error happened when connecting
        if self.over.is_set():
            return

        game_state: dict | None = self.__wait_for_full_lobby()

        if not game_state:
            # the game was interrupted
            return

        self.__num_turns = game_state["num_turns"]
        self.__max_players = game_state["num_players"]
        self.__num_rounds = game_state["num_rounds"]

        # start all player instances
        self.__player_manager.start_players()

        # set the player win counts
        self.__set_player_win_counts(game_state)

        # output the game info to console
        print(self)

        # start first round
        self.__start_next_round(game_state)

    def __start_next_round(self, game_state: dict = None) -> None:
        # start the next round
        self.__next_round = False

        if not game_state:
            game_state = self.__shadow_client.get_game_state()

        self.__current_round = game_state["current_round"]

        client_map: dict = self.__shadow_client.get_map()

        # register round start for every player
        for player in self.__active_players.values():
            player.register_round()

        # initialize the game map (now adds tanks to players & game_map too)
        self.game_map = Map(client_map, game_state, self.__active_players, self.num_turns, self.num_rounds,
                            self.__current_turn)

        # pass Map reference to players
        for player in self.__active_players.values():
            player.add_map(self.game_map)

        # start the first turn
        self.__start_next_turn(game_state)

    def __start_next_turn(self, game_state: dict = None) -> None:
        self.__next_turn = False

        # start the next turn
        if not game_state:
            game_state = self.__shadow_client.get_game_state()

        self.__current_turn[0] = game_state["current_turn"]
        self.__current_player_idx[0] = game_state["current_player_idx"]

        # print()
        if self.__current_player_idx[0] != 0:
            self.__current_player = self.__active_players[self.__current_player_idx[0]]

            # Reset current player attacks
            self.__current_player.register_turn()

            # print(f"Current turn: {self.__current_turn[0]}, "
            #       f"current player: {self.__current_player.player_name}")
        else:
            # print(f"Current turn: {self.__current_turn[0]}")
            self.__current_player = None

        if self.game_map:
            self.game_map.update_turn(game_state)

        if game_state["finished"]:
            self.__round_winner_index = game_state["winner"]

            # TODO add logging enable/disable macro
            # self.__print_round_winner()

            # set the new player win counts
            self.__set_player_win_counts(game_state)

            if game_state["current_round"] == self.__num_rounds:
                self.__print_player_wins()
                self.__determine_game_winner()
                self.__game_finished = True
            else:
                self.__next_round = True

    def __end_game(self) -> None:
        # Notify all players the game has ended
        self.__player_manager.notify_all_players()

        self.__interrupted = True
        if self.__error:
            print('Error:', self.__error)
        elif not self.__game_winner_index and not self.__game_is_draw:
            print("The game was interrupted")
        else:
            self.__interrupted = False

        # If interrupted set all player statuses to interrupted as well
        if self.__interrupted:
            self.__player_manager.set_players_interrupted()

        # Notify players the game exit status was set
        self.__game_exited.set()

        # If not interrupted then logout, the game is finished
        if not self.__interrupted:
            self.__player_manager.logout()

    def __print_round_winner(self) -> None:
        print()
        if not self.__round_winner_index:
            print('The round is a draw')
        else:
            round_winner = self.__active_players[self.__round_winner_index]
            print(f'The round winner is: {round_winner.player_name}.')

    def __determine_game_winner(self):
        win_sum: dict = {}
        max_wins: int = 0
        winner_idx: int = -1
        for idx, win_num in self.__player_wins.items():
            win_sum.setdefault(win_num, 0)
            win_sum[win_num] += 1
            if win_num > max_wins:
                max_wins = win_num
                winner_idx = idx

        print()
        if win_sum[max_wins] != 1:
            print('The game is a draw!')
            self.__game_is_draw = True
        else:
            self.__game_winner_index = winner_idx
            print(f'The winner is: {self.__active_players[self.__game_winner_index].player_name}')

    def __set_player_win_counts(self, game_state):
        for idx, wins in game_state["player_result_points"].items():
            self.__player_wins[int(idx)] = wins

    def __print_player_wins(self) -> None:
        print()
        for idx, win_num in self.__player_wins.items():
            print(f"{self.__active_players[idx]} win points: {win_num}")
