import pandas as pd
import argparse

import bc
import ncm


def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ncm", action="store", nargs="+")
    parser.add_argument("-d", action="store", nargs="+")

    return parser
