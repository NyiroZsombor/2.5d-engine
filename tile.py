import pygame as pg
import preload

class Tile:
    texture_slices: dict[str, list[pg.Surface]] = {
        "block": preload.get_texture_slices("block"),
        "brick": preload.get_texture_slices("brick"),
    }

    def __init__(self, name: str):
        self.name = name
        self.slices: list[pg.Surface] = Tile.texture_slices[name]
        self.slice_num: int = len(self.slices)


    def draw(self, surf: pg.Surface, slice_num: int,
    rect: tuple[int, int, int, int], tint: int) -> None:
        tinted: pg.Surface = self.slices[slice_num].copy()
        tinted.fill(tint, special_flags=pg.BLEND_RGB_MULT)
        tinted = pg.transform.scale(tinted, rect[2:4])
        
        surf.blit(tinted, rect[0:2])