"""Utilites for writing diagnostic overlay images
"""
import os
import itertools as it
from typing import Sequence, Tuple, Dict, Optional
import copy as cp

import glymur
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import imageio

from neuron_morphology.snap_polygons.geometries import Geometries, make_scale


class ImageOutputter:
    """ Overlays polygons and surfaces on provided images. Writes the 
    results to files.

    Parameters
    ----------
    native_geo : Layer geometries before gaps are filled
    result_geo : Layer geometries after gaps are filled
    image_specs : Each is a dictionary defining a single image. Must 
        provide string keys:
            - input_path : read from here
            - output_path : write to (siblings of) this path
            - downsample : the image will be scaled by this factor in each 
                dimension
            - overlay_types : produce these kinds of overlay for this image
    alpha : of the transparent overlays
    color_cycle : as polygon fills are drawn, cycle through these colors
    savefig_kwargs : Passed directly to pyplot's savefig, use to specify 
        e.g dpi.
    """

    DEFAULT_COLOR_CYCLE = ("c", "m", "y", "k", "r", "g", "b")
    OVERLAY_TYPES = {
        "before": "draw_before",
        "after": "draw_after"
    }

    def __init__(
            self, 
            native_geo: Geometries, 
            result_geo: Geometries, 
            image_specs: Optional[Sequence[Dict]],
            alpha: float = 0.4,
            color_cycle: Optional[Sequence] = None,
            savefig_kwargs: Optional[Dict] = None
    ):

        if color_cycle is None:
            color_cycle = ImageOutputter.DEFAULT_COLOR_CYCLE

        self.native_geo = native_geo
        self.result_geo = result_geo
        self.image_specs = image_specs or []

        self.alpha = alpha
        self.color_cycle = color_cycle
        self.overlay_types = cp.copy(ImageOutputter.OVERLAY_TYPES)

        _savefig_kwargs = {"dpi": 300}
        if savefig_kwargs is not None:
            _savefig_kwargs.update(savefig_kwargs)
        self.savefig_kwargs = _savefig_kwargs

    def _draw_geometries(
            self, 
            geometries: Geometries, 
            image: np.ndarray
    ):
        """ Utility for overlaying polygons and surfaces on an image. See 
        draw_before and draw_after for more details.
        """

        fig, axes = plt.subplots()
        axes.imshow(image)

        cycler = it.cycle(self.color_cycle)
        for color, (name, poly) in zip(cycler, geometries.polygons.items()):
            patch = make_pathpatch(
                poly.exterior.coords, 
                alpha=self.alpha, 
                lw=0.25, 
                label=name, 
                facecolor=color, 
                edgecolor="k"
            )
            axes.add_patch(patch)
        
        for name, surf in geometries.surfaces.items():
            patch = make_pathpatch(
                surf.coords, fill=False, lw=0.25, label=name
            )
            axes.add_patch(patch)

        axes.set_axis_off()
        return fig

    def draw_before(
            self, 
            image: np.ndarray,
            scale: float = 1.0
    ):
        """ Display the pre-fill polygons and surfaces overlaid on an image.

        Parameters
        ----------
        image : onto which objects will be drawn
        scale : required to transform from object space to image space

        Returns
        -------
        A matplotlib figure containing the overlay

        """

        return self._draw_geometries(
            self.native_geo.transform(make_scale(scale)),
            image
        )

    def draw_after(
            self, 
            image: np.ndarray,
            scale: float = 1.0
    ):
        """ Display the post-fill polygons and surfaces overlaid on an image.

        Parameters
        ----------
        image : onto which objects will be drawn
        scale : required to transform from object space to image space

        Returns
        -------
        A matplotlib figure containing the overlay

        """

        return self._draw_geometries(
            self.result_geo.transform(make_scale(scale)),
            image
        )

    def write_images(self):
        """ For each image specified in this outputter and each overlay type
        requested for that image, produce and save an overlay.
        """

        written = []

        for image_spec in self.image_specs:
            image = read_image(
                image_spec["input_path"], 
                image_spec["downsample"]
            )

            for overlay_type in image_spec["overlay_types"]:
                if overlay_type not in self.overlay_types:
                    raise ValueError(
                        f"unrecognized overlay type: {overlay_type} "
                        f"(options: {list(self.overlay_types.keys())})"
                    )

                fig = getattr(
                    self, self.overlay_types[overlay_type]
                )(image, 1.0 / image_spec["downsample"])

                output_path = fname_suffix(
                    image_spec["output_path"], overlay_type)
                write_figure(fig, output_path, **self.savefig_kwargs)
    
                written.append({
                    "input_path": image_spec["input_path"],
                    "downsample": image_spec["downsample"],
                    "output_path": output_path,
                    "overlay_type": overlay_type
                })

        return written


def write_figure(fig: plt.Figure, *args, **kwargs):
    """ Write a matplotlib figure without respect to the current figure.

    Parameters
    ----------
    fig : the figure to be writter    
    *args, **kwargs : passed to plt.savefig

    """

    cf_number = plt.gcf().number
    plt.figure(fig.number)
    plt.savefig(*args, **kwargs)
    plt.figure(cf_number)


def read_image(path: str, decimate: int = 1):
    """ Read an image. Dispatch to an appropriate library based on that 
    image's extension.

    Parameters
    ----------
    path : to the image
    decimate : apply a decimation of this factor along each axis of the image

    """

    _, ext = os.path.splitext(path)

    if ext == ".jp2":
        return read_jp2(path, decimate)
    else:
        return read_with_ndimage(path, decimate)


def read_with_ndimage(path: str, decimate: int):
    """Read (and symmetrically decimate) an image file into a numpy array
    """
    return imageio.imread(path)[::decimate, ::decimate, ...]


def read_jp2(path: str, decimate: int):
    """Read (and symmetrically decimate) a jp2 file into a numpy array 
    """
    fil = glymur.Jp2k(path)
    return fil[::decimate, ::decimate]


def fname_suffix(path: str, suffix: str):
    """ Utility for adding a suffix to a path string. The suffix will be 
    inserted before the extension.
    """

    head, ext = os.path.splitext(path)
    if ext == "":
        return f"{head}_{suffix}"
    else:
        return f"{head}_{suffix}{ext}"

    
def make_pathpatch(
        vertices: Sequence[Tuple[float, float]], 
        **patch_kwargs
) -> mpl.patches.PathPatch:
    """ Utility for building a matplotlib pathpatch from an array of vertices

    Parameters
    ----------
    vertices : Defines the path. May be closed or open
    **patch_kwargs : passed directly to pathpatch constructor

    """

    codes = [mpl.path.Path.MOVETO] \
        + [mpl.path.Path.LINETO] * (len(vertices) - 1)
    path = mpl.path.Path(vertices, codes)
    return mpl.patches.PathPatch(path, **patch_kwargs)
