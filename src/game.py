from threading import Thread, Event

from src.game_map.map import Map
from src.players.player import Player
from src.players.player_manager import PlayerManager
from src.remote.game_client import GameClient


class Game(Thread):
    def __init__(self, game_name: str | None = None, num_turns: int | None = None,
                 max_players: int = 1, is_full: bool = False, use_ml_actions: bool = True) -> None:
        super().__init__()

        self.game_map: Map | None = None
        self.__game_name: str | None = game_name

        # create an active event
        self.over: Event = Event()

        self.__num_turns: int | None = num_turns
        self.__max_players: int = max_players
        self.__is_full: bool = is_full
        self.__num_rounds: int | None = None
        self.__next_round: bool = True

        self.__winner: int | None = None
        self.__winner_index: int | None = None
        self.__game_is_draw: bool = False

        self.__error: Exception | None = None

        self.__current_turn: list[int] = [-1]
        self.__current_round: int = 0
        self.__current_player: Player | None = None

        # Observer connection that is used for collecting data
        self.__shadow_client = GameClient()

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

    """     GAME LOGIC      """

    def run(self) -> None:
        try:
            self.__init_game_state()

            while not self.over.is_set():
                # start next round if need be
                if self.__next_round:
                    self.__start_next_round()

                # start the next turn
                self.__start_next_turn()

                # handshake with players
                self.__player_manager.handle_player_turns()

        except (ConnectionError, TimeoutError) as err:
            # an error happened
            self.over.set()
            self.__error = err

        finally:
            self.__end_game()

    def add_local_player(self, name: str, password: str | None = None, is_observer: bool | None = None) -> None:
        self.__player_manager.add_local_player(name, password, is_observer)

    def get_winner_index(self) -> int | None:
        # wait for game end event
        self.over.wait()
        return self.__winner_index

    def __wait_for_full_lobby(self) -> dict | None:
        """ Return game state if the lobby is full, else None if the game was interrupted """
        game_state: dict = self.__shadow_client.get_game_state()

        # add initial remote players and observers
        self.__player_manager.add_remote_players(game_state["players"])
        self.__player_manager.add_remote_players(game_state["observers"])

        # connect queued players
        self.__player_manager.connect_queued_players()

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

        # add all remote players and observers
        self.__player_manager.add_remote_players(game_state["players"])

        # start all player instances
        self.__player_manager.start_players()

        # set the player win counts
        for idx, wins in game_state["player_result_points"].items():
            self.__player_wins[int(idx)] = wins

        self.__start_next_round()

        # output the game info to console
        print(self)

    def __start_next_round(self) -> None:
        # start the next round
        self.__next_round = False

        game_state: dict = self.__shadow_client.get_game_state()

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

    def __start_next_turn(self) -> None:
        # start the next turn
        game_state = self.__shadow_client.get_game_state()

        self.__current_turn[0] = game_state["current_turn"]
        self.__current_player_idx[0] = game_state["current_player_idx"]

        print()
        if self.__current_player_idx[0] != 0:
            self.__current_player = self.__active_players[self.__current_player_idx[0]]
            # Reset current player attacks
            self.__current_player.register_turn()
            print(f"Current turn: {self.__current_turn[0]}, "
                  f"current player: {self.__current_player.player_name}")
        else:
            print(f"Current turn: {self.__current_turn[0]}")
            self.__current_player = None

        if self.game_map:
            self.game_map.update_turn(game_state)

        if game_state["finished"]:
            self.__winner = game_state["winner"]
            if self.__winner is None:
                self.__game_is_draw = True
            else:
                self.__player_wins[self.__winner] += 1
            self.__print_round_winner()

            if game_state["current_round"] == self.__num_rounds:
                self.over.set()
            else:
                self.__next_round = True

    def __end_game(self) -> None:
        # Notify all players the game has ended
        self.__player_manager.notify_all_players()

        if self.__error:
            print(self.__error)
        elif not self.__winner and not self.__game_is_draw:
            print("The game was interrupted")
        else:
            self.__print_game_winner()

        self.__player_manager.logout()

    def __print_round_winner(self) -> None:
        print()
        if self.__game_is_draw:
            print('The round is a draw')
        else:
            winner = self.__active_players[self.__winner]
            self.__winner_index = winner.index
            print(f'The round winner is: {winner.player_name}.')

    def __print_game_winner(self) -> None:
        winner: Player | None = None

        min_wins: int = -1
        max_wins: int = 0

        print()
        for idx, win_num in self.__player_wins.items():
            if self.__active_players[idx].is_observer:
                continue

            print(f"{self.__active_players[idx]} wins: {win_num}")

            if max_wins < win_num:
                winner = self.__active_players[idx]
                max_wins = win_num

            if min_wins == -1:
                min_wins = win_num
            else:
                min_wins = min(min_wins, win_num)

        print()
        if len(self.__player_wins) > 1 and min_wins != max_wins:
            print(f"{winner} is the game winner!")
        else:
            print("The game is a draw!")

    @property
    def player_wins_and_info(self) -> list[tuple[str, str | tuple[int, int, int], int]]:
        return [(self.__active_players[idx].player_name, self.__active_players[idx].color, self.__player_wins[idx])
                for idx in self.__active_players if idx in self.__player_wins]
