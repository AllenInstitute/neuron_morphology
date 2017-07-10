import math
import core_features

# derived feature calculation

def centroid_over_distance(features):
    # bifurcation centroid over max distance (eg, height)
    if features["width"] != float('nan') and features["width"] != 0.0:
        val = features["first_bifurcation_moment_x"] / features["width"]
    else:
        val = float('nan')
    features["bifurcation_centroid_over_distance_x"] = val
    #
    if features["height"] != float('nan') and features["height"] != 0.0:
        val = features["first_bifurcation_moment_y"] / features["height"]
    else:
        val = float('nan')
    features["bifurcation_centroid_over_distance_y"] = val
    #
    if features["depth"] != float('nan') and features["depth"] != 0.0:
        val = features["first_bifurcation_moment_z"] / features["depth"]
    else:
        val = float('nan')
    features["bifurcation_centroid_over_distance_z"] = val
    #
    ########################
    # centroid over max distance (eg, height)
    if features["width"] != float('nan') and features["width"] != 0.0:
        val = features["first_compartment_moment_x"] / features["width"]
    else:
        val = float('nan')
    features["compartment_centroid_over_distance_x"] = val
    #
    if features["height"] != float('nan') and features["height"] != 0.0:
        val = features["first_compartment_moment_y"] / features["height"]
    else:
        val = float('nan')
    features["compartment_centroid_over_distance_y"] = val
    #
    if features["depth"] != float('nan') and features["depth"] != 0.0:
        val = features["first_compartment_moment_z"] / features["depth"]
    else:
        val = float('nan')
    features["compartment_centroid_over_distance_z"] = val

def stdev_over_distance(features):
    ########################
    # bifurcation stdev (sqrt(2nd moment)) over max distance (eg, height)
    if features["width"] != float('nan') and features["width"] != 0.0:
        val = features["bifurcation_stdev_x"] / features["width"]
    else:
        val = float('nan')
    features["bifurcation_stdev_over_distance_x"] = val
    #
    if features["height"] != float('nan') and features["height"] != 0.0:
        val = features["bifurcation_stdev_y"] / features["height"]
    else:
        val = float('nan')
    features["bifurcation_stdev_over_distance_y"] = val
    #
    if features["depth"] != float('nan') and features["depth"] != 0.0:
        val = features["bifurcation_stdev_z"] / features["depth"]
    else:
        val = float('nan')
    features["bifurcation_stdev_over_distance_z"] = val
    #
    ########################
    # stdev (sqrt(2nd moment)) over max distance (eg, height)
    if features["width"] != float('nan') and features["width"] != 0.0:
        val = features["compartment_stdev_x"] / features["width"]
    else:
        val = float('nan')
    features["compartment_stdev_over_distance_x"] = val
    #
    if features["height"] != float('nan') and features["height"] != 0.0:
        val = features["compartment_stdev_y"] / features["height"]
    else:
        val = float('nan')
    features["compartment_stdev_over_distance_y"] = val
    #
    if features["depth"] != float('nan') and features["depth"] != 0.0:
        val = features["compartment_stdev_z"] / features["depth"]
    else:
        val = float('nan')
    features["compartment_stdev_over_distance_z"] = val
    #


def centroid_over_stdev(features):
    # centroid (1st moment) over standard deviation (sqrt(2nd moment)) along 
    #   each axis
    #
    # measure over bifurcations
    first = features["first_bifurcation_moment_x"]
    stdev = features["bifurcation_stdev_x"]
    if first != float('nan') and stdev != float('nan') and stdev != 0.0:
        val = first / stdev
    else:
        val = float('nan')
    features["bifurcation_stdev_over_centroid_x"] = val
    #
    first = features["first_bifurcation_moment_y"]
    stdev = features["bifurcation_stdev_y"]
    if first != float('nan') and stdev != float('nan') and stdev != 0.0:
        val = first / stdev
    else:
        val = float('nan')
    features["bifurcation_stdev_over_centroid_y"] = val
    #
    first = features["first_bifurcation_moment_z"]
    stdev = features["bifurcation_stdev_z"]
    if first != float('nan') and stdev != float('nan') and stdev != 0.0:
        val = first / stdev
    else:
        val = float('nan')
    features["bifurcation_stdev_over_centroid_z"] = val
    #
    #   measured over compartments
    first = features["first_compartment_moment_x"]
    stdev = features["compartment_stdev_x"]
    if first != float('nan') and stdev != float('nan') and stdev != 0.0:
        val = first / stdev
    else:
        val = float('nan')
    features["compartment_stdev_over_centroid_x"] = val
    #
    first = features["first_compartment_moment_y"]
    stdev = features["compartment_stdev_y"]
    if first != float('nan') and stdev != float('nan') and stdev != 0.0:
        val = first / stdev
    else:
        val = float('nan')
    features["compartment_stdev_over_centroid_y"] = val
    #
    first = features["first_compartment_moment_z"]
    stdev = features["compartment_stdev_z"]
    if first != float('nan') and stdev != float('nan') and stdev != 0.0:
        val = first / stdev
    else:
        val = float('nan')
    features["compartment_stdev_over_centroid_z"] = val



class MorphologyFeatures(object):
    def __init__(self, morph, soma_depth=0):
        """
        Calculates morphology features on the specified object

        Parameters
        ----------
        morph: Morphology object
        """
        self.axon = {}
        self.axon_cloud = {}
        self.dendrite = {}
        self.apical_dendrite = {}
        self.basal_dendrite = {}
        self.all_neurites = {}
        #
        self.calculate(morph, soma_depth)


    def calculate(self, morph, soma_depth=0):
        """
        Calculates all features on dendrites and/or axons that stem
        from the soma (ie, it ignores all trees having non-soma roots)
        """
        soma = morph.soma_root()
        # calculate axon cloud features -- ie, the subset of features of 
        #   that can be calculated on an entire disconnected axon
        cloud = morph.clone()
        # ** out-of-order calculation **
        # max distance must be measured with soma present. for cloud, this
        #   must be calculated before non-soma branches are pruned
        ax_dist = core_features.calculate_max_euclidean_distance(morph, 2)
        self.axon_cloud["max_euclidean_distance"] = ax_dist
        # now strip all non-axon nodes and calculate subset of features
        #   appropriate for clouds
        cloud.strip_all_other_types(node_type=2, keep_soma=False)
        self.axon_cloud = self._connection_independent_features(cloud, soma)
        ############################
        # eliminate all but the first tree (assume that one's primary)
        base = morph.clone()
        while base.num_trees > 1:
            base.delete_tree(1)
        # when stripping nodes, eliminate the soma. this is to cover
        #   for the contingency where the axon sprouts from a dendrite,
        #   or vice versa, and would otherwise be connected to the soma
        #
        # some features require the soma however. calculate those separately
        #   below
        #
        # axon-related features
        axon = morph.clone()
        axon.strip_all_other_types(node_type=2, keep_soma=False)
        self.axon = self._calculate(axon, soma)
        # dendrite (basal & apical combined)
        dendrite = morph.clone()
        dendrite.convert_type(4, 3) # convert apical nodes to dend nodes
        dendrite.strip_all_other_types(node_type=3, keep_soma=False)
        self.dendrite = self._calculate(dendrite, soma)
        # basal dendrite
        basal = morph.clone()
        basal.strip_all_other_types(node_type=3, keep_soma=False)
        self.basal_dendrite = self._calculate(basal, soma)
        # apical dendrite
        apical = morph.clone()
        apical.strip_all_other_types(node_type=4, keep_soma=False)
        self.apical_dendrite = self._calculate(apical, soma)
        # axon, basal and apical combined
        all_neurites = morph.clone()
        dendrite.convert_type(4, 3) # convert all nodes to one type
        dendrite.convert_type(2, 3) # convert all nodes to one type
        all_neurites.strip_all_other_types(node_type=3, keep_soma=False)
        self.all_neurites = self._calculate(all_neurites, soma)
        ################################################################
        # features requiring soma
        #
        # number of stems
        ax_stems = core_features.calculate_num_stems_by_type(morph, 2)
        ba_stems = core_features.calculate_num_stems_by_type(morph, 3)
        ap_stems = core_features.calculate_num_stems_by_type(morph, 4)
        self.axon["num_stems"] = ax_stems
        self.dendrite["num_stems"] = ba_stems + ap_stems
        self.basal_dendrite["num_stems"] = ba_stems
        self.apical_dendrite["num_stems"] = ap_stems
        self.all_neurites["num_stems"] = ax_stems + ba_stems + ap_stems
        # max distance of neurite from soma
        ax_dist = core_features.calculate_max_euclidean_distance(morph, 2)
        ba_dist = core_features.calculate_max_euclidean_distance(morph, 3)
        ap_dist = core_features.calculate_max_euclidean_distance(morph, 4)
        d_dist = max(ba_dist, ap_dist)
        n_dist = max(d_dist, ax_dist)
        self.axon["max_euclidean_distance"] = ax_dist
        self.dendrite["max_euclidean_distance"] = d_dist
        self.basal_dendrite["max_euclidean_distance"] = ba_dist
        self.apical_dendrite["max_euclidean_distance"] = ap_dist
        self.all_neurites["max_euclidean_distance"] = n_dist
        #
        sfc = core_features.calculate_soma_surface(morph)
        self.axon["soma_surface"] = sfc
        self.dendrite["soma_surface"] = sfc
        self.basal_dendrite["soma_surface"] = sfc
        self.apical_dendrite["soma_surface"] = sfc
        self.all_neurites["soma_surface"] = sfc
        ################################################################
        # 
        self.axon["relative_soma_depth"] = soma_depth
        self.dendrite["relative_soma_depth"] = soma_depth
        self.basal_dendrite["relative_soma_depth"] = soma_depth
        self.apical_dendrite["relative_soma_depth"] = soma_depth
        self.all_neurites["relative_soma_depth"] = soma_depth
        #
        ################################################################
        ################################################################
        # Axon-specific features
        rot, dist = core_features.calculate_axon_base(morph, soma)
        self.axon["soma_theta"] = rot
        self.dendrite["soma_theta"] = float('nan')
        self.basal_dendrite["soma_theta"] = float('nan')
        self.apical_dendrite["soma_theta"] = float('nan')
        self.all_neurites["soma_theta"] = float('nan')
        self.axon["soma_distance"] = dist
        self.dendrite["soma_distance"] = float('nan')
        self.basal_dendrite["soma_distance"] = float('nan')
        self.apical_dendrite["soma_distance"] = float('nan')
        self.all_neurites["soma_distance"] = float('nan')

    def _calculate(self, morph, soma):
        # calculate the core set of features
        features = self._connection_independent_features(morph, soma)
        # calculate features for the main tree
        #
        moments = core_features.calculate_bifurcation_moments(morph, soma)
        features["first_bifurcation_moment_x"] = moments[0][0]
        features["first_bifurcation_moment_y"] = moments[0][1]
        features["first_bifurcation_moment_z"] = moments[0][2]
        features["bifurcation_stdev_x"] = math.sqrt(moments[1][0])
        features["bifurcation_stdev_y"] = math.sqrt(moments[1][1])
        features["bifurcation_stdev_z"] = math.sqrt(moments[1][2])
        features["bifurcation_skew_x"] = moments[2][0]
        features["bifurcation_skew_y"] = moments[2][1]
        features["bifurcation_skew_z"] = moments[2][2]
        features["bifurcation_kurt_x"] = moments[3][0]
        features["bifurcation_kurt_y"] = moments[3][1]
        features["bifurcation_kurt_z"] = moments[3][2]
        #features["second_bifurcation_moment_x"] = moments[1][0]
        #features["second_bifurcation_moment_y"] = moments[1][1]
        #features["second_bifurcation_moment_z"] = moments[1][2]
        #
        path = core_features.calculate_max_path_distance(morph)
        features["max_path_distance"] = path
        #
        bifs = core_features.calculate_num_bifurcations(morph)
        features["num_bifurcations"] = bifs
        #
        bifs = core_features.calculate_outer_bifs(morph, soma)
        features["num_outer_bifurcations"] = bifs
        #
        branches = core_features.calculate_num_branches(morph)
        features["num_branches"] = branches
        #
        tips = core_features.calculate_num_tips(morph)
        features["num_tips"] = tips
        #
        branch_order = core_features.calculate_max_branch_order(morph)
        features["max_branch_order"] = branch_order
        #
        contraction = core_features.calculate_mean_contraction(morph)
        features["contraction"] = contraction
        #
        num_nodes = morph.num_nodes
        features["num_nodes"] = num_nodes
        # 
        num_neurites = core_features.calculate_num_neurites(morph)
        features["num_neurites"] = num_neurites
        # 
        length = core_features.calculate_total_length(morph)
        features["total_length"] = length
        # 
        pdr = core_features.calculate_mean_parent_daughter_ratio(morph)
        features["mean_parent_daughter_ratio"] = pdr
        #
        frag = core_features.calculate_mean_fragmentation(morph)
        features["mean_fragmentation"] = frag
        #
        remote = core_features.calculate_bifurcation_angle_remote(morph)
        features["bifurcation_angle_remote"] = remote
        ##
        local = core_features.calculate_bifurcation_angle_local(morph)
        features["bifurcation_angle_local"] = local
        #
        pd = core_features.calculate_parent_daughter_ratio(morph)
        features["parent_daughter_ratio"] = pd
        #
        dia = core_features.calculate_mean_diameter(morph)
        features["average_diameter"] = dia
        #
        sfc, vol = core_features.calculate_total_size(morph)
        features["total_surface"] = sfc
        features["total_volume"] = vol
        #
        features["early_branch"] = core_features.calculate_early_branch_path(morph, soma)
        ################################################################
        # derived values
        #
        if branches != float('nan') and branches != 0:
            val = 1.0 * num_neurites / branches
        else:
            val = float('nan')
        features["neurites_over_branches"] = val
        #
        centroid_over_distance(features)
        stdev_over_distance(features)
        centroid_over_stdev(features)

        ########################

        #
        ########################
        #
        return features
        


    def _connection_independent_features(self, morph, soma):
        dims = core_features.calculate_dimensions(morph)
        features = {}
        features["width"] = dims[0]
        features["height"] = dims[1]
        features["depth"] = dims[2]
        #
        moments = core_features.calculate_compartment_moments(morph, soma)
        features["first_compartment_moment_x"] = moments[0][0]
        features["first_compartment_moment_y"] = moments[0][1]
        features["first_compartment_moment_z"] = moments[0][2]
        features["compartment_stdev_x"] = math.sqrt(moments[1][0])
        features["compartment_stdev_y"] = math.sqrt(moments[1][1])
        features["compartment_stdev_z"] = math.sqrt(moments[1][2])
        features["compartment_skew_x"] = moments[2][0]
        features["compartment_skew_y"] = moments[2][1]
        features["compartment_skew_z"] = moments[2][2]
        features["compartment_kurt_x"] = moments[3][0]
        features["compartment_kurt_y"] = moments[3][1]
        features["compartment_kurt_z"] = moments[3][2]
        #
        dims = morph.get_dimensions()
        if dims is not None:
            low = dims[1]
            high = dims[2]
            features["low_x"] = low[0]
            features["low_y"] = low[1]
            features["low_z"] = low[2]
            features["high_x"] = high[0]
            features["high_y"] = high[1]
            features["high_z"] = high[2]
        else:
            features["low_x"] = float('nan')
            features["low_y"] = float('nan')
            features["low_z"] = float('nan')
            features["high_x"] = float('nan')
            features["high_y"] = float('nan')
            features["high_z"] = float('nan')
        #features["second_compartment_moment_x"] = moments[1][0]
        #features["second_compartment_moment_y"] = moments[1][1]
        #features["second_compartment_moment_z"] = moments[1][2]

        return features
