from src.entities.entity_enum import Entities
from src.entities.map_features.feature import Feature
from src.parameters import OBSTACLE_COLOR


class Obstacle(Feature):
    def __init__(self, coord: tuple):
        super().__init__(Entities.OBSTACLE, coord, OBSTACLE_COLOR)
