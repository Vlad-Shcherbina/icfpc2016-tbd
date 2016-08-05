from typing import List, Tuple
import random

from PIL import Image, ImageDraw

from production.cg import Point, polygon_area
from production.ioformats import load_problem


def render_polys_and_edges(
        polys: List[List[Point]],
        edges: List[Tuple[Point, Point]],
        size=100) -> Image.Image:

    points = sum(polys, [])
    points.append(Point(0, 0))
    points.append(Point(1, 1))

    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)

    def norm(x, y):
        return (
            (size - 1) * (x - min_x) / (max_x - min_x),
            size - 1 - (size - 1) * (y - min_y) / (max_y - min_y),
        )

    im = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(im)

    # Unit square, for scale
    draw.polygon([
        norm(0, 0),
        norm(1, 0),
        norm(1, 1),
        norm(0, 1),
    ], fill=(60, 60, 60))

    for poly in polys:
        im2 = Image.new('RGB', (size, size))
        draw2 = ImageDraw.Draw(im2)

        area = polygon_area(poly)
        # CCW is greenish
        # CW is reddish
        if area > 0:
            color = (
                random.randrange(100),
                random.randrange(150, 256),
                random.randrange(100))
        else:
            color = (
                random.randrange(150, 256),
                random.randrange(100),
                random.randrange(100))

        draw2.polygon([norm(pt.x, pt.y) for pt in poly], fill=color)

        im = Image.blend(im, im2, 0.5)

    draw = ImageDraw.Draw(im)
    for pt1, pt2 in edges:
        draw.line(
            [norm(pt1.x, pt1.y), norm(pt2.x, pt2.y)], fill=(255, 255, 255))

    return im


def main():
    p = load_problem('problem7')
    im = render_polys_and_edges(p.silhouette, p.skeleton)
    im.save('hz.png')


if __name__ == '__main__':
    main()
