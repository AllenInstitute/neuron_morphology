# Copyright 2017 Allen Institute for Brain Science
# This file is part of Allen SDK.
#
# Allen SDK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Allen SDK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Allen SDK.  If not, see <http://www.gnu.org/licenses/>.

# Author: Nika Keller

import os
import sys
import logging
from logging.config import fileConfig
import swc as swc
from validation.errors import InvalidMarkerFile
import argparse
import glob


fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.ini'))
logger = logging.getLogger()


def validate_marker(fname):
    print("Evaluating '%s'" % fname)
    err = False
    # make sure the name contains 'marker'
    if len(fname.split('marker')) == 1:
        print("ERROR: File name does not contain string 'marker'.")
        err = True
    # make sure there are an appropriate number of columns
    with open(fname, "r") as f:
        cnt = 0
        line_err = False
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            cnt += 1
            if line[0] == '#':
                continue
            cols = line.split(',')
            if len(cols) != 10 and not line_err:
                print("ERROR: Line %d has %d CSV column(s). Expected 10." % (cnt, len(cols)))
                err = True
                line_err = True
    if not err:
        print("OK")
    # TODO consider looking for a node for each marker point in the associated
    #   SWC file
    return err


def parse_arguments(args):

    """ This function parses command line arguments """

    parser = argparse.ArgumentParser()
    parser.add_argument('file_names', type=str, nargs='+', help="Marker files")
    return parser.parse_args(args)


def main():

    args = vars(parse_arguments(sys.argv[1:]))
    marker_files = []
    for file_name in args['file_names']:
        if glob.has_magic(file_name):
            marker_files += glob.glob(file_name)
        else:
            marker_files.append(file_name)

    for marker_file in marker_files:
        try:
            swc.read_marker_file(marker_file, strict_validation=True)
        except InvalidMarkerFile, im:
            print "Marker file is invalid:\n" + str(im)


if __name__ == "__main__":
    main()
