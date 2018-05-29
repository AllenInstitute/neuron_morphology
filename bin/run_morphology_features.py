#!/usr/bin/python

import argschema as ags
from neuron_morphology._schemas import MorphologyFeatureParameters
import allensdk.core.json_utilities as ju
import neuron_morphology.swc_io as swc
import neuron_morphology.features.feature_extractor as fe
from neuron_morphology.constants import *


def run_morphology_features(pia_transform, swc_file, relative_soma_depth):

    morphology = swc.tree_from_swc(swc_file)
    transformed_morphology = apply_affine(morphology, pia_transform)
    data = calculate_morphology_features(transformed_morphology, relative_soma_depth)
    return data


def calculate_morphology_features(morphology, relative_soma_depth):

    data = {'axon_features': fe.FeatureExtractor(morphology, [AXON], relative_soma_depth).features,
            'axon_cloud_features': fe.FeatureExtractor(morphology, [AXON], relative_soma_depth).features,
            'dendrite_features': fe.FeatureExtractor(morphology, [APICAL_DENDRITE, BASAL_DENDRITE],
                                                     relative_soma_depth).features,
            'apical_dendrite_features': fe.FeatureExtractor(morphology, [APICAL_DENDRITE],
                                                            relative_soma_depth).features,
            'basal_dendrite_features': fe.FeatureExtractor(morphology, [BASAL_DENDRITE], relative_soma_depth).features,
            'all_neurites_features': fe.FeatureExtractor(morphology, [AXON, APICAL_DENDRITE, BASAL_DENDRITE],
                                                         relative_soma_depth).features}

    # make output of new module backwards compatible with previous module
    md = {}
    feat = {"number_of_stems": data["dendrite"]["num_stems"],
            "max_euclidean_distance": data["dendrite"]["max_euclidean_distance"],
            "max_path_distance": data["dendrite"]["max_path_distance"], "overall_depth": data["dendrite"]["depth"],
            "total_volume": data["dendrite"]["total_volume"],
            "average_parent_daughter_ratio": data["dendrite"]["mean_parent_daughter_ratio"],
            "average_diameter": data["dendrite"]["average_diameter"], "total_length": data["dendrite"]["total_length"],
            "overall_width": data["dendrite"]["width"], "number_of_nodes": data["dendrite"]["num_nodes"],
            "average_bifurcation_angle_local": data["dendrite"]["bifurcation_angle_local"],
            "number_of_bifurcations": data["dendrite"]["num_bifurcations"],
            "average_fragmentation": data["dendrite"]["mean_fragmentation"],
            "number_of_tips": data["dendrite"]["num_tips"], "average_contraction": data["dendrite"]["contraction"],
            "average_bifuraction_angle_remote": data["dendrite"]["bifurcation_angle_remote"],
            "number_of_branches": data["dendrite"]["num_branches"], "total_surface": data["dendrite"]["total_surface"],
            "max_branch_order": data["dendrite"]["max_branch_order"], "soma_surface": data["dendrite"]["soma_surface"],
            "overall_height": data["dendrite"]["height"]}

    md["features"] = feat
    data["morphology_data"] = md
    return data


def apply_affine(morphology, pia_transform):
    aff = []
    for i in range(12):
        aff.append(pia_transform["tvr_%02d" % i])

    transformed_morphology = morphology.apply_affine(aff)
    return transformed_morphology


def main():

    module = ags.ArgSchemaParser(schema_type=MorphologyFeatureParameters)
    data = run_morphology_features(module.args["pia_transform"],
                                   module.args["swc_file"],
                                   module.args["relative_soma_depth"])

    ju.write(module.args["output_json"], data)


if __name__ == "__main__":
    main()
