# Define a set of utility functions to initialize the environment

import logging
import sys

def initRootLogger(logLevel):
    root = logging.getLogger()

    if (logLevel >= 1):
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[ %(levelname)s ] %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
