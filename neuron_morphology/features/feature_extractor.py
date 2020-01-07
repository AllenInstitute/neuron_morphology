from neuron_morphology.features.axon import calculate_axon_features
from neuron_morphology.features.axon_cloud import calculate_axon_cloud_features
from neuron_morphology.features.bifurcation_moments import calculate_bifurcation_moment_features
from neuron_morphology.features.compartment_moments import calculate_compartment_moment_features
from neuron_morphology.features.core_features import calculate_core_features
from neuron_morphology.features.dimension import calculate_dimension_features
from neuron_morphology.features.soma import calculate_soma_features
from neuron_morphology.feature_extractor.data import Data

class FeatureExtractor(object):
    def __init__(self, morphology, node_types, data:Data=0, soma_depth=0):

        """
        Calculates morphology features on the specified object

        Parameters
        ----------
        morphology: Morphology object
        node_types: list
        soma_depth: int

        """

        self._morphology = morphology
        self._node_types = node_types
        self._data = data
        self._soma_depth = soma_depth
        self.features = {}
        self.calculate()

    def calculate(self):

        axon_cloud_features = calculate_axon_cloud_features(self._morphology, self._node_types)
        axon_features = calculate_axon_features(self._morphology, self._node_types)
        soma_features = calculate_soma_features(self._morphology, self._data)
        bifurcation_features = calculate_bifurcation_moment_features(self._morphology, self._node_types)
        core_features = calculate_core_features(self._morphology, self._node_types)
        dimension_features = calculate_dimension_features(self._morphology, self._node_types)
        compartment_features = calculate_compartment_moment_features(self._morphology, self._node_types)
        self.features.update(axon_cloud_features)
        self.features.update(axon_features)
        self.features.update(soma_features)
        self.features.update(bifurcation_features)
        self.features.update(core_features)
        self.features.update(dimension_features)
        self.features.update(compartment_features)
        self.centroid_over_distance()
        self.stdev_over_distance()
        self.centroid_over_stdev()

    def centroid_over_distance(self):
        # bifurcation centroid over max distance (eg, height)
        if self.features["width"] != float('nan') and self.features["width"] != 0.0:
            val = self.features["first_bifurcation_moment_x"] / self.features["width"]
        else:
            val = float('nan')
        self.features["bifurcation_centroid_over_distance_x"] = val
        #
        if self.features["height"] != float('nan') and self.features["height"] != 0.0:
            val = self.features["first_bifurcation_moment_y"] / self.features["height"]
        else:
            val = float('nan')
        self.features["bifurcation_centroid_over_distance_y"] = val
        #
        if self.features["depth"] != float('nan') and self.features["depth"] != 0.0:
            val = self.features["first_bifurcation_moment_z"] / self.features["depth"]
        else:
            val = float('nan')
        self.features["bifurcation_centroid_over_distance_z"] = val
        #
        ########################
        # centroid over max distance (eg, height)
        if self.features["width"] != float('nan') and self.features["width"] != 0.0:
            val = self.features["first_compartment_moment_x"] / self.features["width"]
        else:
            val = float('nan')
        self.features["compartment_centroid_over_distance_x"] = val
        #
        if self.features["height"] != float('nan') and self.features["height"] != 0.0:
            val = self.features["first_compartment_moment_y"] / self.features["height"]
        else:
            val = float('nan')
        self.features["compartment_centroid_over_distance_y"] = val
        #
        if self.features["depth"] != float('nan') and self.features["depth"] != 0.0:
            val = self.features["first_compartment_moment_z"] / self.features["depth"]
        else:
            val = float('nan')
        self.features["compartment_centroid_over_distance_z"] = val

    def stdev_over_distance(self):
        ########################
        # bifurcation stdev (sqrt(2nd moment)) over max distance (eg, height)
        if self.features["width"] != float('nan') and self.features["width"] != 0.0:
            val = self.features["bifurcation_stdev_x"] / self.features["width"]
        else:
            val = float('nan')
        self.features["bifurcation_stdev_over_distance_x"] = val
        #
        if self.features["height"] != float('nan') and self.features["height"] != 0.0:
            val = self.features["bifurcation_stdev_y"] / self.features["height"]
        else:
            val = float('nan')
        self.features["bifurcation_stdev_over_distance_y"] = val
        #
        if self.features["depth"] != float('nan') and self.features["depth"] != 0.0:
            val = self.features["bifurcation_stdev_z"] / self.features["depth"]
        else:
            val = float('nan')
        self.features["bifurcation_stdev_over_distance_z"] = val
        #
        ########################
        # stdev (sqrt(2nd moment)) over max distance (eg, height)
        if self.features["width"] != float('nan') and self.features["width"] != 0.0:
            val = self.features["compartment_stdev_x"] / self.features["width"]
        else:
            val = float('nan')
        self.features["compartment_stdev_over_distance_x"] = val
        #
        if self.features["height"] != float('nan') and self.features["height"] != 0.0:
            val = self.features["compartment_stdev_y"] / self.features["height"]
        else:
            val = float('nan')
        self.features["compartment_stdev_over_distance_y"] = val
        #
        if self.features["depth"] != float('nan') and self.features["depth"] != 0.0:
            val = self.features["compartment_stdev_z"] / self.features["depth"]
        else:
            val = float('nan')
        self.features["compartment_stdev_over_distance_z"] = val
        #

    def centroid_over_stdev(self):
        # centroid (1st moment) over standard deviation (sqrt(2nd moment)) along
        #   each axis
        #
        # measure over bifurcations
        first = self.features["first_bifurcation_moment_x"]
        stdev = self.features["bifurcation_stdev_x"]
        if first != float('nan') and stdev != float('nan') and stdev != 0.0:
            val = first / stdev
        else:
            val = float('nan')
        self.features["bifurcation_stdev_over_centroid_x"] = val
        #
        first = self.features["first_bifurcation_moment_y"]
        stdev = self.features["bifurcation_stdev_y"]
        if first != float('nan') and stdev != float('nan') and stdev != 0.0:
            val = first / stdev
        else:
            val = float('nan')
        self.features["bifurcation_stdev_over_centroid_y"] = val
        #
        first = self.features["first_bifurcation_moment_z"]
        stdev = self.features["bifurcation_stdev_z"]
        if first != float('nan') and stdev != float('nan') and stdev != 0.0:
            val = first / stdev
        else:
            val = float('nan')
        self.features["bifurcation_stdev_over_centroid_z"] = val
        #
        #   measured over compartments
        first = self.features["first_compartment_moment_x"]
        stdev = self.features["compartment_stdev_x"]
        if first != float('nan') and stdev != float('nan') and stdev != 0.0:
            val = first / stdev
        else:
            val = float('nan')
        self.features["compartment_stdev_over_centroid_x"] = val
        #
        first = self.features["first_compartment_moment_y"]
        stdev = self.features["compartment_stdev_y"]
        if first != float('nan') and stdev != float('nan') and stdev != 0.0:
            val = first / stdev
        else:
            val = float('nan')
        self.features["compartment_stdev_over_centroid_y"] = val
        #
        first = self.features["first_compartment_moment_z"]
        stdev = self.features["compartment_stdev_z"]
        if first != float('nan') and stdev != float('nan') and stdev != 0.0:
            val = first / stdev
        else:
            val = float('nan')
        self.features["compartment_stdev_over_centroid_z"] = val
