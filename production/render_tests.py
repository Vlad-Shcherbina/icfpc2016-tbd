from production import ioformats
from production.render import Renderer, hstack_images, render_polys_and_edges


def test_everything():
    p = ioformats.load_problem('00042')

    r = Renderer()
    r.draw_unit_square()
    r.draw_poly(p.silhouette[0])
    im1 = r.get_img()

    im2 = Renderer().draw_problem(p).get_img(size=100)

    im = hstack_images(im1, im2)
    #im.save('test_renderer.png')


def test_legacy_render_polys_and_edges():
    p = ioformats.load_problem('00042')
    im = render_polys_and_edges(p.silhouette, p.skeleton)
    #im.save('test_render_polys_and_edges.png')


def test_hstack_images():
    p = ioformats.load_problem('00042')
    im1 = render_polys_and_edges(p.silhouette, p.skeleton)

    p = ioformats.load_problem('00025')
    im2 = render_polys_and_edges(p.silhouette, p.skeleton)

    im = hstack_images(im1, im2)
    #im.save('test_hstack_images.png')


if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])
