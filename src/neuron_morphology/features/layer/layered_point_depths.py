from typing import Sequence
import os

import pandas as pd


class LayeredPointDepths:

    DF_COLS = {
        "ids", "layer_name", "depth", "local_layer_pia_side_depth", 
        "local_layer_wm_side_depth", "point_type"
    }

    def __init__(
        self, 
        ids: Sequence, 
        layer_name: Sequence[str], 
        depth: Sequence, 
        local_layer_pia_side_depth: Sequence, 
        local_layer_wm_side_depth: Sequence,
        point_type: Sequence
    ):
        """ Represents the depths from pia of a collection of cortical points. 
        Units are not specified, but should agree with those used in e.g. 
        ReferenceLayerDepths.

        Parameters
        ----------
        ids : Unique identifiers for these points. e.g. node ids
        layer_name : For each point, the name of the layer containing that 
            point.
        depth : For each point, the distance from the pia surface to that 
            point. The distance metric need not be the euclidean distance, but 
            ought to be measured consistently across points and surfaces.
        local_layer_pia_side_depth : For each point, the distance between the 
            intersection of the shortest path to pia (according to a consistent 
            distance metric) and the upper surface of the layer containing the 
            point.
        local_layer_wm_side_depth : as local_layer_pia_side_depths, on the 
            white matter side. In the case of nodes that are themselves in 
            white matter, this should be nan.
        point_type : For each point, a value indicating the type of object 
            represented by that point (e.g. neuron_morphology.constants.AXON, 
            or "axon_terminal")

        """

        self.df = pd.DataFrame({
            "layer_name": layer_name,
            "depth": depth,
            "local_layer_pia_side_depth": local_layer_pia_side_depth,
            "local_layer_wm_side_depth": local_layer_wm_side_depth,
            "point_type": point_type
        }, index=pd.Index(name="ids", data=ids))

    def to_csv(self, path: str):
        self.df.to_csv(path)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        data = df.reset_index()
        for colname in data.columns:
            if colname not in cls.DF_COLS:
                data.drop(columns=[colname], inplace=True)
        return cls(**data.to_dict(orient="list"))

    @classmethod
    def from_csv(cls, path: str):
        return cls.from_dataframe(pd.read_csv(path))

    @classmethod
    def from_hdf5(cls, path: str):
        return cls.from_dataframe(pd.read_hdf(path))

    @classmethod
    def read(cls, path: str):
        extension = os.path.splitext(path)[1]

        if extension == ".csv":
            return cls.from_csv(path)
        elif extension in (".h5", ".hdf", ".hdf5"):
            return cls.from_hdf5(path)
        else:
            raise IOError(f"unrecognized extension: {extension}")