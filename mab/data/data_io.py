import json
import os
from typing import Type


class DataIO:
    __script_path = os.path.dirname(__file__)

    __training_data_path = os.path.join(__script_path, "training_data")

    __client_map_path = os.path.join(__script_path, "server_data/client_map")
    __game_state_path = os.path.join(__script_path, "server_data/game_state")

    ResultsTable = Type[dict[int, dict[str, list[int]]]]

    """     FORMATTING      """

    @staticmethod
    def __format_game_state(game_state: dict) -> dict:
        idx_by_index: dict[int, int] = {}
        index: int = 0
        for player_dict in game_state['players']:
            idx = player_dict.get('idx')
            if idx not in idx_by_index:
                idx_by_index[idx] = index
                index += 1
            player_dict[idx] = index

        for vehicle_dict in game_state['vehicles'].values():
            vehicle_dict['player_id'] = idx_by_index[vehicle_dict['player_id']]

        return game_state

    """     SAVING      """

    @staticmethod
    def save_session_data(results_table: ResultsTable, game_num: int, exploit_actions: dict[int, str], file_name: str):
        DataIO.__save_results_table(results_table, file_name)
        DataIO.__save_num_games(game_num, file_name)
        DataIO.__save_best_actions(exploit_actions, file_name)

    @staticmethod
    def __save(what, where: str) -> None:
        with open(where + '.json', 'w') as file:
            json.dump(what, file)

    @staticmethod
    def __save_best_actions(best_actions: dict[int, str], file_name: str) -> None:
        DataIO.__save(best_actions, DataIO.__training_data_path + file_name + '_best_actions')

    @staticmethod
    def __save_results_table(results_table: ResultsTable, file_name: str) -> None:
        DataIO.__save(results_table, DataIO.__training_data_path + file_name + '_results_table')

    @staticmethod
    def __save_num_games(num_games: int, file_name: str) -> None:
        DataIO.__save(num_games, DataIO.__training_data_path + file_name + '_num_games')

    @staticmethod
    def save_client_map(client_map: dict) -> None:
        DataIO.__save(client_map, DataIO.__client_map_path)

    @staticmethod
    def save_game_state(game_state: dict) -> None:
        game_state = DataIO.__format_game_state(game_state)
        DataIO.__save(game_state, DataIO.__game_state_path)

    """     LOADING     """

    @staticmethod
    def load_results_table(save_file: str) -> ResultsTable:
        return DataIO.__load(DataIO.__training_data_path + '\\' + save_file + '_results_table')

    @staticmethod
    def load_num_games(save_file: str) -> int:
        return DataIO.__load(DataIO.__training_data_path + '\\' + save_file + '_num_games')

    @staticmethod
    def load_best_actions(save_file: str) -> dict[int, str]:
        return DataIO.__load(DataIO.__training_data_path + '\\' + save_file + '_best_actions')

    @staticmethod
    def load_client_map() -> dict:
        return DataIO.__load(DataIO.__client_map_path)

    @staticmethod
    def load_game_state() -> dict:
        return DataIO.__load(DataIO.__game_state_path)

    @staticmethod
    def __load(from_where: str):
        with open(from_where + '.json', 'r') as file:
            what = json.load(file)
        return what
