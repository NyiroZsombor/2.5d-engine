import pygame as pg
import math
from ray import Ray
from tile_map import TileMap

class Camera:

    def __init__(self, x: float, y: float, tile_map: TileMap) -> None:
        self.x = x
        self.y = y
        self.tile_map = tile_map
        self.tile_size = self.tile_map.tile_size

        self.angle: float = 0
        self.fov: float = math.pi / 2
        self.ray_count: int = 128
        self.rays: list[Ray] = []

        for i in range(self.ray_count):
            t: float = i / (self.ray_count - 1)
            angle: float = self.angle + t * self.fov - self.fov / 2
            ray: Ray = Ray(self.x, self.y, angle, self.tile_map)
            ray.i = i
            self.rays.append(ray)


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


    def get_camera_edges(self, x: float,
    y: float) -> tuple[float, float, float, float]:
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