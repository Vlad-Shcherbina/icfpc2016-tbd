from production import ioformats
from production import render


def test_render_polys_and_edges():
    p = ioformats.load_problem('00042')
    im = render.render_polys_and_edges(p.silhouette, p.skeleton)
    #im.save('test_render_polys_and_edges.png')


def test_hstack_images():
    p = ioformats.load_problem('00042')
    im1 = render.render_polys_and_edges(p.silhouette, p.skeleton)

    p = ioformats.load_problem('00025')
    im2 = render.render_polys_and_edges(p.silhouette, p.skeleton)

    im = render.hstack_images(im1, im2)
    #im.save('test_hstack_images.png')


if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])
