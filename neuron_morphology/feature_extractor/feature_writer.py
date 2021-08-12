""" Utilities (mainly the FeatureWriter class) used by the feature extractor 
executable to format and write outputs.
"""

import os
import copy as cp
import logging
import warnings

from typing import (
    Optional, Any, Dict, List, Iterable, Callable, NamedTuple, Union
)

import h5py
import pandas as pd
import numpy as np

from neuron_morphology.features.layer.layer_histogram import LayerHistogram
from neuron_morphology.feature_extractor.utilities import unnest
from neuron_morphology.features.layer.layer_histogram import \
    EarthMoversDistanceResult


class FeatureWriter:

    def __init__(
        self, 
        heavy_path: str, 
        table_path: Optional[str] = None, 
        formatters: Optional[Iterable["FeatureFormatter"]] = None,
        filemode: Optional[str] = 'w'
    ):
        """ Formats and writes feature extraction outputs

        Parameters
        ----------
        heavy_path : if "heavy" features (e.g. with array outputs) are 
            calculated, write them here.
        table_path : if an output table is requested, write it here

        """

        self.heavy_path = heavy_path
        self.table_path = table_path

        if formatters is None:
            formatters = []


        self.formatters: List["FeatureFormatter"] = list(formatters)
        self.has_heavy = False
        self.output: Dict[str, Any] = {}

        self.validate_table_extension()
        self.heavy_file = h5py.File(self.heavy_path, filemode, driver="core")


    def add_run(self, identifier: str, run: Dict[str, Any]):
        """ Add the results of a feature extraction run to this writer

        Parameters
        ----------
        identifier : the unique identifier for this run
        run : will be added

        """

        run = cp.deepcopy(run)
        features = unnest(run["results"])

        for key in list(features.keys()):
            features[key] = self.process_feature(identifier, key, features[key])

        run["results"] = features

        self.output[identifier] = run 

    def process_feature(self, owner: str, key: str, value: Any):
        """ Processes a feature for writing. This may involve:
            1. changing its type to something json serializable
            2. adding its value to this writer's heavy output

        Parameters
        ----------
        owner : identifies the reconstruction that owns this feature
        key : the name of the feature
        value : the feature's raw value

        Returns
        -------
        Transformed feature value

        """

        matched_handler = None
        matched_name = None

        for name, check, handler in self.formatters:
            if check(key, value):
                if matched_handler is None:
                    matched_handler = handler

                else:
                    warnings.warn(
                        f"skipping formatter: {name} "
                        f"for feature {key} calculated on {owner}"
                        f"({matched_name} matched first)"
                    )
        
        if matched_handler is not None:
            value = matched_handler(self, owner, key, value)

        return value

    def write(self):
        """ Write this writer's output to disk

        Returns
        -------
        This writer's outputs as a dictionary

        """

        if self.has_heavy:
            self.heavy_file.close()

        if self.table_path is not None:
            self.write_table()

        return self.output

    def validate_table_extension(self):
        """ If an output table was requested, check that the path has a 
        supported extension.
        """

        if self.table_path is None:
            return

        self.table_extension = os.path.splitext(self.table_path)[1]
        if self.table_extension not in {".csv"}:
            raise ValueError(f"unsupported extension: {self.table_extension}")

    def build_output_table(self) -> pd.DataFrame:
        """ Convert this writer's output to a reconstruction X feature table

        Returns
        -------
        the generated table

        """

        _table = []
        for reconstruction_id, data in self.output.items():
            current = cp.deepcopy(data["results"])
            current["reconstruction_id"] = reconstruction_id

            # this catches dicts that might have been produced during feature
            # processing
            _table.append(unnest(current))
        
        table = pd.DataFrame(_table)
        table.set_index("reconstruction_id", inplace=True)
        return table

    def write_table(self):
        """ Construct and write a reconstructions X features table from this 
        writer.
        """

        table = self.build_output_table()

        if self.table_extension == ".csv":
            logging.warning(
                "writing additional outputs to csv. See output json for "
                "record of selected features and marks"
            )
            table.to_csv(self.table_path)

        else:
            # just being defensive here - we validate on construction
            raise ValueError(f"invalid extension: {self.table_extension}")

    def register_formatters(self, formatters: Iterable["FeatureFormatter"]):
        """ Add formatters to this writer. The order matters! If multiple 
        formatters match a feature, only the first will be applied.

        Parameters
        ----------
        foratters : an ordered collection of formatter to register

        """
        self.formatters.extend(list(formatters))


# owner, key, value, heavy data store -> transformed value for json
FeatureOutputHandler = Callable[[FeatureWriter, str, str, Any], Any]

# key, value -> is this feature appropriate for this outputter?
FeatureOutputCheck = Callable[[str, Any], bool]

class FeatureFormatter(NamedTuple):
    """ Format feature results for output
    """

    # identifier, used for warning messages mainly
    name: str

    # is this formatter applicable?
    check: FeatureOutputCheck

    # actually format the output
    handler: FeatureOutputHandler

def has_subkey(subkey: str, key: str):
    """ Check whether a string occurs as one of the "."-separated members of 
    another. 
    """

    return subkey in key.split(".")

def add_layer_histogram(
    writer: FeatureWriter,
    owner: str, 
    key: str, 
    histogram: LayerHistogram
) -> str:
    """ Add a layer histogram to this writer's heavy data

    Parameters
    ----------
    owner : identifies the reconstruction that owns this feature
    key : the name of the histogram
    histogram : the histogram's data

    Returns
    -------
    the path at which this writer's heavy data will be stored

    """

    writer.has_heavy = True

    group = writer.heavy_file.create_group(f"{owner}/{key}")
    group.create_dataset("counts", data=histogram.counts)
    group.create_dataset("bin_edges", data=histogram.bin_edges)

    return writer.heavy_path


def process_earth_movers_distance(
    _writer: FeatureWriter,
    _owner: str,
    _key: str,
    value: EarthMoversDistanceResult
) -> Dict[str, Union[str, float]]:
    """ Convert an EarthMoversDistanceResult to a form suitable for json 
    serialization

    Parameters
    ----------
    _* : these are unused
    value : The result to be transformed

    Returns
    -------
    a dictionary like:
    {
        "result": <float result>,
        "interpretation" : <name of interpretation enum value>
    }

    """

    _value = value._asdict()
    _value["interpretation"] = str(_value["interpretation"]).split(".")[1]

    return _value

# ensure small numpy arrays can be serialized to json 
numpy_array_formatter = FeatureFormatter(
    "numpy_array_formatter",
    lambda _, feature: isinstance(feature, np.ndarray),
    lambda _, __, ___, value: value.tolist()
)

# ensure normalized depth histograms written to heavy data
normalized_depth_histogram_formatter = FeatureFormatter(
    "normalized_depth_histogram_formatter",
    lambda key, _: has_subkey("normalized_depth_histogram", key),
    add_layer_histogram
)

# convert earth movers distance results to dicts for json output
earth_movers_distance_formatter = FeatureFormatter(
    "earth_movers_distance_formatter",
    lambda key, _: has_subkey("earth_movers_distance", key),
    process_earth_movers_distance
)

DEFAULT_FEATURE_FORMATTERS = (
    normalized_depth_histogram_formatter,
    earth_movers_distance_formatter,
    numpy_array_formatter,

)
