import pygame as pg
import math
from tile_map import TileMap
from tile import Tile
# TODO: angle = 90°, tan(angle)?
class Ray:
    depth: int = 8
    min_height: float = 0.2
    max_height: float = 0.8
    height_diff: float = max_height - min_height

    def __init__(self, x: float, y: float, angle: float, tile_map: TileMap):
        self.tile_map = tile_map
        self.tile_size = self.tile_map.tile_size
        self.font: pg.font.Font = pg.font.Font(size=16)
        self.set_angle(angle)
        self.set_xy(x, y)
        self.update()


    def set_xy(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.update_position()

    def set_angle(self, angle: float) -> None:
        self.angle = angle
        self.update_angle()


    def update_plane_dist(self, angle: float) -> None:
        self.angle_diff: float | None = None
        self.plane_dist: float | None = None

        if not self.has_int: return
        
        self.angle_diff = self.angle - angle
        self.plane_dist = self.dist * math.cos(self.angle_diff)


    def update_position(self) -> None:
        tile_size: int = self.tile_size
        
        self.first_vx: float = self.x - self.x % tile_size
        if self.angle < math.pi / 2 or self.angle > math.pi * 3 / 2:
            self.first_vx += tile_size
        self.first_vy: float = self.y + (self.first_vx - self.x) * self.slope

        
        self.first_hy: float = self.y - self.y % tile_size
        if self.angle < math.pi: self.first_hy += tile_size
        if self.slope:
            self.first_hx: float | None = (
                self.x + (self.first_hy - self.y) / self.slope
            )


    def update_angle(self) -> None:
        self.slope: float = math.tan(self.angle)

        if abs(self.slope) > 0.0001:
            self.step_h: float | None = self.tile_size / self.slope
        else:
            self.step_h: float | None = None

        if abs(self.slope) < 1000:
            self.step_v: float | None = self.tile_size * self.slope
        else:
            self.step_v: float | None = None

        self.sin: float = math.sin(self.angle)
        self.cos: float = math.cos(self.angle)
        self.rounding: tuple[function, function] = self.get_rounding()
        self.round_mat: dict[int, tuple[function, function]] = {
            0: (int, self.rounding[1]),
            1: (self.rounding[0], int)
        }

        if (self.angle > math.pi / 2 and
        self.angle < math.pi * 3 / 2): self.sign_v: int = -1
        else: self.sign_v: int = 1
        if self.angle < math.pi: self.sign_h: int = 1
        else: self.sign_h: int = -1


    def get_rounding(self) -> tuple[any, any]:
        if (self.angle > math.pi / 2 and
            self.angle < math.pi * 3 / 2):
            x: function = lambda x: int(x) - 1
        else:
            x: function = int

        if self.angle < math.pi:
            y: function = int
        else:
            y: function = lambda x: int(x) - 1

        return (x, y)


    def update(self) -> None:
        # self.update_position()
        # self.update_angle()

        intersection: tuple[float, float, int] | None = self.get_intersection()
        self.rel_int: tuple[float, float] | None = None
        self.int_axis: int | None = None
        self.abs_int: tuple[float, float] | None = None
        self.grid_int: tuple[int, int] | None = None
        self.sub_grid_int: tuple[float, float] | None = None
        self.tile_int: Tile | None = None
        self.dist: float | None = None
        self.has_int: bool = not intersection is None

        if not self.has_int: return

        self.rel_int = intersection[0:2]
        self.int_axis = intersection[2]

        self.abs_int = (
            self.rel_int[0] + self.x, self.rel_int[1] + self.y
        )

        self.grid_int = (
            self.round_mat[self.int_axis][0](self.abs_int[0] / self.tile_size),
            self.round_mat[self.int_axis][1](self.abs_int[1] / self.tile_size),
        )

        self.tile_int = self.tile_map.get_tile(*self.grid_int)

        self.sub_grid_int = (
            (self.abs_int[0] / self.tile_size) % 1,
            (self.abs_int[1] / self.tile_size) % 1
        )

        self.tile_map.get_tile(*self.grid_int)

        self.dist = math.hypot(*self.rel_int)

    
    def get_intersection_axis(self, axis: int) -> tuple[float, float] | None:
        for t in range(self.depth):
            if self.step_h is None and axis == 0: return None
            if self.step_v is None and axis == 1: return None

            if axis == 0:
                x: float = self.first_hx + self.step_h * t * self.sign_h
                y: float = self.first_hy + self.tile_size * t * self.sign_h
            else:
                x: float = self.first_vx + self.tile_size * t * self.sign_v
                y: float = self.first_vy + self.step_v * t * self.sign_v

            tile_x: int = self.round_mat[axis][0](x / self.tile_size)
            tile_y: int = self.round_mat[axis][1](y / self.tile_size)

            if not self.tile_map.is_pos_in_bounds(x, y): return None
            if not self.tile_map.get_tile(tile_x, tile_y) is None:
                return (x, y)


    def get_intersection(self) -> tuple[float, float, int] | None:
        ints: tuple[tuple[float, float] | None, tuple[float, float] | None] = (
            self.get_intersection_axis(0),
            self.get_intersection_axis(1)
        )

        none_count: int = ints.count(None)
        if none_count == 2: return None
        if none_count == 1:
            if not ints[0] is None: idx: int = 0
            else: idx: int = 1

            intersection: tuple[int, int] = ints[idx]

            rel_int: tuple[int, int] = (
                intersection[0] - self.x,
                intersection[1] - self.y
            )

            if (max(rel_int) <= self.depth * self.tile_size
            and min(rel_int) >= -self.depth * self.tile_size):
                return (*rel_int, idx)
            else:
                return None

        rel_ints: tuple[tuple[float, float], tuple[float, float]] = (
            (ints[0][0] - self.x, ints[0][1] - self.y),
            (ints[1][0] - self.x, ints[1][1] - self.y)
        )

        closest_int: int

        if abs(rel_ints[0][0]) < abs(rel_ints[1][0]): closest_int = 0
        else: closest_int = 1

        if (max(rel_ints[closest_int]) <= self.depth * self.tile_size
        and min(rel_ints[closest_int]) >= -self.depth * self.tile_size):
            return (*rel_ints[closest_int], closest_int)
        else:
            return None


    def draw_h(self, surf: pg.Surface) -> None:
        for t in range(self.depth):
            if self.step_h is None: break

            color: tuple[int, int, int] = (0, 255, 255)
            center: tuple[int, int] = (
                int(self.first_hx + self.step_h * t * self.sign_h),
                int(self.first_hy + self.tile_size * t * self.sign_h)
            )
            pg.draw.circle(surf, color, center, 1)



    def draw_v(self, surf: pg.Surface) -> None:
        for t in range(self.depth):
            if self.step_v is None: break

            color: tuple[int, int, int] = (255, 0, 255)
            center: tuple[int, int] = (
                int(self.first_vx + self.tile_size * t * self.sign_v),
                int(self.first_vy + self.step_v * t * self.sign_v)
            )
            pg.draw.circle(surf, color, center, 1)


    def draw(self, surf: pg.Surface) -> None:
        self.draw_h(surf)
        self.draw_v(surf)
        
        if self.rel_int:
            pg.draw.circle(
                surf, (255, 255, 255),
                (
                    self.rel_int[0] + self.x,
                    self.rel_int[1] + self.y
                ), 2
            )

    def draw_text(self, surf: pg.Surface) -> None:
        text: pg.Surface = self.font.render(
            str(self.sub_grid_int), False, 0, 0xFFFFFF
        )

        surf.blit(text, (
            self.abs_int[0] + 16,
            self.abs_int[1] + 16
        ))


    def draw_3d(self, surf: pg.Surface, step_x: int, i: int) -> None:
        if not self.has_int: return
        inv_dist: float = self.calculate_inv_dist()
        if inv_dist <= 0: return
        
        screen_height: int = surf.get_height()
        wall_height: int = Ray.calculate_wall_height(
            inv_dist, Ray.height_diff, Ray.min_height
        ) * screen_height
        
        rect: tuple[int, int, int, int] = (
            step_x * i, int(screen_height / 2 - wall_height / 2),
            step_x, wall_height
        )

        if self.tile_int is None:
            self.draw_3d_fallback(surf, rect, inv_dist)
            return

        self.draw_slice(surf, inv_dist, rect)


    def calculate_inv_dist(self) -> float:
        norm_dist: float = self.plane_dist / (
            self.tile_map.tile_size * self.depth
        )
        return 1 - norm_dist
    

    def calculate_wall_height(inv_dist: float, diff: float, min: float) -> float:
        return diff * inv_dist ** 2 + min
    

    def draw_3d_fallback(self, surf: pg.Surface,
    rect: tuple[int, int, int, int], inv_dist: float) -> None:
        if self.int_axis == 0:
                color: int = int(inv_dist * 255) << 16
        else:
            color: int = (
                (int(inv_dist * 255) << 16) +
                (int(inv_dist * 128) << 8)
            )
        pg.draw.rect(surf, color, rect)


    def draw_slice(self, surf: pg.Surface,
    inv_dist: float, rect: tuple[int, int, int, int]) -> None:
        slice_num: int = int(
            self.sub_grid_int[self.int_axis] * self.tile_int.slice_num
        )
        
        tint: int = int(255 * inv_dist)
        self.tile_int.draw(
            surf, slice_num,
            rect, tint + (tint << 8) + (tint << 16)
        )