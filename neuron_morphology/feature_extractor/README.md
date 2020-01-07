Morphology Feature Extractor
============================

This is a tool for calculating morphological features (see neuron_morphology.features for options) of single-neuron reconstructions. You can use this tool as-is from the command line, or import it into your own code. This tool supports [swc-formatted](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html) reconstructions, such as those in the free, publically available [Allen Cell Types Database](http://celltypes.brain-map.org/).

Command Line Use
----------------

In order to use this tool on the command line, you must first install the neuron_morphology package (we suggest using a virtualenv or conda environement). Then run:
```
python -m neuron_morphology.feature_extractor --swc_paths "['path/to/an.swc', 'path/to/another.swc']" --output_json my_outputs.json
```

Note that the swc paths need to be passed in as a Python-style list literal.

For convenience, you can also get outputs as a csv whose rows are individual neurons and whose columns are features:
```
python -m neuron_morphology.feature_extractor --swc_paths "['path/to/an.swc', 'path/to/another.swc']" --output_json my_outputs.json --additional_output_path my_output_table.csv
```

This is rapidly becoming a long command! You can write the inputs to a json, like such:

```
contents of my_inputs.json:
{
    "swc_paths": [
        "path/to/an.swc",
        "path/to/another.swc"
    ],
    "additional_output_path": "path/for/output_table.csv"
}
```

then run:
```
python -m neuron_morphology.feature_extractor --input_json my_inputs.json --output_json my_outputs.json
```

See the [schema definition](./_schemas.py) for a full list of parameters.

Library Use
-----------
You can also import the feature extractor and use it to build your own tools (and register custom features!). Please see [the example notebook](../../notebooks/feature_extractor_example.ipynb) for more guidance.