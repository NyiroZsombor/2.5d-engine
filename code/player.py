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

        self.angle: float = 0
        self.rot_vel: float = 0
        self.rot_speed: float = math.pi / 120
        self.mouse_captured: bool = False

        self.fov: float = math.pi / 2
        self.ray_count: int = 128
        self.create_rays()

        self.actions: dict[str, int] = {
            "forward": pg.K_w,
            "backward": pg.K_s,
            "turn_left": pg.K_LEFT,
            "turn_right": pg.K_RIGHT,
            "move_left": pg.K_a,
            "move_right": pg.K_d
        }


    def create_rays(self) -> None:
        self.rays: list[Ray] = []
        for i in range(self.ray_count):
            t: float = i / (self.ray_count - 1)
            angle: float = self.angle + t * self.fov - self.fov / 2
            ray: Ray = Ray(self.x, self.y, angle, self.tile_map)
            ray.i = i
            self.rays.append(ray)


    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.KEYDOWN:
            if event.key == self.actions["forward"]:
                self.vel_x += self.speed
                self.vel_y += self.speed

            elif event.key == self.actions["backward"]:
                self.vel_x -= self.speed
                self.vel_y -= self.speed

            elif event.key == self.actions["turn_left"]:
                self.rot_vel = -self.rot_speed

            elif event.key == self.actions["turn_right"]:
                self.rot_vel = self.rot_speed

            if event.key == pg.K_ESCAPE:
                self.mouse_captured = not self.mouse_captured
                pg.mouse.set_visible(not self.mouse_captured)
                # print(f"{self.mouse_captured = }")

        elif event.type == pg.KEYUP:
            if event.key == self.actions["forward"]:
                self.vel_x -= self.speed
                self.vel_y -= self.speed
            elif event.key == self.actions["backward"]:
                self.vel_x += self.speed
                self.vel_y += self.speed

            elif event.key == self.actions["turn_left"]:
                self.rot_vel = 0

            elif event.key == self.actions["turn_right"]:
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


    def is_point_in_fov(self, x: float, y: float) -> bool:
        x -= self.x
        y -= self.y

        left_ray: Ray = self.rays[0]
        right_ray: Ray = self.rays[-1]

        xl = x * left_ray.sign_v
        yl = y * left_ray.sign_v
        xr = x * right_ray.sign_v
        yr = y * right_ray.sign_v

        return (
            left_ray.slope * xl < yl and
            right_ray.slope * xr > yr
        )


    def get_camera_edges(self, x: float, y: float) -> tuple[float, float, float, float]:
        x -= self.x
        y -= self.y

        left_ray: Ray = self.rays[0]
        right_ray: Ray = self.rays[-1]
        parallel_slope: float = math.tan(self.angle + math.pi / 2)

        a: float = (x * parallel_slope - y)
        x_n: float = a / (parallel_slope - left_ray.slope)
        x_m: float = a / (parallel_slope - right_ray.slope)
        y_n: float = x_n * left_ray.slope
        y_m: float = x_m * right_ray.slope

        return (x_n, x_m, y_m, y_n)
    

    def get_point_screen_pos(self, x: float, y: float, 
    edges: tuple[float, float, float, float]) -> float | None:
        if not self.is_point_in_fov(x, y): return None

        x -= self.x
        y -= self.y

        x_n, x_m, y_m, y_n = edges

        if ((self.angle >= math.pi / 4
        and self.angle < math.pi * 3 / 4) or 
        (self.angle >= math.pi * 5 / 4
        and self.angle < math.pi * 7 / 4)):
            t: float = (x - x_m) / (x_n - x_m)
        else:
            t: float = (y - y_m) / (y_n - y_m)

        return 1 - t
        

    def get_point_plane_dist(self, x: float, y: float, 
    edges: tuple[float, float, float, float]) -> float | None:
        if not self.is_point_in_fov(x, y): return None

        x -= self.x
        y -= self.y

        x_n, x_m, y_m, y_n = edges
        d_n: float = x_n**2 + y_n**2

        return math.sqrt(
            d_n - ((x_m - x_n) / 2)**2 -
            ((y_m - y_n) / 2)**2
        )
        
    def draw_rays(self, surf: pg.Surface) -> None:
        self.rays[0].draw(surf)
        self.rays[-1].draw(surf)


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


    def draw_3d(self, surf: pg.Surface, entities: list) -> None:
        def sort_func(x: any) -> float:
            if not x.plane_dist is None: return x.plane_dist
            else: return 0

        step_x: int = int(surf.get_width() / self.ray_count)

        sorted_rays: list[Ray] = self.rays.copy()
        entities = entities.copy()
        sorted_rays.sort(key=sort_func, reverse=True)
        entities.sort(key=sort_func, reverse=True)

        for ray in sorted_rays:
            if len(entities) > 0:
                if not (entities[0].plane_dist is None
                or ray.plane_dist is None):
                    if entities[0].plane_dist > ray.plane_dist:
                        entities.pop(0).draw_3d(surf)
            ray.draw_3d(surf, step_x, ray.i)

        for entity in entities:
            entity.draw_3d(surf)