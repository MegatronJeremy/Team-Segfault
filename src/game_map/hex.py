from math import sqrt

from src.parameters import SCREEN_HEIGHT, SCREEN_WIDTH, HEX_RADIUS_Y, HEX_RADIUS_X


class Hex:
    __sqrt3 = sqrt(3)
    __rings: list[tuple] = []
    moves = ((1, 0, -1), (0, 1, -1), (1, -1, 0), (-1, 0, 1), (0, -1, 1), (-1, 1, 0))

    @staticmethod
    def td_fire_corridor_deltas(max_range: int) -> tuple:
        # returns a 2d tuple where each sub-tuple are the coords in a straight line corridor of td shooting deltas
        return tuple([tuple([Hex.coord_mult(move, m) for m in range(1, max_range + 1)]) for move in Hex.moves])

    @staticmethod
    def possible_shots(tank_coord: tuple, fire_deltas: tuple) -> tuple:
        x, y, z = tank_coord
        return tuple([(dx + x, dy + y, dz + z) for (dx, dy, dz) in fire_deltas])

    @staticmethod
    def opposite_coord(origin: tuple, target: tuple) -> tuple:
        dir_vec = Hex.dir_vec(origin, target)
        rev_dir_vec = Hex.rev_dir_vec(dir_vec)
        return Hex.coord_sum(origin, rev_dir_vec)

    @staticmethod
    def dir_vec(origin: tuple, target: tuple) -> tuple:
        dist = Hex.manhattan_dist(origin, target)
        x1, y1, z1 = origin
        x2, y2, z2 = target
        dx = ((x2 - x1) // dist)
        dy = ((y2 - y1) // dist)
        dz = ((z2 - z1) // dist)
        return dx, dy, dz

    @staticmethod
    def rev_dir_vec(dir_vec: tuple) -> tuple:
        return tuple(-x for x in dir_vec)

    @staticmethod
    def fire_deltas(min_range: int, max_range: int) -> tuple:
        fire_deltas = []
        for i in range(min_range, max_range + 1):
            for coord in Hex.__rings[i]:
                fire_deltas.append(coord)
        return tuple(fire_deltas)

    @staticmethod
    def make_rings(max_range: int = 4) -> None:  # Change max_range if maximum range of any tank is > 4 hexes
        Hex.__rings = [Hex.make_ring(i) for i in range(0, max_range + 1)]

    @staticmethod
    def make_ring(ring_num: int) -> tuple[tuple[int, int, int], ...]:
        # Makes all the possible coordinates in a given ring around (0,0,0)
        ring_coords = []
        max_crd = ring_num
        min_crd = -ring_num
        required_abs_sum = ring_num * 2
        for i in range(min_crd, max_crd + 1):
            for j in range(max(min_crd, min_crd - i), min(max_crd, max_crd - i) + 1):
                k = -i - j
                if abs(i) + abs(j) + abs(k) == required_abs_sum:
                    ring_coords.append((i, j, k))
        return tuple(ring_coords)

    @staticmethod
    def manhattan_dist(coord1: tuple, coord2: tuple) -> int:
        x1, y1, z1 = coord1
        x2, y2, z2 = coord2
        return (abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)) // 2

    @staticmethod
    def coord_sum(coord1: tuple, coord2: tuple) -> tuple:
        return tuple(fst + snd for fst, snd in zip(coord1, coord2))

    @staticmethod
    def coord_mult(coord: tuple, m: int) -> tuple:
        return tuple(x * m for x in coord)

    @staticmethod
    def make_center(coord: tuple) -> tuple[int, int]:
        """Returns the center of a given hex in cartesian co-ordinates for current screen"""
        x, y, z = coord
        x, y = (1 * x - 0.5 * y - 0.5 * z), (Hex.__sqrt3 / 2 * y - Hex.__sqrt3 / 2 * z)
        return SCREEN_WIDTH // 2 + round(x * HEX_RADIUS_X[0]), SCREEN_HEIGHT // 2 - round(y * HEX_RADIUS_Y[0])

    @staticmethod
    def make_corners(coord: tuple) -> tuple:
        # Returns cartesian coordinates of the six corners for a given array of hex coordinates + the first one twice
        x, y, z = coord
        first = Hex.make_center((x, y, z - 1))
        return (
            first,
            Hex.make_center((x, y + 1, z)),
            Hex.make_center((x - 1, y, z)),
            Hex.make_center((x, y, z + 1)),
            Hex.make_center((x, y - 1, z)),
            Hex.make_center((x + 1, y, z)),
            first
        )

    @staticmethod
    def unpack_coords(coord: dict) -> tuple:
        x = coord["x"]
        y = coord["y"]
        z = coord["z"]
        return x, y, z


Hex.make_rings()
