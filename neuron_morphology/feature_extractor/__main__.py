import copy as cp
import logging
import os
import multiprocessing as mp
import functools

import pandas as pd

from argschema import ArgSchemaParser
from ._schemas import InputParameters, OutputParameters

from neuron_morphology.features.default_features import default_features
from neuron_morphology.feature_extractor.feature_extractor import \
    FeatureExtractor
from neuron_morphology.feature_extractor.mark import well_known_marks
from neuron_morphology.swc_io import morphology_from_swc
from neuron_morphology.feature_extractor.data import Data


known_feature_sets = {
    "aibs_default": default_features
}


def load_data(swc_path):
    morphology = morphology_from_swc(swc_path)
    return Data(morphology=morphology)


def build_output_table(outputs):
    table = []
    for reconstruction_id, data in outputs["results"].items():
        current = cp.deepcopy(data["results"])
        current["reconstruction_id"] = reconstruction_id
        table.append(current)
    
    table = pd.DataFrame(table)
    table.set_index("reconstruction_id", inplace=True)
    return table


def write_additional_outputs(outputs, path):
    extension = os.path.splitext(path)[1]

    table = build_output_table(outputs)

    if extension == ".csv":
        logging.warning(
            "writing additional outputs to csv. See output json for "
            "record of selected features and marks"
        )
        table.to_csv(path)

    else:
        raise ValueError(f"unsupported extension: {extension}")


def run_feature_extraction(swc_path, feature_set, only_marks, required_marks):

    try:
        features = known_feature_sets[feature_set]
    except KeyError:
        print(
            f"known feature sets: {list(known_feature_sets.keys())}\n"
            f"you provided: {feature_set}"
        )
        raise

    only_mark_set = {well_known_marks[name] for name in only_marks} \
        if only_marks is not None else None
    required_mark_set = {well_known_marks[name] for name in required_marks} \
        if required_marks is not None else set()

    data = load_data(swc_path)

    extractor = FeatureExtractor(features)
    run = extractor.extract(
        data,
        only_marks=only_mark_set,
        required_marks=required_mark_set
    )

    return swc_path, run.serialize()


def main(
    swc_paths, 
    feature_set, 
    required_marks=None,
    only_marks=None,
    num_processes=None
):
    """
    """

    num_processes = num_processes if num_processes else mp.cpu_count()
    num_processes = min(num_processes, len(swc_paths))

    extract = functools.partial(
        run_feature_extraction, 
        feature_set=feature_set, 
        only_marks=only_marks, 
        required_marks=required_marks
    )

    if num_processes > 1:
        pool = mp.Pool(num_processes)
        mapper = pool.imap_unordered(extract, swc_paths)
    else:
        mapper = (extract(swc_path) for swc_path in swc_paths)

    output = {}
    for swc_path, current_outputs in mapper:
        output[swc_path] = current_outputs

    return output


if __name__ == "__main__":
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    inputs_record = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(inputs_record.pop("log_level"))
    inputs_record.pop("input_json", None)
    inputs_record.pop("output_json", None)
    additional_output_path = inputs_record.pop("additional_output_path", None)

    output = {}
    output.update({"input_parameters": parser.args})
    output.update({"results": main(**inputs_record)})

    if additional_output_path is not None:
        write_additional_outputs(output, additional_output_path)
    
    if "output_json" in parser.args:
        parser.output(output, indent=2)
    else:
        print(parser.get_output_json(output))