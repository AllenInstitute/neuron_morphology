import os

import marshmallow as mm

import argschema
from argschema.fields import String, Int
from argschema.sources.source import ArgSource


class PostgresInputConfigSchema(mm.Schema):
    host = String(
        description="",
        required=""
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
        required=False,
        default=5432
    )


class PostgresSource(ArgSource):
    ConfigSchema = PostgresInputConfigSchema

    def get_dict(self):
        query_engine = 