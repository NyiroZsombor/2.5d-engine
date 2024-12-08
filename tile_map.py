import pygame as pg
from tile import Tile

class TileMap:

    def __init__(self, map_size: tuple[int, int], tile_size: int):
        self.map_size = map_size
        self.tile_size = tile_size
        self.grid: list[Tile | None] = [
            None for _ in range(self.map_size[0] * self.map_size[1])
        ]


    def draw(self, surf: pg.Surface) -> None:
        self.draw_tiles(surf)
        # self.draw_grid(surf)


    def draw_grid(self, surf: pg.Surface) -> None:
        color: tuple[int, int, int] = (64, 64, 64)
        for i in range(self.map_size[0] + 1):
            y: int = i * self.tile_size
            start: tuple[int, int] = (0, y)
            end: tuple[int, int] = (surf.get_width(), y)

            pg.draw.line(surf, color, start, end)

        for i in range(self.map_size[1] + 1):
            x: int = i * self.tile_size
            start: tuple[int, int] = (x, 0)
            end: tuple[int, int] = (x, surf.get_height())

            pg.draw.line(surf, color, start, end)


    def draw_tiles(self, surf: pg.Surface) -> None:
        for idx in range(len(self.grid)):
            tile: Tile | None = self.grid[idx]

            if not tile is None:
                size: tuple[int, int] = (self.tile_size, self.tile_size)
                pos: tuple[int, int] = tuple(map(
                    lambda x: self.tile_size * x, self.get_pos(idx)
                ))

                color: int = 0xFFFFFF
                pg.draw.rect(surf, color, (pos, size))


    def get_idx(self, x: int | float, y: int | float) -> int:
        if type(x) == float: x = int(x / self.tile_size)
        if type(y) == float: y = int(y / self.tile_size)

        return y * self.map_size[0] + x


    def get_tile(self, x: int | float, y: int | float) -> Tile | None:
        if type(x) == float: x = int(x / self.tile_size)
        if type(y) == float: y = int(y / self.tile_size)

        return self.grid[self.get_idx(x, y)]
    

    def get_pos(self, idx: int) -> tuple[int, int]:
        return idx % self.map_size[0], idx // self.map_size[1]
    

    def is_pos_in_bounds(self, x: int | float, y: int | float) -> bool:
        if type(x) == float: x = int(x / self.tile_size)
        if type(y) == float: y = int(y / self.tile_size)

        return (
            x >= 0 and x < self.map_size[0] and
            y >= 0 and y < self.map_size[1]
        )