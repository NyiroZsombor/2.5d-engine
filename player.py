import pygame as pg
import math
from ray import Ray
from tile_map import TileMap

class Player:

    def __init__(self, x: float, y: float, tile_map: TileMap):
        self.x = x
        self.y = y
        self.tile_map = tile_map

        self.vel_x: float = 0
        self.vel_y: float = 0
        self.speed: float = 0.75

        self.angle: float = -math.pi / 2
        self.rot_vel: float = 0
        self.rot_speed: float = math.pi / 90
        self.mouse_captured: bool = False

        self.fov: float = math.pi / 2
        self.ray_count: int = 128
        self.rays: list[Ray] = []
        for i in range(self.ray_count):
            t: float = i / (self.ray_count - 1)
            self.rays.append(Ray(
                self.x, self.y,
                self.angle + t * self.fov - self.fov / 2,
                self.tile_map
            ))

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.vel_x = self.speed
                self.vel_y = self.speed

            if event.key == pg.K_LSHIFT:
                self.vel_x = -self.speed
                self.vel_y = -self.speed

            elif event.key == pg.K_LEFT:
                self.rot_vel = -self.rot_speed

            elif event.key == pg.K_RIGHT:
                self.rot_vel = self.rot_speed
            if event.key == pg.K_ESCAPE:
                self.mouse_captured = not self.mouse_captured
                print(f"{self.mouse_captured = }")

        elif event.type == pg.KEYUP:
            if (event.key == pg.K_SPACE
            or event.key == pg.K_LSHIFT):
                self.vel_x = 0
                self.vel_y = 0

            elif event.key == pg.K_LEFT:
                self.rot_vel = 0

            elif event.key == pg.K_RIGHT:
                self.rot_vel = 0

        if event.type == pg.MOUSEMOTION:
            if not self.mouse_captured: return

            self.rot_vel = event.rel[0] * math.pi / 512


    def update(self) -> None:
        prev_x: float = self.x
        prev_y: float = self.y
        self.x += self.vel_x * math.cos(self.angle)
        self.y += self.vel_y * math.sin(self.angle)
        tile_x: int = int(self.x / self.tile_map.tile_size)
        tile_y: int = int(self.y / self.tile_map.tile_size)

        if not self.tile_map.get_tile(tile_x, tile_y) is None:
            self.x = prev_x
            self.y = prev_y

        self.angle += self.rot_vel
        if self.mouse_captured: self.rot_vel /= 2
        if abs(self.rot_vel) < math.pi / 120: self.rot_vel = 0

        if self.angle >= math.tau:
            self.angle = self.angle - math.tau
        if self.angle < 0:
            self.angle = self.angle + math.tau

        self.update_rays()        


    def update_rays(self) -> None:
        for i in range(self.ray_count):
            ray: Ray = self.rays[i]
            t: float = i / (self.ray_count - 1)
            angle: float = (
                self.angle + t * self.fov - self.fov / 2
            )

            if angle >= math.tau:
                angle -= math.tau
            if angle < 0:
                angle += math.tau

            ray.set_angle(angle)
            ray.set_xy(self.x, self.y)
            ray.update()
            ray.update_plane_dist(self.angle)


    def draw_rays(self, surf: pg.Surface) -> None:
        for ray in self.rays:
           ray.draw(surf)


    def draw(self, surf: pg.Surface) -> None:
        size: int = 8
        points: list[tuple[int, int]] = []
        for i in range(-1, 2):
            if i == 0: scale: int = 2
            else: scale: int = 1

            current_angle: float = self.angle + i * math.tau / 3
            scaled: int = scale * size
            
            points.append((
                int(scaled * math.cos(current_angle) + self.x),
                int(scaled * math.sin(current_angle) + self.y)
            ))

        pg.draw.polygon(surf, (255, 128, 0), points)


    def draw_3d(self, surf: pg.Surface) -> None:
        step_x: int = int(surf.get_width() / self.ray_count)

        for i in range(self.ray_count):
            ray = self.rays[i]

            if not ray.has_int: continue

            norm_dist: float = ray.plane_dist / (
                self.tile_map.tile_size * ray.depth
            )
            inv_dist: float = (1 - norm_dist)

            if inv_dist <= 0: continue

            if ray.int_axis == 0:
                color: int = int(inv_dist * 255) << 16
            else:
                color: int = (
                    (int(inv_dist * 255) << 16) +
                    (int(inv_dist * 128) << 8)
                )

            min_height: float = 0.2
            max_height: float = 0.7
            height_diff: float = max_height - min_height
            height: int = surf.get_height()

            wall_height: int = int((
                height_diff * inv_dist ** 2 + min_height
            ) * height)

            pos: tuple[int, int] = (
                step_x * i,
                int(height / 2 - wall_height / 2)
            )
            size: tuple[int, int] = (
                step_x,
                wall_height
            )
            if ray.tile_int is None:
                pg.draw.rect(surf, color, (pos, size))
                continue

            slice_num: int = int(
                ray.sub_grid_int[ray.int_axis] * ray.tile_int.slice_num
            )
            
            tint: int = int(255 * inv_dist)
            ray.tile_int.draw(
                surf, slice_num,
                (*pos, *size), tint + (tint << 8) + (tint << 16)
            )