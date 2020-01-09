from typing import Sequence, Optional

import pandas as pd


class LayeredPointDepths:

    def __init__(
        self, 
        ids: Sequence, 
        layer_names: Sequence[str], 
        depths: Sequence, 
        local_layer_pia_side_depths: Sequence, 
        local_layer_wm_side_depths: Sequence,
        point_types: Sequence
    ):
        """ Represents the depths from pia of a collection of cortical points. 
        Units are not specified, but should agree with those used in e.g. 
        ReferenceLayerDepths.

        Parameters
        ----------
        ids : Unique identifiers for these points. e.g. node ids
        layer_names : For each point, the name of the layer containing that 
            point.
        depths : For each point, the distance from the pia surface to that 
            point. The distance metric need not be the euclidean distance, but 
            ought to be measured consistently across points and surfaces.
        local_layer_pia_side_depths : For each point, the distance between the 
            intersection of the shortest path to pia (according to a consistent 
            distance metric) and the upper surface of the layer containing the 
            point.
        local_layer_wm_side_depths : as local_layer_pia_side_depths, on the 
            white matter side. In the case of nodes that are themselves in 
            white matter, this should be nan.
        point_types : For each point, a value indicating the type of object 
            represented by that point (e.g. neuron_morphology.constants.AXON, 
            or "axon_terminal")

        """

        self.df = pd.DataFrame({
            "layer_name": layer_names,
            "depth": depths,
            "local_layer_pia_side_depth": local_layer_pia_side_depths,
            "local_layer_wm_side_depth": local_layer_wm_side_depths,
            "point_type": point_types
        }, index=pd.Index(name="id", data=ids))

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        data = df.reset_index().to_dict(orient="list")
        return cls(**data)

    @classmethod
    def from_csv(cls, path: str):
        return cls.from_dataframe(pd.read_csv(path))

    @classmethod
    def from_hdf5(cls, path: str):
        return cls.from_dataframe(pd.read_hdf(path))