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

import sys
import logging
from logging.config import fileConfig
import swc as swc
from validation.errors import InvalidMorphology
import argparse


fileConfig('logging_config.ini')
logger = logging.getLogger()


def line_in_file(file_name, node_id):

    """ This function reads the swc file and returns the line that corresponds
        to the id of the node that is passed as a parameter
    """

    with open(file_name, "r") as f:
        for line in f:
            if line.lstrip().startswith('#'):
                continue
            tokens = line.split()
            if tokens[0] == node_id:
                return line


def parse_arguments(args):

    """ This function parses command line arguments """

    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', type=str, help="SWC file")
    return parser.parse_args(args)


if __name__ == "__main__":

    parse_arguments(sys.argv[1:])

    swc_file = sys.argv[1]
    try:
        swc.read_swc(swc_file, strict_validation=True)
    except InvalidMorphology, im:
        print "Morphology is invalid:\n" + str(im)
