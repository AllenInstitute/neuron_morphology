Overview
========


Morphological reconstructions
-----------------------------
The package supports reconstructions in the `SWC <http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html>`_ file format
such as those in the `Allen Cell Types Database <http://celltypes.brain-map.org>`_, `Neuro Morpho <http://neuromorpho.org/>`_ or fMOST.


Predefined morphological features
---------------------------------
The package can calculate a set of morphological features as listed below:

TODO:Need to list a table of feature, description and a corresponding calling function

Generally, morphological features are of two kinds: intrinsic that are invariant under coordinate
transformation (such as affine transformation) or extrinsic that may change under some of the transformation.


TODO:link to example notebook here


Transformations
---------------

The package also provides tools for performing a set of coordinate transformations needed as a preprocessing step before extracting extrinsic features.

TODO:link to example notebook here


User-defined morphological features
-----------------------------------
Additionally users may specify custom features to be include as a feature extraction set.

TODO:link to example notebook here


Data processing pipeline
------------------------
The package is designed to support the processing pipeline of
Allen Institute's morphological reconstruction data `whitepaper <http://help.brain-map.org/download/attachments/8323525/CellTypes_Morph_Overview.pdf>`_.
If you have a question about these data, you can ask it on our `community forum <https://community.brain-map.org>`_

