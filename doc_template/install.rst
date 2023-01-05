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

installing from github
----------------------

If you want to install a specific branch, tag, or commit of `neuron_morphology`, you can do so using pip:

.. code-block:: bash

    pip install neuron_morphology

The *dev* branch contains cutting-edge features that might not have been formally released yet. By installing this way, you can access those features.

installing for development
--------------------------

If you want to work on `neuron_morphology`, you should first clone the repository, then install it in editable mode so that you can easily test your changes:

.. code-block:: bash

    git clone https://github.com/alleninstitute/neuron_morphology
    cd neuron_morphology

    conda install -c conda-forge "fenics-dolfinx>=0.4.2" # optional for using streamlines
    pip install gmsh # optional for using streamlines; note that certain platforms (e.g. Centos) may need to install from source
    pip install -r requirements.txt -U
    pip install -r test_requirements.txt -U

    pip install -e .


installing from conda-forge [coming soon!]
------------------------------------------
To install using conda (, run

.. code-block:: bash

    conda install -c conda-forge -y neuron_morphology

This method is preferred vs. pip, since some subpackages of `neuron_morphology` depend on 3rd party packages which don't pip install well on all major platforms. Note that this use of conda as a *package* manager does not require or depend on using conda as your *environment* manager
