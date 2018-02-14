import argschema as ags
import allensdk.core.json_utilities as ju
import neuron_morphology.features.upright_transform as ut
from shapely.geometry import Polygon


def run_upright_transform():

    soma_path = "7694,2740,7682,2762,7656,2748,7672,2728,7686,2726,7694,2740"
    pia_path = "4992,1982,5326,1676,5672,1456,5906,1302,6044,1234,6396,1112,6872,932,7120,862,7530,760,7882,714,8232,718,8630,752,8732,776,8836,828"
    white_matter_path = "6326,4133,6484,4024,6779,3859,6948,3785,7128,3704,7165,3710,7186,3725,7189,3726,7187,3739"
    soma_coordinates = ut.transform_path_to_coordinates(soma_path)
    pia_coordinates = ut.transform_path_to_coordinates(pia_path)
    white_matter_coordinates = ut.transform_path_to_coordinates(white_matter_path)
    ut.calculate_shortest_distance(soma_coordinates, pia_coordinates, white_matter_coordinates)


def main():

    run_upright_transform()


if __name__ == "__main__":
    main()
