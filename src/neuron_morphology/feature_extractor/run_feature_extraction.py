from typing import Dict, Any, Tuple, List, Set, Optional, Type
import inspect

from neuron_morphology.features.default_features import default_features
from neuron_morphology.feature_extractor.feature_extractor import \
    FeatureExtractor
from neuron_morphology.feature_extractor.mark import Mark
import neuron_morphology.feature_extractor.mark as _mark
from neuron_morphology.swc_io import morphology_from_swc
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.layer.reference_layer_depths import \
    ReferenceLayerDepths, WELL_KNOWN_REFERENCE_LAYER_DEPTHS
from neuron_morphology.features.layer.layered_point_depths import \
    LayeredPointDepths

"""
    These functions are provided as helper functions for running
    feature extraction on a single neuron_reconstruction.
    run_feature_extraction is used by the main feature_extractor function,
    and must be in a seperate py file due to how Windows
    handles multiprocessing
"""



# this is a little hack to get a look up table for the built-in marks
well_known_marks: Dict[str, Type[Mark]] = {}
for item_name in dir(_mark):
    item = getattr(_mark, item_name)
    if inspect.isclass(item) and issubclass(item, Mark) and not item is Mark:
        well_known_marks[item_name] = item


known_feature_sets = {
    "aibs_default": default_features
}


def resolve_reference_layer_depths(key=None, names=None, boundaries=None):
    """ Given either the name of a well known depths set or a set of names and 
    corresponding boundaries, produce a ReferenceLayerDepths

    Parameters
    ----------
    key : of a well known reference layer
    names : the names of each layer in a custom sequence
    boundaries : the upper and lower depths of each layer in a custom sequence

    Returns
    -------
    the requested reference layer depths

    """

    if key is not None and names is None and boundaries is None:
        return WELL_KNOWN_REFERENCE_LAYER_DEPTHS.get(key)
    elif names is not None and boundaries is not None:
        return ReferenceLayerDepths.sequential(names, boundaries)
    else:
        raise ValueError("unable to construct reference layer depths")


def hydrate_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """ Resolve argued feature parameters to a format comprehensible by 
    the features. e.g. loading data from a path.

    Parameters
    ----------
    parameters : to be hydrated

    Returns
    -------
    The hydrated parameters

    """

    output = {}

    for key in list(parameters.keys()):
        value = parameters[key]

        if key == "layered_point_depths_path":
            output["layered_point_depths"] = LayeredPointDepths.read(value)
        elif key == "reference_layer_depths":
            output["reference_layer_depths"] = \
                resolve_reference_layer_depths(**value)
        else:
            output[key] = value

    return output


def setup_data(
    reconstruction: Dict[str, Any], 
    global_parameters: Dict[str, Any]
) -> Tuple[str, Data]:
    """ Construct a Data for extracting features from a single reconstruction.

    Parameters
    ----------
    reconstruction : The reconstruction to be setup. Must specify an swc_path
    global_parameters : any cross-reconstruction feature parameters

    Returns 
    -------
    identifier : a label for this reconstruction
    data suitable for feature extraction

    """

    parameters: Dict[str, Any] = {}
    identifier = reconstruction.get("identifier", reconstruction.get("swc_path"))
    swc_path = reconstruction.pop("swc_path")
    morphology = morphology_from_swc(swc_path)

    parameters.update(hydrate_parameters(global_parameters))
    parameters.update(hydrate_parameters(reconstruction))

    return identifier, Data(morphology, **parameters)

def run_feature_extraction(
    reconstruction_spec: Dict[str, Any], 
    feature_set: str,
    only_marks: List[str], 
    required_marks: List[str],
    global_parameter_spec: Dict[str, Any]
) -> Tuple[str, Dict]:
    """ Run feature extraction for a single reconstruction.

    Parameters
    ----------
    reconstruction_spec : a dictionary specifying a reconstruction. Must 
        have an swc_path.
    feature_set : names the set of features for which calculation will be 
        attempted
    only_marks : names marks to which calculation will be restricted
    required_marks : raise an exception if these named marks fail validation
    global_parameter_spec : a dictionary specifying cross-reconstruction 
        parameters

    Returns
    -------
    identifier : a label for this reconstruction
    A dict with keys:
        results - a dict, mapping features to calculated values
        selected_marks - the set of marks that passed validation
        selected features - the set of features for which calculation was 
            attempted

    """

    try:
        features = known_feature_sets[feature_set]
    except KeyError:
        print(
            f"known feature sets: {list(known_feature_sets.keys())}\n"
            f"you provided: {feature_set}"
        )
        raise

    only_mark_set: Set[Type[Mark]] = {
        well_known_marks[name] for name in only_marks
        } if only_marks is not None else None
    required_mark_set: Set[Type[Mark]] = {
        well_known_marks[name] for name in required_marks
        } if required_marks is not None else set()

    identifier, data = setup_data(reconstruction_spec, global_parameter_spec)

    extractor = FeatureExtractor(features)
    run = extractor.extract(
        data,
        only_marks=only_mark_set,
        required_marks=required_mark_set
    )

    return identifier, run.serialize()