import csv
from jinja2 import Environment, select_autoescape, FileSystemLoader
from neuron_morphology.rendering.reconstruction_grouping import create_reconstruction_grouping
import os
import sys
import imghdr


def parse_csv(csv_file):

    """ Parses the csv file and creates a dict from the data

        Parameters
        ----------

        csv_file: string
            Path to csv file

        Returns
        -------

        data: dict
            Dictionary that is constructed from the csv file

    """

    with open(csv_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
    return data


def get_template_path(template_dir_name):

    """ Gets the jinja2 template directory path. This function is necessary for running this module in a bundle.
        PyInstaller creates a temp folder and stores the path in sys._MEIPASS when this package is bundled.
        When not run in the bundle, the path is the template folder in the current directory

        Parameters
        ----------

        template_dir_name: string
            Name of the template directory

        Returns
        -------

        Path to the template directory

    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, template_dir_name)


def is_thumbnail(key, value):

    """ Determines if the key and value of a dictionary item is a thumbnail

        Parameters
        ----------

        key: string
        value: string

        Returns
        -------

        True or False: boolean

    """

    if not type(value) is str:
        return False

    is_thumbnail = False
    if key.endswith('thumbnail'):
        is_thumbnail = True
    elif os.path.isfile(value) and imghdr.what(value):
        is_thumbnail = True

    return is_thumbnail


def create_tile_viewer(csv_file, reconstruction_hierarchy, reconstruction_card_properties, max_columns=None):

    """ Creates a viewer that has reconstruction cards

        Parameters
        ----------

        csv_file: string
            Path to a csv file that has the data that is displayed by the viewer

        reconstruction_hierarchy: list of dicts
            Columns in the csv file that are used to group the reconstructions

        reconstruction_card_properties: list of dicts
            Columns in the csv file that is displayed in the reconstruction card

        max_columns: string
            Number of reconstructions to display in each row. Can be None. If None, it displays all the
            reconstructions in one row

        Returns
        -------

        html: string
            Object that can be saved as an html file

    """

    template_dir = get_template_path('templates')
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html', 'xml']))
    env.filters['is_thumbnail'] = is_thumbnail
    html_template = env.get_template('reconstruction_card.html')
    data = parse_csv(csv_file)
    reconstruction_grouping = create_reconstruction_grouping(reconstruction_hierarchy, reconstruction_card_properties,
                                                             data)
    reconstruction_card = [item['attribute'] for item in reconstruction_card_properties]
    if max_columns:
        max_columns = int(max_columns)

    html = html_template.render(data=[reconstruction_grouping], max_columns=max_columns,
                                reconstruction_card=reconstruction_card)
    return html
