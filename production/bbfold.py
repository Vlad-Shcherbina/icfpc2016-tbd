from production.cg import Point
from production.ioformats import Solution
from fractions import Fraction
from typing import List, Tuple

def foldpoints(target_len: Fraction) -> List[Tuple[Fraction, Fraction]]:
    current_len = Fraction(1)
    half_folds = 0
    while target_len <= current_len / 2:
        current_len /= 2
        half_folds += 1
    remainder = current_len - target_len
    
    for i in range(2 ** half_folds + 1):
        if remainder and i % 2:
            yield ( current_len * i - remainder,
                    current_len - remainder)
            
        yield ( current_len * i,
                current_len - 2 * remainder if i % 2 else Fraction(0))

        if remainder and i % 2 and current_len * i + remainder < 1:
            yield ( current_len * i + remainder,
                    current_len - remainder)
            

def foldgrid(x1, y1, x2, y2) -> Solution:
    target_width = x2 - x1
    target_height = y2 - y1
    xpoints = list(foldpoints(target_width))
    ypoints = list(foldpoints(target_height))
    orig_points = [Point(x, y) for x, _ in xpoints for y, _ in ypoints]
    dst_points = [Point(x + x1, y + y1) for _, x in xpoints for _, y  in ypoints]
    facets = []
    stride = len(ypoints)
    for x in range(len(xpoints) - 1):
        for y in range(len(ypoints) - 1):
            idx = x * stride
            facets.append([idx, idx + 1, idx + stride + 1, idx + stride])

    return Solution(orig_points, facets, dst_points)


def _m2s(mapping):
    return '; '.join('{} {}'.format(f1, f2) for f1, f2 in mapping)


def test_foldpoints1():
    assert _m2s(foldpoints(Fraction(1))) == '0 0; 1 1'
    assert _m2s(foldpoints(Fraction(1, 2))) == '0 0; 1/2 1/2; 1 0'
    assert _m2s(foldpoints(Fraction(1, 4))) == '0 0; 1/4 1/4; 1/2 0; 3/4 1/4; 1 0'
    
    assert _m2s(foldpoints(Fraction(2, 3))) == '0 0; 2/3 2/3; 1 1/3'
    assert _m2s(foldpoints(Fraction(3, 8))) == '0 0; 3/8 3/8; 1/2 1/4; 5/8 3/8; 1 0'
        

if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])