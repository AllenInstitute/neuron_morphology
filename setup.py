from setuptools import setup, find_packages


setup(
    version='0.2.4',
    name='allensdk_neuron_morphology',
    author='Keith Godfrey, Nike Keller',
    author_email='keithg@alleninstitute.org, nikah@alleninstitute.org',
    packages=find_packages(),
    package_data={'': ['*.conf', '*.cfg', '*.md', '*.json', '*.dat', '*.env', '*.sh', '*.txt', 'bps', 'Makefile', 'COPYING'] },
    include_package_data=True,
    description='Neuron morphology analysis and visualization tools',
    install_requires=['scipy>=0.14.0', 'numpy>=1.8.2'],
    tests_require=['pytest>=2.6.3',
                   'pytest-cov>=2.2.1',
                   'pytest-cover>=3.0.0',
                   'pytest-mock>=0.11.0',
                   'pytest-pep8>=1.0.6',
                   'coverage>=3.7.1',
                   'mock>=1.0.1'],
    setup_requires=['setuptools', 'sphinx', 'numpydoc'],
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
