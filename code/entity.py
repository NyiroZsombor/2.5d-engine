import pygame as pg
import json
import preload
from player import Player
from ray import Ray
from tile_map import TileMap

class Entity:
    sprites: dict[str, pg.Surface] = {}

    def init() -> None:
        entities: list[str] = []
        with open("../sprites.json") as file:
            entities = json.load(file)

        for name in entities:
            Entity.sprites[name] = preload.get_sprites(name)


    def __init__(self, name: str, x: float,
    y: float, tile_map: TileMap) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.tile_map = tile_map


    def update(self, player: Player) -> None:
        self.edges: tuple[float, float, float, float] = (
            player.get_camera_edges(self.x, self.y)
        )
        self.plane_dist: float | None = (
            player.get_point_plane_dist(self.x, self.y, self.edges)
        )
        self.cam_pos: float | None = (
            player.get_point_screen_pos(self.x, self.y, self.edges)
        )
        self.inv_dist: float | None = self.calculate_inv_dist()
        self.height: float | None = None
        if not self.inv_dist is None:
            self.scale = Ray.calculate_wall_height(
                self.inv_dist, Ray.height_diff, Ray.min_height
            )


    def calculate_inv_dist(self) -> float | None:
        if self.plane_dist is None: return None

        norm_dist: float = self.plane_dist / (
            self.tile_map.tile_size * Ray.depth
        )
        return 1 - norm_dist


    def draw_2d(self, surf: pg.Surface) -> None:
        scale: tuple[float, float] = (
            surf.get_width() / 512,
            surf.get_height() / 512,
        )
        rx: int = 16 * scale[0]
        ry: int = 16 * scale[1]

        pg.draw.ellipse(surf, 0xFF0000, (
            int((self.x - rx // 2) * scale[0]),
            int((self.y - ry // 2) * scale[1]),
            rx, ry
        ))


    def draw_3d(self, surf: pg.Surface) -> None:
        if self.cam_pos is None or self.plane_dist is None: return
        if self.cam_pos > 1 or self.cam_pos < 0: return
        if self.inv_dist < 0: return

        sprite: pg.Surface = Entity.sprites[self.name]
        sprite = pg.transform.scale_by(sprite, self.scale)

        wall_height: float = Ray.calculate_wall_height(
            self.inv_dist, Ray.height_diff, Ray.min_height
        ) * surf.get_height()

        x: int = (
            int(surf.get_width() * self.cam_pos)
            - int(sprite.get_width() / 2)
        )
        y: int = int(
            surf.get_height() / 2 + wall_height / 2 - sprite.get_height()
        )

        tint: int = int(255 * self.inv_dist)
        tint = tint + (tint << 8) + (tint << 16)
        sprite.fill(tint, special_flags=pg.BLEND_RGB_MULT)

        surf.blit(sprite, (x, y))