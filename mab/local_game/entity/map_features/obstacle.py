from .feature import Feature


class Obstacle(Feature):
    def __init__(self, coord: tuple):
        super().__init__('obstacle', coord)