from src.parameters import DEFAULT_NUM_TURNS, DEFAULT_NUM_TURNS_ONE_PLAYER


def setup_num_turns(num_turns: int, num_players: int) -> int:
    if num_turns < 1:
        num_turns = DEFAULT_NUM_TURNS
    if num_turns == DEFAULT_NUM_TURNS:
        num_turns = DEFAULT_NUM_TURNS_ONE_PLAYER * num_players
    if num_turns % num_players != 0:
        num_turns = num_turns + (num_players - num_turns % num_players)
    return num_turns
