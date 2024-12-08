import pygame as pg
from PIL import Image, ImageDraw

def slice_texture(name: str) -> None:
    out_path: str = "assets/slices/"
    
    img: Image.Image = Image.open("assets/" + name + ".jpg")

    for x in range(img.size[0]):
        cropped: Image.Image = img.crop((
            x, 0, x + 1, img.size[1]
        ))

        cropped.save(out_path + name + str(x) + ".jpg")

def get_texture_slices(name: str) -> list[pg.Surface]:
    slice_texture(name)
    i: int = 1
    slices: list[pg.Surface] = []
    
    while True:
        try:
            current: pg.Surface = pg.image.load(f"assets/slices/{name}{i}.jpg")
        except FileNotFoundError:
            break
        slices.append(current)

        i += 1

    return slices

def get_gradient(
start: tuple[int, int, int],
end: tuple[int, int, int]) -> None:
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

    img.save("gradient.jpg")
    return pg.image.load("gradient.jpg")

if __name__ == "__main__":
    pass