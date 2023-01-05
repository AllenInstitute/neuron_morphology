Install
=======

requirements
------------
We support Python 3.8-3.9 on Linux, OSX, and Windows. Similar Python versions (e.g. 3.7-3.10) will probably work, but we don't regularly test using those versions.  Also, the [steamlines] feature set, which is required for doing morphology uprighting requires the fenics-dolfinx package which is not easily available for Windows and so we don't reccomending using Windows if you want those features of this package. 

managing your Python environment
--------------------------------

We recommend installing `neuron_morphology` into a managed Python environment. Having multiple isolated environments lets you install incompatible packages (or different versions of the same package!) simultaneously and prevents unexpected behavior by utilities that rely on the system Python installation.

Two popular tools for managing Python environments are `anaconda <https://anaconda.org/anaconda/anaconda-project>`_ and `venv <https://docs.python.org/3/library/venv.html>`_. The rest of this document assumes that you have created and activated an environment using one of these tools. Using anaconda, this looks like:

.. code-block:: bash

    conda create -y --name environment-name python=3.9
    conda activate environment-name

and using venv:

.. code-block:: bash

    python -m venv path/to/environment
    source path/to/environment/bin/activate

install non pip requirements
----------------------
If you want to utilize the streamlines feature set of this package, which is required to do uprighting and layer aligning morphologies with respect to layers in cortex, for example, then we reccomend installing some requirements via conda. 

.. code-block:: bash

    conda install fenics-dolfinx python-gmsh

NOTE: these packages are not available on conda for Windows, or some older versions of python. 

The rest of the requirements should install fine via pip, or if you don't need these features, you can skip this step. 

installing package
----------------------

We recommend installing `neuron_morphology` via pip:

.. code-block:: bash

    pip install neuron_morphology



installing for development
--------------------------

If you want to work on `neuron_morphology`, you should first clone the repository, then install it in editable mode so that you can easily test your changes:

First do the conda environment and requirements installation described above.

.. code-block:: bash

    git clone https://github.com/alleninstitute/neuron_morphology
    cd neuron_morphology
    pip install -e .

