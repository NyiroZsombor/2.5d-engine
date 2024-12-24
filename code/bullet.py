import pygame as pg
import math
from tile_map import TileMap
from entity import Entity
from camera import Camera

class Bullet(Entity):

    def __init__(self, x: float, y: float,
    tile_map: TileMap, angle: float) -> None:
        super().__init__("bullet", x, y, tile_map)
        self.width = 12
        self.height = 12

        self.speed = 1.5
        self.angle = angle
        self.vel_x = math.cos(self.angle) * self.speed
        self.vel_y = math.sin(self.angle) * self.speed


    def update(self, cam: Camera) -> bool:
        collision: bool = self.move()
        self.calculate_3d(cam)

        return collision