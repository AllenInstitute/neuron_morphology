import numpy as np


def plot_morphology_xy(morphology, ax):

    nodes = morphology.nodes()
    x = [node['x'] for node in nodes]
    y = [node['y'] for node in nodes]

    ax.scatter(x, y, s=0.1, color="k")
    ax.set_aspect('equal')


def plot_morphology_zy(morphology, ax):

    nodes = morphology.nodes()
    y = [node['y'] for node in nodes]
    z = [node['z'] for node in nodes]

    ax.scatter(z, y, s=0.1, color="k")
    ax.set_aspect('equal')


def plot_cortical_boundary(pia_coords, wm_coords, ax):
    ax.plot(pia_coords['x'], pia_coords['y'], color="orange")
    ax.plot(wm_coords['x'], wm_coords['y'], color="blue")
    return ax


def plot_soma(soma_center, ax):
    ax.scatter(soma_center[0], soma_center[1], s=10, color="r")


def plot_depth_field(depth_field,ax):

    x = depth_field.x
    y = depth_field.y
    X, Y = np.meshgrid(x, y, indexing='ij')

    vals = depth_field.values

    ax.contourf(X, Y, vals)
    ax.set_aspect('equal')

def plot_gradient_field(gradient_field,ax):
    step = 100
    gradient_ds = gradient_field[::step, ::step, :]

    x = gradient_ds.x
    y = gradient_ds.y
    vals = gradient_ds.values
    X, Y = np.meshgrid(x, y, indexing='ij')
    ax.quiver(X, Y, vals[:, :, 0].flatten(), vals[:, :, 1].flatten())

