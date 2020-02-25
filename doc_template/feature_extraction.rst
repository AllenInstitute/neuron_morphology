Feature Extraction
==================

Introduction
-------

The Feature Extractor package is designed to allow flexible feature extraction from swc files and additional data.


Running Feature Extraction from the Command Line
-----------------------------------------------

The feature extractor module is an `argschema module <https://argschema.readthedocs.io/en/latest/>`_, which can be run from the command line:

.. code-block:: bash

    feature_extractor --input_json path_to_inputs.json --output_json write_outputs_here.json

Please see the `schema file <https://github.com/AllenInstitute/neuron_morphology/blob/dev/neuron_morphology/feature_extractor/_schemas.py>`_ for usage details and options.


Running in Python/Notebooks
---------------------------

You can take advantage of all of the capabilities of Feature Extractor by running it in python and jupyter notebooks. 

Here are two basic examples for running IVSCC and fMOST data:

	* `IVSCC example notebook <_static/IVSCC_features_example.html`_
	* `fMOST example notebook <_static/fMOST_features_example.html`_

For a more detailed look at the feature extractor capabilites, checkout `feature_extractor_example <static/feature_extractor_example.html>`_

