import sys

from allensdk.brain_observatory.argschema_utilities import \
    optional_lims_inputs

from neuron_morphology.snap_polygons._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.snap_polygons._from_lims import get_inputs_from_lims


def main():
    """
    """


if __name__ == "__main__":
    parser = optional_lims_inputs(
        sys.argv, 
        InputParameters,
        OutputParameters, 
        get_inputs_from_lims
    )

    main()