import copy as cp
import logging
import multiprocessing as mp
import functools
from typing import Dict, Any, Tuple, List, Set, Optional, Type

from argschema import ArgSchemaParser

from neuron_morphology.feature_extractor._schemas import (
    InputParameters, OutputParameters)

from neuron_morphology.feature_extractor.run_feature_extraction import \
    run_feature_extraction

from neuron_morphology.feature_extractor.feature_writer import (
    FeatureWriter, DEFAULT_FEATURE_FORMATTERS)


def extract_multiple(
    reconstructions: List[Dict[str, Any]], 
    feature_set: str,
    heavy_output_path: str,
    required_marks: Optional[List[str]] = None,
    only_marks: Optional[List[str]] = None,
    num_processes: Optional[int] = None,
    global_parameters: Optional[Dict[str, Any]] = None,
    output_table_path: Optional[str] = None
):
    """ For each path in swc_paths, load the file into a morphology and (attempt 
    to) extract each feature in the set specified by feature_set.

    Because of how Windows handles multiprocessing, run_feature_extraction
    must be in another py file.

    Parameters
    ----------
    reconstructions : specify the reconstructions on which to compute features
    feature_set : names the set of features for which calculation will be
        attempted
    heavy_output_path : write "heavy" outputs, such as arrays, to this h5 file
    only_marks : names marks to which calculation will be restricted
    required_marks : raise an exception if these named marks fail validation
    num_processes : use this many cores in the multiprocessing pool.
    global_parameters : a dictionary specifying cross-reconstruction
        parameters
    output_table_path : if not none, write a flattened table of features here

    Returns
    -------
    a dictionary whose keys are reconstruction identifers and whose values are
        the outputs of run_feature_extraction for those reconstructions.

    """

    num_processes = num_processes if num_processes else mp.cpu_count()
    num_processes = min(num_processes, len(reconstructions))

    global_parameters = {} if global_parameters is None else global_parameters

    extract = functools.partial(
        run_feature_extraction,
        feature_set=feature_set,
        only_marks=only_marks,
        required_marks=required_marks,
        global_parameter_spec=global_parameters
    )

    if num_processes > 1:
        pool = mp.Pool(num_processes)
        mapper = pool.imap_unordered(extract, reconstructions)
    else:
        mapper = (extract(morph) for morph in reconstructions) # type: ignore[assignment]

    writer = FeatureWriter(
        heavy_output_path,
        output_table_path,
        formatters=DEFAULT_FEATURE_FORMATTERS
    )

    for identifier, run in mapper:
        writer.add_run(identifier, run)

    return writer.write()


def main():
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    inputs_record = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(inputs_record.pop("log_level"))
    inputs_record.pop("input_json", None)
    inputs_record.pop("output_json", None)
    output_table_path = inputs_record.pop("output_table_path", None)
    
    output = {}
    output.update({"inputs": parser.args})
    output.update({"results": extract_multiple(**inputs_record)})

    parser.output(output)


if __name__ == "__main__":
    main()