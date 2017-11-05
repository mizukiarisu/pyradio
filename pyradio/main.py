import csv
import sys
import curses
import logging
from argparse import ArgumentParser
from os import path, getenv

from .radio import PyRadio

PATTERN = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def __configureLogger():
    logger = logging.getLogger("pyradio")
    logger.setLevel(logging.DEBUG)

    # Handler
    fh = logging.FileHandler("pyradio.log")
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(PATTERN)

    # add formatter to ch
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(fh)


DEFAULT_FILE = ''
locations = []
if getenv('XDG_CONFIG_HOME'):
    locations.append(path.join(getenv('XDG_CONFIG_HOME'), 'pyradio', 'stations.csv'))
locations.extend([path.join(getenv('HOME', '~'), '.pyradio', 'stations.csv'),
                 path.join(getenv('HOME', '~'), '.pyradio'),
                 path.join(path.dirname(__file__), 'stations.csv')])

for p in locations:
    if path.exists(p) and path.isfile(p):
        DEFAULT_FILE = p
        break


def shell():
    parser = ArgumentParser(description="Console radio player")
    parser.add_argument("--stations", "-s", default=DEFAULT_FILE,
                        help="Path on stations csv file.")
    parser.add_argument("--play", "-p", nargs='?', default=False,
                        help="Start and play. "
                        "The value is num station or empty for random.")
    parser.add_argument("--add", "-a", action='store_true',
                        help="Add station to list.")
    parser.add_argument("--list", "-l", action='store_true',
                        help="List of added stations.")
    parser.add_argument("--debug", "-d", action='store_true',
                        help="Start pyradio in debug mode.")
    args = parser.parse_args()

    # No need to parse the file if we add station
    if args.add:
        params = raw_input("Enter the name: "), raw_input("Enter the url: ")
        with open(args.stations, 'a') as cfgfile:
            writter = csv.writer(cfgfile)
            writter.writerow(params)
            sys.exit()

    with open(args.stations, 'r') as cfgfile:
        stations = []
        for row in csv.reader(filter(lambda row: row[0]!='#', cfgfile), skipinitialspace=True):
            if not row:
                continue
            name, url = [s.strip() for s in row]
            stations.append((name, url))

    if args.list:
        for name, url in stations:
            print(('{0:50s} {1:s}'.format(name, url)))
        sys.exit()

    if args.debug:
        __configureLogger()
        print("Debug mode acitvated")

    # Starts the radio gui.
    pyradio = PyRadio(stations, play=args.play)
    curses.wrapper(pyradio.setup)


if __name__ == '__main__':
    shell()
