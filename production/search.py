from production import ioformats
from production.meshes import Mesh


def main():  # pragma: no cover
    p = ioformats.load_problem('00012')

    m = Mesh(p)
    m.debug_print()
    r = m.render()

    m.precompute_span_templates()
    for node in m.nodes:
        s = 0
        for angle in 1, 2, 4:
            if m.span_templates[node, angle]:
                s += angle
        if s != 7:
            r.draw_text(node, str(s))

    r.get_img(200).save('mesh.png')


if __name__ == '__main__':
    main()
