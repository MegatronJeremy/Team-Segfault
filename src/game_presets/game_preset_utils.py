from src.parameters import DEFAULT_NUM_TURNS


def setup_num_turns(num_turns: int, num_players: int) -> int:
    if num_turns < 1:
        num_turns = DEFAULT_NUM_TURNS
    else:
        num_turns *= num_players
    return num_turns
