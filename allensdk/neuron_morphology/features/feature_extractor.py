from . import core_features
import math


class FeatureExtractor(object):
    def __init__(self, morphology, node_types, soma_depth=0):
        """
        Calculates morphology features on the specified object
        Parameters
        ----------
        morphology: Morphology object
        """

        self._morphology = morphology
        self._node_types = node_types
        self._soma_depth = soma_depth
        self.features = {}
        self.calculate()

    def calculate(self):
        self.calculate_axon_cloud_features()
        self.calculate_axon_specific_features()
        self.calculate_number_of_stems()
        self.calculate_max_euclidean_distance()
        self.calculate_soma_features()
        self.calculate_bifurcation_moments()
        self.calculate_core_features()
        self.calculate_dimension_features()
        self.calculate_compartment_moment_features()

    def calculate_axon_cloud_features(self):

        # calculate axon cloud features -- ie, the subset of features of
        #   that can be calculated on an entire disconnected axon
        # ** out-of-order calculation **
        # max distance must be measured with soma present. for cloud, this
        #   must be calculated before non-soma branches are pruned
        ax_dist = core_features.calculate_max_euclidean_distance(self._morphology, self._node_types)
        self.calculate_compartment_moment_features()
        self.calculate_dimension_features()
        self.features["max_euclidean_distance"] = ax_dist

    def calculate_axon_specific_features(self):
        soma = self._morphology.get_root()
        rot, dist = core_features.calculate_axon_base(self._morphology, soma, self._node_types)
        self.features["soma_theta"] = rot
        self.features["soma_distance"] = dist

    def calculate_number_of_stems(self):
        self.features["num_stems"] = core_features.calculate_number_of_stems_by_type(self._morphology, self._node_types)

    def calculate_max_euclidean_distance(self):
        self.features["max_euclidean_distance"] = core_features.calculate_max_euclidean_distance(self._morphology,
                                                                                                 self._node_types)

    def calculate_soma_features(self):
        self.features["soma_surface"] = core_features.calculate_soma_surface(self._morphology)
        self.features["relative_soma_depth"] = self._soma_depth

    def calculate_bifurcation_moments(self):
        soma = self._morphology.get_root()
        moments = core_features.calculate_bifurcation_moments(self._morphology, soma, self._node_types)
        self.features["first_bifurcation_moment_x"] = moments[0][0]
        self.features["first_bifurcation_moment_y"] = moments[0][1]
        self.features["first_bifurcation_moment_z"] = moments[0][2]
        self.features["bifurcation_stdev_x"] = math.sqrt(moments[1][0])
        self.features["bifurcation_stdev_y"] = math.sqrt(moments[1][1])
        self.features["bifurcation_stdev_z"] = math.sqrt(moments[1][2])
        self.features["bifurcation_skew_x"] = moments[2][0]
        self.features["bifurcation_skew_y"] = moments[2][1]
        self.features["bifurcation_skew_z"] = moments[2][2]
        self.features["bifurcation_kurt_x"] = moments[3][0]
        self.features["bifurcation_kurt_y"] = moments[3][1]
        self.features["bifurcation_kurt_z"] = moments[3][2]

    def calculate_core_features(self):
        soma = self._morphology.get_root()
        self.features["max_path_distance"] = core_features.calculate_max_path_distance(self._morphology,
                                                                                       node_types=self._node_types)
        self.features["num_bifurcations"] = core_features.calculate_number_of_bifurcations(self._morphology,
                                                                                           node_types=self._node_types)
        self.features["num_outer_bifurcations"] = core_features.calculate_outer_bifs(self._morphology,
                                                                                     soma,
                                                                                     self._node_types)
        self.features["num_neurites"] = core_features.calculate_number_of_neurites(self._morphology,
                                                                                   node_types=self._node_types)
        self.features["num_branches"] = core_features.calculate_number_of_branches(self._morphology,
                                                                                   node_types=self._node_types)
        if self.features["num_branches"] != float('nan') and self.features["num_branches"] != 0:
            self.features["neurites_over_branches"] = 1.0 * self.features["num_branches"] / self.features["num_branches"]
        else:
            self.features["neurites_over_branches"] = float('nan')
        self.features["num_tips"] = core_features.calculate_number_of_tips(self._morphology,
                                                                           node_types=self._node_types)
        self.features["max_branch_order"] = core_features.calculate_max_branch_order(self._morphology,
                                                                                     node_types=self._node_types)
        self.features["contraction"] = core_features.calculate_mean_contraction(self._morphology,
                                                                                node_types=self._node_types)
        self.features["num_nodes"] = len(self._morphology.get_node_by_types(self._node_types))
        self.features["total_length"] = core_features.calculate_total_length(self._morphology,
                                                                             node_types=self._node_types)
        self.features["mean_parent_daughter_ratio"] = core_features.calculate_mean_parent_daughter_ratio(self._morphology,
                                                                                                         node_types=self._node_types)
        self.features["mean_fragmentation"] = core_features.calculate_mean_fragmentation(self._morphology,
                                                                                         node_types=self._node_types)
        self.features["bifurcation_angle_remote"] = core_features.calculate_bifurcation_angle_remote(self._morphology,
                                                                                                     node_types=self._node_types)
        self.features["bifurcation_angle_local"] = core_features.calculate_bifurcation_angle_local(self._morphology,
                                                                                                   node_types=self._node_types)
        self.features["parent_daughter_ratio"] = core_features.calculate_parent_daughter_ratio(self._morphology,
                                                                                               node_types=self._node_types)
        self.features["average_diameter"] = core_features.calculate_mean_diameter(self._morphology,
                                                                                  node_types=self._node_types)
        #
        sfc, vol = core_features.calculate_total_size(self._morphology, node_types=self._node_types)
        self.features["total_surface"] = sfc
        self.features["total_volume"] = vol
        #
        self.features["early_branch"] = core_features.calculate_early_branch_path(self._morphology,
                                                                                  soma,
                                                                                  self._node_types)

        self.centroid_over_distance()
        self.stdev_over_distance()
        self.centroid_over_stdev()

    def calculate_dimension_features(self):
        dims = core_features.calculate_dimensions(self._morphology, self._node_types)
        if dims is not None:
            low = dims[1]
            high = dims[2]
            self.features["width"] = dims[0][0]
            self.features["height"] = dims[0][1]
            self.features["depth"] = dims[0][2]
            self.features["low_x"] = low[0]
            self.features["low_y"] = low[1]
            self.features["low_z"] = low[2]
            self.features["high_x"] = high[0]
            self.features["high_y"] = high[1]
            self.features["high_z"] = high[2]

        else:
            self.features["width"] = float('nan')
            self.features["height"] = float('nan')
            self.features["depth"] = float('nan')
            self.features["low_x"] = float('nan')
            self.features["low_y"] = float('nan')
            self.features["low_z"] = float('nan')
            self.features["high_x"] = float('nan')
            self.features["high_y"] = float('nan')
            self.features["high_z"] = float('nan')

    def calculate_compartment_moment_features(self):
        soma = self._morphology.get_root()
        moments = core_features.calculate_compartment_moments(self._morphology, soma, self._node_types)
        self.features["first_compartment_moment_x"] = moments[0][0]
        self.features["first_compartment_moment_y"] = moments[0][1]
        self.features["first_compartment_moment_z"] = moments[0][2]
        self.features["compartment_stdev_x"] = math.sqrt(moments[1][0])
        self.features["compartment_stdev_y"] = math.sqrt(moments[1][1])
        self.features["compartment_stdev_z"] = math.sqrt(moments[1][2])
        self.features["compartment_skew_x"] = moments[2][0]
        self.features["compartment_skew_y"] = moments[2][1]
        self.features["compartment_skew_z"] = moments[2][2]
        self.features["compartment_kurt_x"] = moments[3][0]
        self.features["compartment_kurt_y"] = moments[3][1]
        self.features["compartment_kurt_z"] = moments[3][2]

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
