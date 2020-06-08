import os
import sys
import logging
import neuron_morphology.swc_io as swc
import neuron_morphology.validation as validation
from neuron_morphology.validation.result import *
import neuron_morphology.marker as marker
from neuron_morphology.validation.report import Report
import argparse
import glob
import neuron_morphology.validation.morphology_statistics as statistics

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
        print("You need to provide one of the following arguments: directory, swc file, marker file")
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
            print("You cannot choose a directory with more than one swc or marker file")
            sys.exit(1)
        else:
            if len(swc_files) == 0:
                print("No swc file in the directory. No swc validation was done.")
                sys.exit(1)
            else:
                matching_morphology_name = marker_files[0].replace('.marker', '.swc')
                if matching_morphology_name != swc_files[0]:
                    print("No matching .swc file found. No marker validation was done for:\n %s \n\n" % marker_files[0])
                    sys.exit(1)
        swc_file = swc_files[0]
        marker_file = marker_files[0]
    else:
        swc_file = args['swc']
        marker_file = args['marker']

    report = Report()
    try:
        morpho = swc.morphology_from_swc(swc_file)
        morpho.validate(strict=True)
        report.add_swc_results(swc_file, [])
    except InvalidMorphology as im:
        report.add_swc_results(swc_file, im.validation_errors)

    morphology = None
    try:
        morphology = swc.morphology_from_swc(swc_file)
        morphology.validate(strict=False)
    except InvalidMorphology as im:
        report.add_marker_results(marker_file, [MarkerValidationError("Unable to parse matching SWC file "
                                                                      "to validate the marker file.", {}, "Fatal")])
    if morphology:
        stats = statistics.morphology_statistics(morphology)
        report.add_swc_stats(swc_file, stats)

        if marker_file:
            try:
                results = validation.validate_marker(marker.read_marker_file(marker_file), morphology)
                report.add_marker_results(marker_file, results)
            except InvalidMarkerFile as imf:
                report.add_marker_results(marker_file, imf.validation_errors)

    print(report.to_json())
    if report.has_results():
        sys.exit(1)


if __name__ == "__main__":
    main()
