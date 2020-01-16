""" Utilities (mainly the FeatureWriter class) used by the feature extractor 
executable to format and write outputs.
"""

import io
import os
import copy as cp
import logging
from typing import Optional, Any, Dict

import h5py
import numpy as np
import pandas as pd

from neuron_morphology.feature_extractor.utilities import unnest
from neuron_morphology.features.layer.layer_histogram import LayerHistogram


class FeatureWriter:

    def __init__(self, heavy_path: str, table_path: Optional[str] = None):
        """ Formats and writes feature extraction outputs

        Parameters
        ----------
        heavy_path : if "heavy" features (e.g. with array outputs) are 
            calculated, write them here.
        table_path : if an output table is requested, write it here

        """

        self.heavy_path = heavy_path
        self.table_path = table_path

        self.validate_table_extension()

        self.has_heavy = False
        self.heavy_file = h5py.File(self.heavy_path, driver="core")
        self.output: Dict[str, Any] = {}

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

        split = set(key.split("."))

        if "normalized_depth_histogram" in split:
            self.add_layer_histogram(owner, key, value)
            value = self.heavy_path

        elif "earth_movers_distance" in split:
            value = value._asdict()
            value["interpretation"] = str(value["interpretation"]).split(".")[1]
    
        elif isinstance(value, np.ndarray):
            value = value.tolist()

        return value

    def add_layer_histogram(
        self, 
        owner: str, 
        key: str, 
        histogram: LayerHistogram
    ):
        """ Add a layer histogram to this writer's heavy data

        Parameters
        ----------
        owner : identifies the reconstruction that owns this feature
        key : the name of the histogram
        histogram : the histogram's data

        """

        self.has_heavy = True

        group = self.heavy_file.create_group(f"{owner}/{key}")
        group.create_dataset("counts", data=histogram.counts)
        group.create_dataset("bin_edges", data=histogram.bin_edges)

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
            