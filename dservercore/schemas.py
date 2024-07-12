"""marshmallow schema for (de-) serialization and validation"""
from marshmallow import Schema
from marshmallow.fields import (
    String,
    UUID,
    Dict,
    List,
    Boolean,
    Integer,
    Nested,
    Float,
    Raw
)


class ConfigSchema(Schema):
    config = Dict(keys=String(), values=Raw())


class VersionSchema(Schema):
    versions = Dict(keys=String(), values=String())


class ItemSchema(Schema):
    hash = String()
    relpath = String()
    size_in_bytes = Integer()
    utc_timestamp = Float()


class ReadmeSchema(Schema):
    readme = String()


class ManifestSchema(Schema):
    items = Dict(keys=String, values=Nested(ItemSchema))
    hash_function = String()
    dtoolcore_version = String()


# Define a schema for the response
class AnnotationSchema(Schema):
    annotations = Dict(keys=String(), values=String())


class TagSchema(Schema):
    tags = List(String())


class RegisterDatasetSchema(Schema):
    uuid = UUID()
    base_uri = String()
    uri = String()
    # dtoolcore_version should be included when storing (based on current version) but not required on the request
    name = String()
    type = String()
    readme = String()
    manifest = Nested(ManifestSchema)
    creator_username = String()
    frozen_at = String()
    created_at = String()
    annotations = Dict()
    tags = List(String)
    number_of_items = Integer()
    size_in_bytes = Integer()


class SearchDatasetSchema(Schema):
    free_text = String()
    creator_usernames = List(String)
    base_uris = List(String)
    uuids = List(UUID)
    tags = List(String)


class SummarySchema(Schema):
    number_of_datasets = Integer()
    total_size_in_bytes = Integer()
    creator_usernames = List(String)
    base_uris = List(String)
    datasets_per_creator = Dict(keys=String, values=Integer)
    size_in_bytes_per_creator = Dict(keys=String, values=Integer)
    datasets_per_base_uri = Dict(keys=String, values=Integer)
    size_in_bytes_per_base_uri = Dict(keys=String, values=Integer)
    tags = List(String)
    datasets_per_tag = Dict(keys=String, values=Integer)
    size_in_bytes_per_tag = Dict(keys=String, values=Integer)