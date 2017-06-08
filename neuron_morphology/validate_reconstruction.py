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
import neuron_morphology.validation as validation
from neuron_morphology.validation.result import *
import neuron_morphology.marker as marker
from neuron_morphology.report import Report
import argparse
import glob
import neuron_morphology.statistics as statistics


fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.ini'))
logger = logging.getLogger()


def parse_arguments(args):

    """ This function parses command line arguments """

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, nargs='+', help="SWC and Marker files")
    parser.add_argument('--swc', type=str, help="SWC file")
    parser.add_argument('--marker', type=str, help="Marker file")
    return parser.parse_args(args)


def main():

    args = vars(parse_arguments(sys.argv[1:]))

    if args['dir'] is None and args['swc'] is None and args['marker'] is None:
        print "You need to provide one of the following arguments: directory, swc file, marker file"
        sys.exit(1)

    reconstruction_files = []
    swc_file = None
    marker_file = None
    if args['dir']:
        for file_name in args['dir']:
            if glob.has_magic(file_name):
                reconstruction_files += glob.glob(file_name)
            else:
                reconstruction_files.append(file_name)

        swc_files = [f for f in reconstruction_files if f.endswith('.swc')]
        marker_files = [f for f in reconstruction_files if f.endswith('.marker')]

        if len(swc_files) > 1 or len(marker_files) > 1:
            print "You cannot choose a directory with more than one swc or marker file"
            sys.exit(1)
        else:
            if len(swc_files) == 0:
                print "No swc file in the directory. No swc validation was done."
                sys.exit(1)
            else:
                matching_morphology_name = marker_files[0].replace('.marker', '.swc')
                if matching_morphology_name != swc_files[0]:
                    print "No matching .swc file found. No marker validation was done for:\n %s \n\n" % marker_files[0]
                    sys.exit(1)
        swc_file = swc_files[0]
        marker_file = marker_files[0]
    else:
        swc_file = args['swc']
        marker_file = args['marker']

    report = Report()
    try:
        swc.read_swc(swc_file, strict_validation=True)
        report.add_swc_results(swc_file, [])
    except InvalidMorphology, im:
        report.add_swc_results(swc_file, im.validation_errors)

    morphology = None
    try:
        morphology = swc.read_swc(swc_file, strict_validation=False)
    except InvalidMorphology, im:
        report.add_marker_results(marker_file, [MarkerValidationError("Unable to parse matching SWC file "
                                                                      "to validate the marker file.", {}, "Fatal")])
    if morphology:
        stats = statistics.morphology_statistics(morphology)
        report.add_swc_stats(swc_file, stats)

        if marker_file:
            try:
                results = validation.validate_marker(marker.read_marker_file(marker_file), morphology)
                report.add_marker_results(marker_file, results)
            except InvalidMarkerFile, imf:
                report.add_marker_results(marker_file, imf.validation_errors)

    print report.to_json()
    if report.has_results():
        sys.exit(1)


if __name__ == "__main__":
    main()

