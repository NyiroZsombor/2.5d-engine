import pygame as pg
import math
from time import time
from tile_map import TileMap
from bullet import Bullet
from entity import Entity
from camera import Camera
from kinematic_entity import KinematicEntity

class Player(Camera, KinematicEntity):

    def __init__(self, x: float, y: float, tile_map: TileMap):
        Camera.__init__(self, x, y, tile_map)
        KinematicEntity.__init__(self, x, y, 8, 8, tile_map)

        self.init_movement()
        self.init_combat()


    def init_movement(self) -> None:
        self.rot_vel: float = 0
        self.rot_speed: float = math.pi / 120
        self.mouse_captured: bool = False
        self.movement_angle: float | None = None

        self.action_keys: dict[str, int] = {
            "forward": pg.K_w,
            "backward": pg.K_s,
            "turn_left": pg.K_LEFT,
            "turn_right": pg.K_RIGHT,
            "move_left": pg.K_a,
            "move_right": pg.K_d,
            "shoot": pg.K_SPACE
        }

        self.actions: dict[str, bool] = {}

        for key in self.action_keys.keys():
            self.actions[key] = False


    def init_combat(self) -> None:
        self.max_health: int = 5
        self.max_magazine: int = 5
        self.ammo_per_magazine: int = 6

        self.damage_immunity: float = 2
        self.last_damage_time: float = 0
        self.health: int = self.max_health
        self.ammo: int = self.ammo_per_magazine
        self.magazine: int = self.max_magazine

        self.reload_time: float = 3
        self.shooting_period: float = 1
        self.last_shot_time: float = time() - self.shooting_period
        self.bullets: list[Bullet] = []


    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.KEYDOWN:
            for key in self.action_keys.keys():
                if event.key == self.action_keys[key]:
                    self.actions[key] = True

            if event.key == pg.K_ESCAPE:
                self.mouse_captured = not self.mouse_captured
                pg.mouse.set_visible(not self.mouse_captured)
                # print(f"{self.mouse_captured = }")

        elif event.type == pg.KEYUP:
            for key in self.action_keys.keys():
                if event.key == self.action_keys[key]:
                    self.actions[key] = False

        if event.type == pg.MOUSEMOTION:
            if not self.mouse_captured: return

            self.rot_vel = event.rel[0] * math.pi / 512


    def update(self, entities: list[Entity]) -> None:
        self.handle_movement()

        if not self.movement_angle is None:
            dx: float = math.cos(self.movement_angle + self.angle)
            dy: float = math.sin(self.movement_angle + self.angle)
            self.vel_x = dx * self.speed
            self.vel_y = dy * self.speed
        else:
            self.vel_x = 0
            self.vel_y = 0

        self.move()

        self.angle += self.rot_vel
        if self.mouse_captured: self.rot_vel /= 2
        if abs(self.rot_vel) < math.pi / 120: self.rot_vel = 0

        if self.angle >= math.tau:
            self.angle = self.angle - math.tau
        if self.angle < 0:
            self.angle = self.angle + math.tau

        self.update_combat(entities)
        self.update_rays()


    def handle_movement(self) -> None:
        if (self.actions["turn_left"]
        == self.actions["turn_right"]): self.rot_vel = 0
        if self.actions["turn_left"]: self.rot_vel = -self.rot_speed
        if self.actions["turn_right"]: self.rot_vel = self.rot_speed

        count: int = 0
        movment_key: list[str] = [
            "forward", "backward", "move_left", "move_right"
        ]
        for key in self.action_keys.keys():
                if not key in movment_key: continue
                if self.actions[key]: count += 1

        if count == 0: self.movement_angle = None
        else: self.calculate_movement_angle(count)


    def calculate_movement_angle(self, count: int) -> float:
        angle_sum: float = 0

        if self.actions["backward"]: angle_sum += math.pi
        if self.actions["move_right"]: angle_sum += math.pi / 2
        if self.actions["move_left"] and self.actions["backward"]:
            angle_sum += math.pi * 3 / 2
        elif self.actions["move_left"]:
            angle_sum -= math.pi / 2

        self.movement_angle = angle_sum / count


    def update_combat(self, entities: list[Entity]) -> None:
        ready: bool = self.last_shot_time + self.reload_time < time()
        no_ammo: bool = self.ammo < 1
        has_magazine: bool = self.magazine > 0

        if ready and no_ammo and has_magazine:
            self.magazine -= 1
            self.ammo = self.ammo_per_magazine

        if self.actions["shoot"]:
            self.shoot()

        idx_to_remove: list[Bullet] = []

        for i in range(len(self.bullets)):
            bullet: Bullet = self.bullets[i]

            if bullet.update(self):
                idx_to_remove.append(i)
                continue
            
            for entity in entities:
                if bullet.collide(entity):
                    idx_to_remove.append(i)

        for entity in entities:
            if self.last_damage_time + self.damage_immunity < time():
                if self.collide(entity):
                    self.last_damage_time = time()
                    self.health -= 1

        while len(idx_to_remove) > 0:
            idx: int = idx_to_remove.pop()
            del self.bullets[idx]


    def shoot(self) -> None:
        if self.last_shot_time + self.shooting_period > time(): return
        if self.ammo < 1: return
        
        self.ammo -= 1
        self.last_shot_time = time()

        self.bullets.append(Bullet(self.x, self.y,self.tile_map, self.angle))


    def draw_2d(self, surf: pg.Surface) -> None:
        size: int = 8
        points: list[tuple[int, int]] = []
        scale: tuple[float, float] = (
            surf.get_width() / 512,
            surf.get_height() / 512,
        )

        for i in range(-1, 2):
            if i == 0: dist: int = 2
            else: dist: int = 1

            current_angle: float = self.angle + i * math.tau / 3
            scaled: int = dist * size
            
            points.append((
                int((scaled * math.cos(current_angle) + self.x) * scale[0]),
                int((scaled * math.sin(current_angle) + self.y) * scale[1])
            ))

        pg.draw.polygon(surf, (255, 128, 0), points)


    def draw_3d(self, surf: pg.Surface, entities: list[Entity]) -> None:
        union = entities.copy()
        union.extend(self.bullets)
        Camera.draw_3d(self, surf, union)