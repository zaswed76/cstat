# -*- coding: utf-8 -*-

import logging.handlers, sys

def log(log_file):
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter("""'%(module)s '%(asctime)s.%(msecs)d %(levelname)s  at line %(lineno)d: %(message)s""", '%Y-%m-%d %H:%M:%S')

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

    handler = logging.FileHandler(log_file, 'a')
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

if __name__ == '__main__':
    log.debug("www")
    log.error("www")