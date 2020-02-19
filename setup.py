from setuptools import setup, find_packages
import glob
import os


scripts = glob.glob(os.path.join('bin', '*'))

version_path = os.path.join(
    os.path.dirname(__file__), 
    "neuron_morphology", 
    "VERSION.txt"
)
with open(version_path, "r") as version_file:
    version = version_file.read().strip()

setup(
    version=version,
    name='neuron_morphology',
    author='Allen Institute for Brain Science',
    author_email='marmot@alleninstitute.org',
    packages=find_packages(),
    include_package_data=True,
    scripts=scripts,
    description='Neuron morphology analysis and visualization tools',
    setup_requires=['pytest-runner'],
    entry_points={
        "console_scripts": [
            "feature_extractor=neuron_morphology.feature_extractor.__main__:main",
            "layered_point_depths=neuron_morphology.layered_point_depths.__main__:main",
        ]
    },
    keywords=['neuroscience', 'bioinformatics', 'scientific'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License', # Allen Institute Software License
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
        ], install_requires=['numpy'])
