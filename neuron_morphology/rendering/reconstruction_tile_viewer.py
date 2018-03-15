import csv
from jinja2 import Environment, PackageLoader, select_autoescape
from neuron_morphology.rendering.reconstruction_grouping import create_reconstruction_grouping


def parse_csv(csv_file):

    with open(csv_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
    return data


def create_tile_viewer(csv_file, html_file, reconstruction_hierarchy, reconstruction_card_properties, max_columns=None):

    env = Environment(loader=PackageLoader('neuron_morphology', 'templates'), autoescape=select_autoescape(['html'
                                                                                                            , 'xml']))
    html_template = env.get_template('reconstruction_card.html')
    data = parse_csv(csv_file)
    reconstruction_grouping = create_reconstruction_grouping(reconstruction_hierarchy, reconstruction_card_properties,
                                                             data)
    reconstruction_card = set().union(item['attribute'] for item in reconstruction_card_properties)
    if max_columns != 'None':
        max_columns = int(max_columns)

    with open(html_file, "w") as htmlfile:
        htmlfile.write(html_template.render(data=[reconstruction_grouping], max_columns=max_columns
                                            , reconstruction_card=reconstruction_card))
