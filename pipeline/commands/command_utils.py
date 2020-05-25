import os

import matplotlib.pyplot as plt
import boto3

from neuron_morphology.morphology import Morphology
from neuron_morphology.swc_io import (morphology_from_swc, morphology_to_swc)


s3 = boto3.client("s3")


def collect_morphology(bucket: str,
                       swc_key: str):
    swc_response = s3.get_object(Bucket=bucket,
                                 Key=swc_key,
                                 )
    return morphology_from_swc(swc_response["Body"])


def morphology_to_s3(bucket: str, key: str, morphology: Morphology):
    """Store morphology in an s3 bucket as swc

    Parameters
    ----------
    bucket : name of the bucket in which to store this dataset
    key : at which to store the dataset
    morphology : The morphology to store

    Returns
    -------
    key : the argued key

    Notes
    -----
    we must write morphology to "disk" temporarily and send that.
    """
    tmp_path = key.split("/")[-1]
    morphology_to_swc(morphology, tmp_path)

    s3.upload_file(Filename=tmp_path, Bucket=bucket, Key=key)
    os.remove(tmp_path)
    return key


def morphology_png_to_s3(bucket: str,
                         key: str,
                         morphology: Morphology):

    tmp_path = key.split("/")[-1]

    nodes = morphology.nodes()
    x = [node['x'] for node in nodes]
    y = [node['y'] for node in nodes]
    z = [node['z'] for node in nodes]

    fig, ax = plt.subplots(1, 2)
    ax[0].scatter(x, y, s=0.1)
    ax[0].set_title('x-y view')
    ax[1].scatter(z, y, s=0.1)
    ax[1].set_title('z-y view')
    fig.suptitle(tmp_path[:-4], fontsize=16)
    fig.savefig(tmp_path)

    s3.upload_file(Filename=tmp_path, Bucket=bucket, Key=key)
    os.remove(tmp_path)
    return key
