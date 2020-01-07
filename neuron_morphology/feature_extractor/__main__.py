import copy as cp
import logging

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


def main(
    swc_paths, 
    feature_set, 
    additional_output_path=None,
    required_marks=None,
    only_marks=None
):
    """
    """

    try:
        features = known_feature_sets[feature_set]
    except KeyError:
        print(
            f"known feature sets: {list(known_feature_sets.keys())}\n"
            f"you provided: {feature_set}"
        )
        raise

    only_mark_set = {well_known_marks[name] for name in only_marks} if only_marks is not None else None
    required_mark_set = {well_known_marks[name] for name in required_marks} if required_marks is not None else set()
    

    output = {}
    for swc_path in swc_paths:

        data = load_data(swc_path)

        extractor = FeatureExtractor(features)
        run = extractor.extract(
            data,
            only_marks=only_mark_set,
            required_marks=required_mark_set
        )
        output[swc_path] = run.serialize()

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

    output = {}
    output.update({"input_parameters": parser.args})
    output.update({"results": main(**inputs_record)})
    
    if "output_json" in parser.args:
        parser.output(output, indent=2)
    else:
        print(parser.get_output_json(output))