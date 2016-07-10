import logging
logger = logging.getLogger(__name__)

from production.examples.spammy_module import f


def main():  # pragma: no cover
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname).1s %(module)10.10s:%(lineno)-4d %(message)s')
    logging.getLogger(
        'production.examples.spammy_module').setLevel(logging.WARN)

    logger.info(f())


if __name__ == '__main__':
    main()
