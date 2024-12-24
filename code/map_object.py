class MapObject:
    min_height: float = 0.2
    max_height: float = 0.8
    height_diff: float = max_height - min_height
    depth: int = 8

    def calculate_inv_plane_dist(self) -> float | None:
        if self.plane_dist is None: return None

        norm_dist: float = self.plane_dist / (
            self.tile_map.tile_size * self.depth
        )
        return 1 - norm_dist
    

    def calculate_wall_scale(self) -> float | None:
        if self.inv_plane_dist is None: return None
        return self.height_diff * self.inv_plane_dist ** 2 + self.min_height