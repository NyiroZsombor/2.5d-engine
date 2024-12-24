import pygame as pg
import sys
import preload
import json
from time import time
from player import Player
from tile_map import TileMap
from tile import Tile
from entity import Entity

class Game:

    def __init__(self) -> None:
        self.init_dependencies()

        self.paths: dict[str, str]
        with open("../paths.json") as file:
            self.paths = json.load(file)

        self.init_display()
        self.init_effects()

        self.tile_map: TileMap = TileMap((16, 16), 32)

        for i in range(16 * 16):
            if i % 14 == 0:
                self.tile_map.grid[i] = Tile("block")
            elif (i % 7 == 0
            or i // 16 == 0
            or i // 16 == 15
            or i % 16 == 0
            or i % 16 == 15):
                self.tile_map.grid[i] = Tile("brick")

        self.player: Player = Player(150, 150, self.tile_map)
        self.entities: list[Entity] = [
            Entity("ghost", 300, 300, self.tile_map),
            Entity("box", 100, 50, self.tile_map),
            Entity("bullet", 200, 100, self.tile_map)
        ]
        self.clock: pg.time.Clock = pg.time.Clock()
        self.ticks: int = 0
        self.fps_start_ticks: int = 0
        self.monitor_fps: bool = False
        self.fps_start: float = time()
        self.mouse_pos: tuple[int, int] = (0, 0)

        self.game_loop()


    def init_dependencies(self) -> None:
        pg.init()
        pg.display.init()
        pg.font.init()
        Tile.init()
        Entity.init()


    def init_display(self) -> None:
        pg.display.set_caption("2.5D renderer")
        pg.display.set_icon(pg.image.load(self.paths["assets"] + "/icon.png"))

        self.screen_size: tuple[int, int] = (768, 704)
        screen: pg.Surface = pg.display.set_mode(self.screen_size)
        main_view: pg.Surface = pg.surface.Surface((768, 512))
        minimap: pg.Surface = pg.surface.Surface((256, 256))
        ui: pg.Surface = pg.surface.Surface((768, 192))

        self.load_resources()

        self.screens: dict[str, pg.Surface] = {
            "minimap": minimap,
            "screen": screen,
            "main_view": main_view,
            "ui": ui
        }


    def load_resources(self) -> None:
        self.ui_img: pg.Surface = self.load_ui_img("ui")
        self.ammo_img: pg.Surface = self.load_ui_img("ammo")
        self.magazine_img: pg.Surface = self.load_ui_img("magazine")
        self.full_heart_img: pg.Surface = self.load_ui_img("full_heart")
        self.empty_heart_img: pg.Surface = self.load_ui_img("empty_heart")

        self.font: pg.font.Font = pg.font.Font(
            self.paths["fonts"] + "/Roboto-Light.ttf", 12
        )


    def load_ui_img(self, name: str) -> pg.Surface:
        return pg.transform.scale2x(
            pg.image.load(self.paths["ui"] + "/" + name + ".png")
        )
        

    def init_effects(self) -> None:
        self.gradient: pg.Surface = preload.get_gradient(
            (0, 0, 0), (255, 255, 255)
        )
        self.gradient = pg.transform.scale(self.gradient, self.screen_size)

        self.minimap_size: tuple[int, int] = (256, 256)
        self.minimap_effect: pg.Surface = preload.get_minimap_effect()
        self.minimap_effect = pg.transform.scale(
            self.minimap_effect, (128, 128)
        )
        self.vignette: pg.Surface = preload.get_vignette(
            (255, 255, 255), (0, 0, 0), "vignette"
        )
        self.vignette = pg.transform.scale(
            self.vignette, self.screens["main_view"].get_size()
        )
        self.low_health_vignette: pg.Surface = preload.get_vignette(
            (255, 255, 255), (255, 0, 0), "low_health_vignette"
        )
        self.low_health_vignette = pg.transform.scale(
            self.low_health_vignette, self.screens["main_view"].get_size()
        )


    def game_loop(self) -> None:
        while True:
            if time() - self.fps_start > 1 and self.ticks > 0:
                if self.monitor_fps:
                    fps: float = round(
                        1 / ((time() - self.fps_start)
                        / (self.ticks - self.fps_start_ticks))
                    )
                    print(f"fps: {fps}")
                self.fps_start = time()
                self.fps_start_ticks = self.ticks
            self.ticks += 1

            for event in pg.event.get():
                self.handle_event(event)

            self.update()
            self.draw()

            pg.display.flip()
            self.clock.tick(60 if not self.monitor_fps else 0)
            

    def handle_event(self, event) -> None:
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        self.player.handle_event(event)

        if event.type == pg.MOUSEMOTION:
            self.mouse_pos = event.pos

            if not self.player.mouse_captured: return

            w34: int = int(self.screen_size[0] * 3 / 4)
            w4: int = int(self.screen_size[0] / 4)
            h34: int = int(self.screen_size[1] * 3 / 4)
            h4: int = int(self.screen_size[1] / 4)

            if event.pos[0] <= w4 and event.rel[0] < 0:
                pg.mouse.set_pos(w34, event.pos[1])
            elif event.pos[0] >= w34 and event.rel[0] > 0:
                pg.mouse.set_pos(w4, event.pos[1])

            if event.pos[1] <= h4 and event.rel[1] < 0:
                pg.mouse.set_pos(event.pos[0], h34)
            elif event.pos[0] >= h34 and event.rel[1] > 0:
                pg.mouse.set_pos(event.pos[0], h4)


    def update(self) -> None:
        self.player.update(self.entities)
        for entity in self.entities:
            entity.update(self.player)


    def draw(self) -> None:
        self.screens["screen"].fill(0)

        self.draw_main_view()
        self.draw_ui()


    def draw_main_view(self) -> None:
        self.screens["main_view"].blit(pg.transform.scale(
                self.gradient, self.screens["main_view"].get_size()
        ), (0, 0))

        self.player.draw_3d(self.screens["main_view"], self.entities)

        has_taken_damage: bool = (
            self.player.last_damage_time + 0.5 >= time()
        )
        low_health: bool = self.player.health == 1
        period: float = (self.player.last_damage_time + time()) % 1
        blink: bool = period < 0.5

        if has_taken_damage or (low_health and blink):
            self.screens["main_view"].blit(
                self.low_health_vignette, (0, 0), special_flags=pg.BLEND_RGB_MULT
            )
        else:
            self.screens["main_view"].blit(
                self.vignette, (0, 0), special_flags=pg.BLEND_RGB_MULT
            )

        self.screens["screen"].blit(self.screens["main_view"], (0, 0))


    def draw_ui(self) -> None:
        self.screens["ui"].blit(self.ui_img, (0, 0))

        self.draw_minimap()
        self.draw_name()
        self.draw_ammo()
        self.draw_health()

        self.screens["screen"].blit(self.screens["ui"], (0, 512))


    def draw_minimap(self) -> None:
        self.screens["minimap"].fill(0x002200)
        self.tile_map.draw(self.screens["minimap"])
        for entity in self.entities:
            entity.draw_2d(self.screens["minimap"])
        self.player.draw_2d(self.screens["minimap"])
        
        pos: tuple[int, int] = (334, 34)
        w: int = self.minimap_size[0]
        h: int = self.minimap_size[1]
        w2: int = int(w / 2)
        h2: int = int(h / 2)
        area: tuple[int, int] = (
            min(max(int(self.player.x / 2 - w2 / 2), 0), w2),
            min(max(int(self.player.y / 2 - h2 / 2), 0), h2),
            w / 2, h / 2
        )

        pos2: tuple[int, int] = (
            area[0], area[1] + int((self.ticks / 2) % h2)
        )
        pos3: tuple[int, int] = (
            area[0], area[1] + int((self.ticks / 2) % h2) - h2
        )

        self.screens["minimap"].blit(
            self.minimap_effect, pos2, special_flags=pg.BLEND_RGB_ADD
        )
        self.screens["minimap"].blit(
            self.minimap_effect, pos3, special_flags=pg.BLEND_RGB_ADD
        )
        self.screens["ui"].blit(self.screens["minimap"], pos, area)


    def draw_name(self) -> None:
        text: pg.Surface = self.font.render("some guy", True, 0)
        text = pg.transform.scale2x(text)
        if text.get_width() > 152:
            text = pg.transform.scale(text, (152, text.get_height()))
        self.screens["ui"].blit(
            text, (int(231 - text.get_width() / 2), 36)
        )


    def draw_ammo(self) -> None:
        p: Player = self.player
        x: int = 153
        y1: int = 90
        y_cd: int = y1 + self.ammo_img.get_height() + 4
        y2: int = 138
        w = (self.ammo_img.get_width() + 2) * 10

        for i in range(p.ammo):
            offset: int = (self.ammo_img.get_width() + 2) * i
            self.screens["ui"].blit(self.ammo_img, (x + offset, y1))

        if p.ammo > 0:
            t: int = int((time() - p.last_shot_time) / p.shooting_period * w)
        else:
            t: int = int((time() - p.last_shot_time) / p.reload_time * w)

        t = min(t, w)
        if t < w:
            start: tuple[int, int] = (x, y_cd)
            end: tuple[int, int] = (x + w - t, y_cd)
            pg.draw.line(self.screens["ui"], 0x00DD00, start, end)

        for i in range(self.player.magazine):
            offset: int = (self.magazine_img.get_width() + 2) * i
            self.screens["ui"].blit(self.magazine_img, (x + offset, y2))


    def draw_health(self) -> None:
        x: int = 499
        y: int = 35
        w: int = self.full_heart_img.get_width()

        for i in range(self.player.health):
            self.screens["ui"].blit(self.full_heart_img, (x + i * (w + 2), y))


if __name__ == "__main__":
    Game()