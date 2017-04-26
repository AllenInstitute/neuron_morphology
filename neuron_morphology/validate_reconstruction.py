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
import argparse
import glob
import json


fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.ini'))
logger = logging.getLogger()


def create_report_swc(swc_file, errors):

    """ This function creates a report for swc validation """
    record = dict()
    record["file_name"] = swc_file
    record["errors"] = []

    for error in errors:
        error_record = dict()
        error_record['message'] = error.message
        error_record['ids'] = error.node_ids
        record["errors"].append(error_record)

    return record


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
    file_errors = dict()
    parsed_morphologies = dict()
    report = []

    for swc_file in swc_files:
        try:
            morphology = swc.read_swc(swc_file, strict_validation=True)
            parsed_morphologies[swc_file] = morphology
            file_errors[swc_file] = []
        except InvalidMorphology, im:
            parsed_morphologies[swc_file] = None
            file_errors[swc_file] = im.validation_errors
            print "Morphology is not valid.\n"
            report.append(create_report_swc(swc_file, file_errors[swc_file]))

        if file_errors[swc_file] is []:
            print "Morphology is valid."

    print json.dumps(report, indent=4, separators=(',', ': '))

    for marker_file in marker_files:
        matching_morphology_name = marker_file.replace('.marker', '.swc')
        if matching_morphology_name not in parsed_morphologies:
            print "No matching .swc file found for: %s" % marker_file
        else:
            matching_morphology = parsed_morphologies[matching_morphology_name]
            if not matching_morphology:
                print "Matching morphology failed validation"
            else:
                try:
                    validation.validate_marker(marker.read_marker_file(marker_file), matching_morphology)
                    print "Marker file is valid."
                except InvalidMarkerFile, imf:
                    print "Marker file is invalid:\n" + str(imf)


if __name__ == "__main__":
    main()

