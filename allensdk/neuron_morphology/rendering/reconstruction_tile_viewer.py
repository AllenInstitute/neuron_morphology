import csv
from jinja2 import Environment, select_autoescape, FileSystemLoader
from allensdk.neuron_morphology.rendering.reconstruction_grouping import create_reconstruction_grouping
import os


def parse_csv(csv_file):

    """Parses the csv file and creates a dict from the data.

    :parameter csv_file: string
            path to csv file.
    :return data: dict
            dictionary that is constructed from the csv file.
    """

    with open(csv_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
    return data


def create_tile_viewer(csv_file, html_file, reconstruction_hierarchy, reconstruction_card_properties, max_columns=None):

    """Creates a viewer that has reconstruction cards.

    :parameter csv_file: string
                path to a csv file that has the data that is displayed by the viewer.
    :parameter html_file: string
                path to a html file that is created from the data in the csv file.
    :parameter reconstruction_hierarchy: list of dicts
                columns in the csv file that are used to group the reconstructions.
    :parameter reconstruction_card_properties: list of dicts
                columns in the csv file that is displayed in the reconstruction card.
    :parameter max_columns: string
                number of reconstructions to display in each row. Can be None. If None, it displays all the
                reconstructions in one row
    :return: None
    """

    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html', 'xml']))

    html_template = env.get_template('reconstruction_card.html')
    data = parse_csv(csv_file)
    reconstruction_grouping = create_reconstruction_grouping(reconstruction_hierarchy, reconstruction_card_properties,
                                                             data)
    reconstruction_card = set().union(item['attribute'] for item in reconstruction_card_properties)
    if max_columns:
        max_columns = int(max_columns)

    with open(html_file, "w") as htmlfile:
        htmlfile.write(html_template.render(data=[reconstruction_grouping], max_columns=max_columns
                                            , reconstruction_card=reconstruction_card))
