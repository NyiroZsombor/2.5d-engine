import pygame as pg
from tile_map import TileMap

class KinematicEntity:

    def __init__(self, x: float, y: float, width: float,
    height: float, tile_map: TileMap) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.tile_map = tile_map

        self.speed: float = 0.6
        self.vel_x: float = 0
        self.vel_y: float = 0


    def move(self, collide: bool=True) -> bool:
        if not collide:
            self.x += self.vel_x
            self.y += self.vel_y
            return False
            
        next_x: float = self.x + self.vel_x
        next_y: float = self.y + self.vel_y

        tile_x: int = int(self.x / self.tile_map.tile_size)
        tile_y: int = int(self.y / self.tile_map.tile_size)
        next_tile_x: int = int(next_x / self.tile_map.tile_size)
        next_tile_y: int = int(next_y / self.tile_map.tile_size)

        move_x: bool = self.tile_map.get_tile(next_tile_x, tile_y) is None
        move_y: bool = self.tile_map.get_tile(tile_x, next_tile_y) is None

        if move_x and move_y:
            if self.tile_map.get_tile(tile_x, tile_y) is None:
                self.x += self.vel_x
                self.y += self.vel_y

            elif self.vel_x > self.vel_y: self.x += self.vel_x
            else: self.y += self.vel_y
        elif move_x: self.x += self.vel_x
        elif move_y: self.y += self.vel_y

        return not (move_x and move_y)


    def collide(self, other) -> bool:
        sx: float = self.x - self.width / 2
        sy: float = self.y - self.height / 2
        ox: float = other.x - other.width / 2
        oy: float = other.y - other.height / 2

        return (
            ((sx > ox and sx < other.x + other.width / 2) or
            (ox > sx and ox < self.x + self.width / 2)) and
            ((sy > oy and sy < other.y + other.height / 2) or
            (oy > sy and oy < self.y + self.height / 2))
        )


    def draw_rect(self, surf: pg.Surface) -> None:
        scale: tuple[float, float] = (
            surf.get_width() / 512,
            surf.get_height() / 512,
        )
        rect: tuple[int, int, int, int] = (
            int((self.x - self.width / 2) * scale[0]),
            int((self.y - self.height / 2) * scale[1]),
            int(self.width * scale[0]),
            int(self.height * scale[1]),
        )
        pg.draw.rect(surf, 0xFF0000, rect, 1)