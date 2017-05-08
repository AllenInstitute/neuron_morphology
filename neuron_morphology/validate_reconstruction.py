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
from neuron_morphology.validation.errors import *
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
    parser.add_argument('file_names', type=str, nargs='+', help="SWC and Marker files")
    return parser.parse_args(args)


def main():

    args = vars(parse_arguments(sys.argv[1:]))
    reconstruction_files = []
    for file_name in args['file_names']:
        if glob.has_magic(file_name):
            reconstruction_files += glob.glob(file_name)
        else:
            reconstruction_files.append(file_name)

    swc_files = [f for f in reconstruction_files if f.endswith('.swc')]
    marker_files = [f for f in reconstruction_files if f.endswith('.marker')]

    if len(swc_files) > 1 or len(marker_files) > 1:
        print "You cannot choose a directory with more than one swc or marker file"
    else:
        report = Report()

        for swc_file in swc_files:
            try:
                swc.read_swc(swc_file, strict_validation=True)
                report.add_swc_errors(swc_file, [])
            except InvalidMorphology, im:
                report.add_swc_errors(swc_file, im.validation_errors)

            morphology = swc.read_swc(swc_file, strict_validation=False)
            stats = statistics.morphology_statistics(morphology)
            report.add_swc_stats(swc_file, stats)

        for marker_file in marker_files:
            matching_morphology_name = marker_file.replace('.marker', '.swc')
            if matching_morphology_name != swc_files[0]:
                print "No matching .swc file found. No marker validation was done for:\n %s \n\n" % marker_file
            else:
                morphology = None
                try:
                    morphology = swc.read_swc(matching_morphology_name, strict_validation=False)
                except InvalidMorphology, im:
                    report.add_marker_errors(marker_file, [MarkerValidationError("Unable to parse matching SWC file "
                                                                                 "to validate the marker file.", {}, "High")])
                if morphology:
                    try:
                        validation.validate_marker(marker.read_marker_file(marker_file), morphology)
                        report.add_marker_errors(marker_file, [])
                    except InvalidMarkerFile, imf:
                        report.add_marker_errors(marker_file, imf.validation_errors)

        print report.to_json()


if __name__ == "__main__":
    main()

