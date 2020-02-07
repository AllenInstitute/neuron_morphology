import os

import marshmallow as mm

from argschema.fields import String, Int


class PostgresInputConfigSchema(mm.Schema):
    host = String(
        description="",
        required=True
    )
    database = String(
        description="",
        required=True
    )
    user = String(
        description="",
        required=True
    )
    password = String(
        description="",
        required=False,
        default=os.environ.get("POSTGRES_SOURCE_PASSWORD")
    )
    port = Int(
        description="",
        required=False, # seems not to get hydrated from the default
        default=5432
    )
