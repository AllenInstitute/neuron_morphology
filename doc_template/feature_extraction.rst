Feature Extraction
==================

Introduction
------------

Morphological features are useful for investigating and clustering neuron morphologies. The Feature Extractor package is designed to allow flexible morpholigcal feature extraction from swc neuron reconstruction files and supplementary data. The default_feature set is a combination of `L-measure <http://cng.gmu.edu:8080/Lm/>`_ and other features used by the Allen Institute.


Running Feature Extraction from the Command Line
-----------------------------------------------

The feature extractor module is an `argschema module <https://argschema.readthedocs.io/en/latest/>`_, which can be run from the command line:

.. code-block:: bash

    feature_extractor --input_json path_to_inputs.json --output_json write_outputs_here.json

Please see the `schema file <https://github.com/AllenInstitute/neuron_morphology/blob/dev/neuron_morphology/feature_extractor/_schemas.py>`_ for usage details and options.


Running in Python/Notebooks
---------------------------

You can take advantage of all of the capabilities of Feature Extractor by running it in python and jupyter notebooks. By running in python and notebooks, you can easily add your own features, create different feature sets, and customize your feature extractor to meet your needs.

Here are two basic examples for running IVSCC and fMOST data:

	* `IVSCC example notebook <_static/IVSCC_features_example.html>`_
	* `fMOST example notebook <_static/fMOST_features_example.html>`_

For a more detailed look at the feature extractor capabilites, checkout `feature_extractor_example <_static/feature_extractor_example.html>`_

