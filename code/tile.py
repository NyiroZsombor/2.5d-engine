import pygame as pg
import json
import preload

class Tile:
    texture_slices: dict[str, list[pg.Surface]] = {}

    def init() -> None:
        textures: list[str] = []
        with open("../textures.json") as file:
            textures = json.load(file)

        for name in textures:
            Tile.texture_slices[name] = preload.get_texture_slices(name)


    def __init__(self, name: str):
        self.name = name
        self.slice_num: int = len(Tile.texture_slices[self.name])


    def draw(self, surf: pg.Surface, slice_num: int,
    rect: tuple[int, int, int, int], tint: int) -> None:
        tinted: pg.Surface = self.texture_slices[self.name][slice_num].copy()
        tinted.fill(tint, special_flags=pg.BLEND_RGB_MULT)
        tinted = pg.transform.scale(tinted, rect[2:4])
        
        surf.blit(tinted, rect[0:2])