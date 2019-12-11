#!/usr/bin/python

from timeit import default_timer as timer

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections as mc
from scipy.spatial import voronoi_plot_2d

import argparse
import allensdk.core.json_utilities as ju
from neuron_morphology.transforms.upright_transform import (
    UprightTransform, convert_coords_str)


def plot_upright_input(filename):
    jin = ju.read(filename)

    soma_coords_str = jin['primary']['Soma']['path']
    pia_coords_str = jin['primary']['Pia']['path']
    wm_coords_str = jin['primary']['White Matter']['path']

    soma_coords = convert_coords_str(soma_coords_str)
    pia_coords = convert_coords_str(pia_coords_str)
    wm_coords = convert_coords_str(wm_coords_str)

    sx = soma_coords['x'].mean()
    sy = soma_coords['y'].mean()

    fig, ax = plt.subplots()

    ax.plot(soma_coords['x'], soma_coords['y'])
    ax.plot(pia_coords['x'], pia_coords['y'])
    ax.plot(wm_coords['x'], wm_coords['y'])
    ax.legend(['soma', 'pia', 'wm'])

    # plt.show()
    start = timer()
    T, v_diagram, mid_line, min_proj, theta = UprightTransform.from_coords_str(
        soma_coords_str, pia_coords_str, wm_coords_str)
    end = timer()
    print(end - start)

    lc = mc.LineCollection(mid_line)
    ax.add_collection(lc)

    ax.arrow(sx, sy, min_proj[0] - sx, min_proj[1] - sy)

    fig, ax = plt.subplots()

    soma_coords_t = transform_coords(soma_coords, T)
    ax.plot(soma_coords_t[:, 0], soma_coords_t[:, 1])
    pia_coords_t = transform_coords(pia_coords, T)
    ax.plot(pia_coords_t[:, 0], pia_coords_t[:, 1])
    wm_coords_t = transform_coords(wm_coords, T)
    ax.plot(wm_coords_t[:, 0], wm_coords_t[:, 1])
    ax.legend(['soma', 'pia', 'wm'])

    voronoi_plot_2d(v_diagram)

    print('Theta (rad): ', theta)
    print('Theta (deg): ', np.degrees(theta))
    print(T.to_dict())
    plt.show()


def transform_coords(coords, T):
    n_coords = coords['x'].shape[0]
    array = np.hstack((coords['x'].reshape((n_coords, 1)),
                       coords['y'].reshape((n_coords, 1)),
                       np.zeros((n_coords, 1))))
    return T.transform(array.T).T


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name')
    args = parser.parse_args()
    plot_upright_input(args.file_name)

if __name__ == '__main__':
    main()
