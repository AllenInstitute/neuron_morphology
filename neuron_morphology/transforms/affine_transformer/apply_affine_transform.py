import sys

from argschema import ArgSchemaParser

from neuron_morphology.swc_io import morphology_from_swc, morphology_to_swc
from neuron_morphology.transforms.affine_transformer._schemas import (
    ApplyAffineSchema, OutputParameters)
from neuron_morphology.transforms.affine_transform import AffineTransform


def main():
    mod = ArgSchemaParser(schema_type=ApplyAffineSchema,
                          output_schema_type=OutputParameters)
    args = mod.args

    if 'affine_dict' in args:
        affine_transform = AffineTransform.from_dict(args['affine_dict'])
    elif 'affine_list' in args:
        affine_transform = AffineTransform.from_list(args['affine_list'])
    else:
        raise ValueError('must provide either an affine_dict or affine_list')

    morph_in = morphology_from_swc(args['input_swc'])

    morph_out = affine_transform.transform_morphology(morph_in)

    morphology_to_swc(morph_out, args['output_swc'])

    output = {
        'inputs': args,
        'transformed_swc': args['output_swc'],
    }

    mod.output(output)


if __name__ == '__main__':
    main()
