IVSCC Spatial Transformation
============================

For `feature extraction <feature_extraction.html>`_ or visualization, we often need to apply a transformation to the space in which our reconstruction dwells. Some examples:

- **unshrink** : If a neuron is reconstructed from slice, the depth dimension may not scaled equivalently to the width and height dimensions, due to tissue shrinkage. In this case, the neuron must be rescaled along the depth dimension in order for features like compartment volume to be meaningful.
- **upright** : Images of single cortical neurons reconstructed in slice may be rotated arbitrarily. In order to visualize or calculate the symmetry of a neuron's apical dendrites, we must rotate the neuron so that the piaward direction is "up".

The ``neuron_morphology`` repository contains a set of utilities for calculating and applying such transformations. These utilities are ones that we, the Allen Institute, use for processing our in-vitro single cell characterization data (IVSCC, `whitepaper here <http://help.brain-map.org/download/attachments/8323525/CellTypes_Morph_Overview.pdf?version=4&modificationDate=1528310097913&api=v2>`_), but you may also find them handy if your data are similar.

Components
----------

Here are the spatial transform components that we use for our IVSCC data. For each one, we've also included a link to the detailed input and output specification for that executable.

- pia_wm_streamlines (`schema <https://github.com/AllenInstitute/neuron_morphology/blob/dev/neuron_morphology/transforms/pia_wm_streamlines/_schemas.py>`_) : Given 2D linestrings describing the pia and white matter surfaces local to a neuron, calculate a cortical depth field, whose values are the depth between pia and white matter.
- upright_angle (`schema <https://github.com/AllenInstitute/neuron_morphology/blob/dev/neuron_morphology/transforms/upright_angle/_schemas.py>`_) : Given an swc-formatted reconstruction and the outputs of pia_wm_streamlines, find the angle of rotation about the soma which will align the "y" axis of the reconstruction with the piaward direction.
- apply_affine_transform (`schema <https://github.com/AllenInstitute/neuron_morphology/blob/dev/neuron_morphology/transforms/affine_transformer/_schemas.py>`_) : Given a 3D affine transform and an swc-formatted reconstruction, produce a transformed reconstruction also in swc format.


Command-line invocation
-----------------------

Once you have installed ``neuron_morphology``, you can run these utilities from the command line as you would any `argschema module <https://argschema.readthedocs.io/en/latest/>`_. Here is an example:

.. code-block:: bash

    pia_wm_streamlines --input_json path_to_inputs.json --output_json write_outputs_here.json

In this case, the contents of ``path_to_inputs.json`` might look like:

.. code-block:: json

    {
        "pia_path_str": "10.0,1.0,10.0,3.0,9.0,5.0",
        "wm_path_str": ".0,1.0,1.0,3.0,1.0,4.0"
    }

Please see the `schema file <https://github.com/AllenInstitute/neuron_morphology/blob/dev/neuron_morphology/transforms/pia_wm_streamlines/_schemas.py>`_ for more details and options.

Putting it all together
-----------------------

Most likely, you would like to run several of these components in sequence. Here is a `jupyter notebook <_static/nb_name.html>`_ which demonstrates how to do that.