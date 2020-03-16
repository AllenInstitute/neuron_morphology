import pandas as pd
from neuron_morphology.morphology import Morphology


SWC_COLUMNS = ('id', 'type', 'x', 'y', 'z', 'radius', 'parent',)
COLUMN_CASTS = {
    'id': int,
    'parent': int,
    'type': int
}


def read_swc(path, columns=SWC_COLUMNS, sep=' ', casts=COLUMN_CASTS):

    """ Read an swc file into a pandas dataframe
    """

    df = pd.read_csv(path, names=columns, comment='#', sep=sep)
    apply_casts(df, casts)
    return df


def write_swc(data, path, comments=None, sep=' ', columns=SWC_COLUMNS, casts=COLUMN_CASTS):

    """ Write an swc file from a pandas dataframe
    """

    if comments is None:
        comments = []
    comments = ['# ' + comment + '\n' for comment in comments]

    apply_casts(data, casts)

    data = data[[col for col in columns]]
    with open(path, 'w') as swc_file:
        swc_file.writelines(comments)
    data.to_csv(path, sep=sep, index=False, header=None, mode='a')


def apply_casts(df, casts):

    for key, typ in casts.items():
        df[key] = df[key].astype(typ)


def morphology_from_swc(swc_path):

    swc_data = read_swc(swc_path, sep=' ')

    nodes = swc_data.to_dict('record')
    for node in nodes:
        # unfortunately, pandas automatically promotes numeric types to float in to_dict
        node['parent'] = int(node['parent'])
        node['id'] = int(node['id'])
        node['type'] = int(node['type'])

    return Morphology(
        nodes,
        node_id_cb=lambda node: node['id'],
        parent_id_cb=lambda node: node['parent']
    )

def morphology_to_swc(morphology, swc_path, comments=None):
    """
        Write an swc file from a morphology object
    """

    df = pd.DataFrame(morphology.nodes())
    write_swc(df, swc_path, comments=comments)
