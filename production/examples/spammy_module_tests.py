from production.examples.spammy_module import f


def test_hz():
    assert f() == 42


if __name__ == '__main__':
    import sys, logging, pytest
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__] + sys.argv[1:])
