import pygame as pg
import json
from PIL import Image, ImageDraw

def slice_texture(name: str) -> None:
    slice_path: str = ""
    texture_path: str = ""
    with open("../paths.json") as file:
        paths: dict[str, str] = json.load(file)
        slice_path = paths["slices"]
        texture_path = paths["textures"]
    
    img: Image.Image = Image.open(texture_path + "/" + name + ".jpg")

    for x in range(img.size[0]):
        cropped: Image.Image = img.crop((
            x, 0, x + 1, img.size[1]
        ))

        cropped.save(slice_path + "/" + name + str(x) + ".jpg")

def get_texture_slices(name: str) -> list[pg.Surface]:
    slice_texture(name)
    slice_path: str = ""
    with open("../paths.json") as file:
        paths: dict[str, str] = json.load(file)
        slice_path = paths["slices"]
    
    i: int = 1
    slices: list[pg.Surface] = []
    
    while True:
        try:
            path: str = slice_path + "/" + name + str(i) + ".jpg"
            current: pg.Surface = pg.image.load(path)
        except FileNotFoundError:
            break
        slices.append(current)

        i += 1

    return slices

def get_sprites(name: str) -> pg.Surface:
    sprites_path: str = ""
    with open("../paths.json") as file:
        paths: dict[str, str] = json.load(file)
        sprites_path = paths["sprites"]
    
    img: pg.Surface = pg.image.load(sprites_path + "/" + name + ".png")

    return pg.transform.scale_by((img), 8)

def get_gradient(
start: tuple[int, int, int],
end: tuple[int, int, int]) -> pg.Surface:
    assets_path: str = ""
    with open("../paths.json") as file:
        paths: dict[str, str] = json.load(file)
        assets_path = paths["assets"]

    size = 1024
    img: Image.Image = Image.new("RGB", (size, size))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
    for i in range(size):
        t: float = abs(i - size / 2) / size * 2
        draw.rectangle((0, i, size, i + 1), (
            int((end[0] - start[0]) * t + start[0]),
            int((end[1] - start[1]) * t + start[1]),
            int((end[2] - start[2]) * t + start[2])
        ))

    path: str = assets_path + "/gradient.jpg"
    img.save(path)
    return pg.image.load(path)

def get_minimap_effect() -> pg.Surface:
    assets_path: str = ""
    with open("../paths.json") as file:
        paths: dict[str, str] = json.load(file)
        assets_path = paths["assets"]

    size = 1024
    strips: int = 4
    img: Image.Image = Image.new("RGB", (size, size))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
    
    for i in range(strips):
        color = (0x002200, 0x000000)[i % 2]
        y1: int = int(size * i / strips)
        j: int = 0

        while j / 32 < 32:
            draw.line((0, y1 + j, size, y1 + j), color, 32)
            j += 64

    path: str = assets_path + "/minimap_effect.jpg"
    img.save(path)
    return pg.image.load(path)

def get_vignette(
start: tuple[int, int, int],
end: tuple[int, int, int]) -> None:
    assets_path: str = ""
    with open("../paths.json") as file:
        paths: dict[str, str] = json.load(file)
        assets_path = paths["assets"]

    size = 1024
    x: int = int(size / 2)
    y: int = int(size / 2)
    img: Image.Image = Image.new("RGB", (size, size))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
    p: int = 64
    s: float = 0.75

    for i in range(p, 0, -1):
        t: float = (i / p)
        c: float = t**3
        draw.circle((x, y), int(t * size * s), (
            int((end[0] - start[0]) * c + start[0]),
            int((end[1] - start[1]) * c + start[1]),
            int((end[2] - start[2]) * c + start[2])
        ))

    path: str = assets_path + "/vignette.jpg"
    img.save(path)
    return pg.image.load(path)

if __name__ == "__main__":
    get_vignette((255, 255, 255), (0, 0, 0))