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


    def draw_grid(self, surf: pg.Surface) -> None:
        color: int = 0x444444
        scale: tuple[float, float] = (
            surf.get_width() / 512,
            surf.get_height() / 512,
        )
        scaling: function = lambda x: int(x * scale)

        for i in range(self.map_size[0] + 1):
            y: int = i * self.tile_size
            start: tuple[int, int] = (0, int(y * scale[1]))
            end: tuple[int, int] = (
                int(surf.get_width() * scale[0]), int(y * scale[1]))

            start = tuple(map(scaling, start))
            end = tuple(map(scaling, end))
            pg.draw.line(surf, color, start, end)

        for i in range(self.map_size[1] + 1):
            x: int = i * self.tile_size
            start: tuple[int, int] = (int(x * scale[0]), 0)
            end: tuple[int, int] = (
                int(x * scale[0]), int(surf.get_height() * scale[1]))

            start = tuple(map(scaling, start))
            end = tuple(map(scaling, end))
            pg.draw.line(surf, color, start, end)


    def draw_tiles(self, surf: pg.Surface) -> None:
        scale: tuple[float, float] = (
            surf.get_width() / 512,
            surf.get_height() / 512,
        )

        for idx in range(len(self.grid)):
            tile: Tile | None = self.grid[idx]

            if not tile is None:
                size: tuple[int, int] = (
                    int(self.tile_size * scale[0]),
                    int(self.tile_size * scale[1])
                )
                pos: tuple[int, int] = (
                    int(self.get_pos(idx)[0] * self.tile_size * scale[0]),
                    int(self.get_pos(idx)[1] * self.tile_size * scale[0])
                )

                color: int = 0x008800
                pg.draw.rect(surf, color, (pos, size))


    def get_idx(self, x: int, y: int) -> int:
        return y * self.map_size[0] + x


    def get_tile(self, x: int, y: int) -> Tile | None:
        return self.grid[self.get_idx(x, y)]
    

    def get_pos(self, idx: int) -> tuple[int, int]:
        return idx % self.map_size[0], idx // self.map_size[1]
    

    def is_pos_in_bounds(self, x: int | float, y: int | float) -> bool:
        x /= self.tile_size
        y /= self.tile_size
        return (
            x >= 0 and x < self.map_size[0] and
            y >= 0 and y < self.map_size[1]
        )