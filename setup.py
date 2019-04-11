from setuptools import setup, find_packages
import glob
import os


scripts = glob.glob(os.path.join('bin', '*'))


setup(
    version='0.3.0',
    name='allensdk_neuron_morphology',
    author='Nika Keller, Keith Godfrey',
    author_email='nikah@alleninstitute.org',
    packages=find_packages(),
    include_package_data=True,
    scripts=scripts,
    description='Neuron morphology analysis and visualization tools',
    setup_requires=['pytest-runner'],
    entry_points={
          'console_scripts': [
              'allensdk.neuron_morphology = allensdk.neuron_morphology.__main__:main'
            ]
    },
    keywords=['neuroscience', 'bioinformatics', 'scientific'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
        ], install_requires=['numpy'])
