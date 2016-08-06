from typing import List, Tuple
import random

from PIL import Image, ImageDraw

from production.cg import Point, polygon_area
from production import ioformats


class Renderer:
    """Responsible for drawing one single square image with polygons.

    Example:
    im = Renderer().draw_problem(p).get_img()

    Use hstack_images() to compose output of individual renderers.
    """

    def __init__(self):
        self.points_for_viewport = [Point(0, 0), Point(1, 1)]
        self.draw_commands = []
        self.size = 100

    def draw_unit_square(self):
        self.draw_poly(
            [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)],
            color=(60, 60, 60))
        return self

    def draw_poly(self, poly: List[Point], color=None):
        """
        `color` is RGB or RGBA tuple
        By default random greenish for CCW polys and
        random reddish for CW polys.
        """
        if color is None:
            area = polygon_area(poly)
            if area > 0:
                color = (
                    random.randrange(100),
                    random.randrange(150, 256),
                    random.randrange(100),
                    100)
            else:
                color = (
                    random.randrange(150, 256),
                    random.randrange(100),
                    random.randrange(100),
                    100)

        for pt in poly:
            self.update_viewport(pt)

        def draw_command(im):
            im2 = Image.new('RGBA', (self.size, self.size))
            draw2 = ImageDraw.Draw(im2)
            draw2.polygon([self.norm(pt) for pt in poly], fill=color)
            return Image.alpha_composite(im, im2)

        self.draw_commands.append(draw_command)
        return self

    def draw_edge(self, pt1: Point, pt2: Point, color=None):
        if color is None:
            color = (
                random.randrange(200, 255),
                random.randrange(200, 255),
                random.randrange(200, 255),
            )

        self.update_viewport(pt1)
        self.update_viewport(pt2)

        def draw_command(im):
            draw = ImageDraw.Draw(im)
            draw.line(
                [self.norm(pt1), self.norm(pt2)], fill=color)
            return im

        self.draw_commands.append(draw_command)
        return self

    def draw_problem(self, p: ioformats.Problem):
        self.draw_unit_square()
        for poly in p.silhouette:
            self.draw_poly(poly)
        for edge in p.skeleton:
            self.draw_edge(*edge)
        return self

    def get_img(self, size=None):
        if size:
            self.size = size

        self.min_x = min(p.x for p in self.points_for_viewport)
        self.max_x = max(p.x for p in self.points_for_viewport)
        self.min_y = min(p.y for p in self.points_for_viewport)
        self.max_y = max(p.y for p in self.points_for_viewport)

        w = self.max_x - self.min_x
        h = self.max_y - self.min_y

        # ensure 1:1 ratio
        d = (w - h) / 2
        self.min_y -= max(d, 0)
        self.max_y += max(d, 0)
        self.min_x -= max(-d, 0)
        self.max_x += max(-d, 0)

        im = Image.new('RGBA', (self.size, self.size))
        for draw_command in self.draw_commands:
            im = draw_command(im)

        return im

    def update_viewport(self, pt: Point):
        self.points_for_viewport.append(pt)

    def norm(self, pt: Point):
        return (
            (self.size - 1) * (pt.x - self.min_x) / (self.max_x - self.min_x),
            self.size - 1 - (self.size - 1) * (pt.y - self.min_y) / (
                self.max_y - self.min_y),
        )


def render_polys_and_edges(
        polys: List[List[Point]],
        edges: List[Tuple[Point, Point]],
        size=100) -> Image.Image:
    """This is legacy stuff, just use Renderer directly."""
    r = Renderer()
    r.draw_unit_square()
    for poly in polys:
        r.draw_poly(poly)
    for edge in edges:
        r.draw_edge(*edge)
    return r.get_img(size)


def hstack_images(im1, im2):
    #print(im1.size)
    assert im1.size[1] == im2.size[1]
    #return im1
    im = Image.new('RGBA', (im1.size[0] + im2.size[0], im1.size[1]))
    im.paste(im1, (0, 0) + im1.size)
    im.paste(im2, (im1.size[0], 0, im1.size[0] + im2.size[0], im1.size[1]))
    return im


def main():
    p = ioformats.load_problem('problem95')
    im = render_polys_and_edges(p.silhouette, p.skeleton)
    #im = hstack_images(im, im)
    im.save('hz.png')


if __name__ == '__main__':
    main()
