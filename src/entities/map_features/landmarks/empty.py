from src.entities.entity_enum import Entities
from src.entities.map_features.feature import Feature
from src.parameters import EMPTY_COLOR


class Empty(Feature):
    def __init__(self, coord: tuple):
        super().__init__(Entities.EMPTY, coord, EMPTY_COLOR)
