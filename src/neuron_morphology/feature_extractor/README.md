Morphology Feature Extractor
============================

This is a tool for calculating morphological features (see neuron_morphology.features for options) of single-neuron reconstructions. You can use this tool as-is from the command line, or import it into your own code. This tool supports [swc-formatted](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html) reconstructions, such as those in the free, publically available [Allen Cell Types Database](http://celltypes.brain-map.org/).

Command Line Use
----------------

In order to use this tool on the command line, you must first install the neuron_morphology package (we suggest using a virtualenv or conda environement). Then you should create a `.json` file like this one:

```
contents of my_inputs.json:
{
    "reconstructions": [
        {
            "swc_path": "path/to/an.swc"
        },
        {
            "swc_path": "path/to/another.swc"
        }
    ],
    "output_table_path": "path/for/output_table.csv",
    "heavy_output_path": "some_path.h5"
}
```

This file specifies the inputs, parameters, and outputs of this feature extraction job. Some key components:
- reconstructions : this is where we point the extractor at swc files. We can also pass in reconstruction-specific parameters here
- heavy_output_path : This is where any large-scale outputs (e.g. layer histogram arrays) will be written.
- output_table_path : if this optional parameter is provided, a reconstructions X features csv will be written here.

then run:
```
python -m neuron_morphology.feature_extractor --input_json my_inputs.json --output_json my_outputs.json
```

See the [schema definition](./_schemas.py) for a full list of parameters.

Library Use
-----------
You can also import the feature extractor and use it to build your own tools (and register custom features!). Please see [the example notebook](../../notebooks/feature_extractor_example.ipynb) for more guidance.