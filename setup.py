from setuptools import setup, find_packages
import glob
import os


scripts = glob.glob(os.path.join('bin', '*'))

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

with open('requirements_test.txt', 'r') as f:
    requirements_test = f.read().splitlines()

setup(
    version='0.2.4',
    name='allensdk_neuron_morphology',
    author='Nike Keller, Keith Godfrey',
    author_email='nikah@alleninstitute.org',
    packages=find_packages(),
    include_package_data=True,
    scripts=scripts,
    description='Neuron morphology analysis and visualization tools',
    install_requires=requirements,
    tests_require=requirements_test,
    setup_requires=['setuptools', 'sphinx', 'numpydoc'],
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
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
        ])
