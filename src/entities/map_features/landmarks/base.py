from src.entities.entity_enum import Entities
from src.entities.map_features.feature import Feature
from src.parameters import BASE_COLOR


class Base(Feature):
    __rounds_to_cap = 1

    def __init__(self, coord: tuple):
        super().__init__(Entities.BASE, coord, BASE_COLOR)
