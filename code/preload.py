import pygame as pg
import json
from PIL import Image, ImageDraw

def slice_texture(name: str) -> None:
    slice_path: str = ""
    texture_path: str = ""
    with open("paths.json") as file:
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
    with open("paths.json") as file:
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
    with open("paths.json") as file:
        paths: dict[str, str] = json.load(file)
        sprites_path = paths["sprites"]
    
    img: pg.Surface = pg.image.load(sprites_path + "/" + name + ".png")

    return pg.transform.scale_by((img), 8)

def get_gradient(
start: tuple[int, int, int],
end: tuple[int, int, int]) -> None:
    assets_path: str = ""
    with open("paths.json") as file:
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