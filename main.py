import pygame as pg
import sys
import preload
import time
from player import Player
from tile_map import TileMap
from tile import Tile

pg.init()
pg.display.init()
pg.font.init()

pg.display.set_caption("2.5D renderer")
screen_size: tuple[int, int] = (512, 512)
screen: pg.Surface = pg.display.set_mode(screen_size)
minimap: pg.Surface = pg.surface.Surface((512, 512))
screens: dict[str, pg.Surface] = {
    "main": screen,
    "minimap": minimap
}

gradient: pg.Surface = preload.get_gradient((0, 0, 0), (255, 255, 255))
gradient = pg.transform.scale(gradient, screen_size)
tile_map: TileMap = TileMap((16, 16), 32)

for i in range(16 * 16):
    if i % 14 == 0:
        tile_map.grid[i] = Tile("block")
    elif (i % 7 == 0
    or i // 16 == 0
    or i // 16 == 15
    or i % 16 == 0
    or i % 16 == 15):
        tile_map.grid[i] = Tile("brick")

player: Player = Player(150, 150, tile_map)
clock: pg.time.Clock = pg.time.Clock()
frames: int = 0
start: float = time.time()

while True:
    if frames == 60:
        print(f"fps: {round(1 / ((time.time() - start) / 60))}")
        start = time.time()
        frames = 0
    frames += 1

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        player.handle_event(event)

        if event.type == pg.MOUSEMOTION:
            if not player.mouse_captured: continue

            if event.pos[0] <= screen_size[0] / 4 and event.rel[0] < 0:
                pg.mouse.set_pos(screen_size[1] * 3 / 4, event.pos[1])
            elif event.pos[0] >= screen_size[1] * 3 / 4 and event.rel[0] > 0:
                pg.mouse.set_pos(screen_size[1] / 4, event.pos[1])

    player.update()

    screen.fill(0)
    screen.blit(gradient, (0, 0))

    minimap.fill(0)
    player.draw_3d(screens["main"])
    tile_map.draw(screens["minimap"])
    # tile_map.draw_grid(screens["minimap"])
    player.draw(screens["minimap"])
    # player.draw_rays(screens["minimap"])

    screen.blit(pg.transform.scale(
        minimap, (128, 128)
    ), (0, 0))

    pg.display.flip()
    clock.tick(60)