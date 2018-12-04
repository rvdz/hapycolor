from unittest import defaultTestLoader as loader, TextTestRunner
import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbosity", help="Verbosity [0-3]", type=int,
                    required=False)
    args = vars(ap.parse_args())

    path_to_my_project = os.path.dirname(os.path.abspath(__file__)) + '/../'
    sys.path.insert(0, path_to_my_project)

    suite = loader.discover('tests')

    verbosity = int(args["verbosity"]) if args["verbosity"] is not None else 1
    runner = TextTestRunner(verbosity=verbosity)
    ret = not runner.run(suite).wasSuccessful()
    return ret


if __name__ == '__main__':
    sys.exit(main())
