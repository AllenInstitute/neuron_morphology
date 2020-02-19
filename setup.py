from setuptools import setup, find_packages
import glob
import os


version_path = os.path.join(
    os.path.dirname(__file__), 
    "neuron_morphology", 
    "VERSION.txt"
)
with open(version_path, "r") as version_file:
    version = version_file.read().strip()


setup(
    version=version,
    name="neuron_morphology",
    author="Allen Institute for Brain Science",
    author_email="Marmot@AllenInstitute.onmicrosoft.com",
    packages=find_packages(),
    include_package_data=True,
    description="Tools for working with single-neuron morphological reconstructions",
    setup_requires=["pytest-runner"],
    entry_points={
        "console_scripts": [
            "feature_extractor      = neuron_morphology.feature_extractor.__main__:main",
            "layered_point_depths   = neuron_morphology.layered_point_depths.__main__:main",
            "snap_polygons          = neuron_morphology.snap_polygons.__main__:main",
            "apply_affine_transform = neuron_morphology.transforms.affine_transformer.apply_affine_transform:main",
            "pia_wm_streamlines     = neuron_morphology.transforms.pia_wm_streamlines.calculate_pia_wm_streamlines:main",
            "upright_angle          = neuron_morphology.transforms.upright_angle.compute_angle:main",
        ]
    },
    keywords=["neuroscience", "bioinformatics", "scientific"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License", # Allen Institute Software License
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ], 
    install_requires=["numpy"]
)
