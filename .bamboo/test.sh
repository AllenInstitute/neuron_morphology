#!/usr/bin/env bash

set -eu
export PATH=/shared/utils.x86_64/anaconda2-4.3.1/bin:$PATH
export HOME=${bamboo_build_working_directory}/.home
export TMPDIR=${bamboo_build_working_directory}
export CONDA_PATH_BACKUP=${CONDA_PATH_BACKUP:-$PATH}
export CONDA_PREFIX=${CONDA_PREFIX:-}
export CONDA_PS1_BACKUP=${CONDA_PS1_BACKUP:-}
CONDA_TEST_ENV_PREFIX=${bamboo_build_working_directory}/.conda/${bamboo_TEST_ENVIRONMENT}
if [ -d ${CONDA_TEST_ENV_PREFIX} ]; then
    conda remove -y -${bamboo_VERBOSITY} --prefix ${CONDA_TEST_ENV_PREFIX} --all
fi
conda create -y -${bamboo_VERBOSITY} --clone ${bamboo_BASE_ENVIRONMENT} --prefix ${CONDA_TEST_ENV_PREFIX}
source activate ${bamboo_build_working_directory}/.conda/${bamboo_TEST_ENVIRONMENT}
cd ${bamboo_build_working_directory}/${bamboo_CHECKOUT_DIRECTORY}
conda install -y virtualenv
pip install tox
tox
source deactivate
