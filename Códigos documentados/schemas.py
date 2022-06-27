from marshmallow import Schema, fields, post_load

from model.body import Body
from model.keplerian_body import KeplerianBody
from model.keplerian_solar_probe import KeplerianSolarProbe
from model.solar_probe import SolarProbe


# Creates a schema for the object 'Body' with all data assigned to it
class BodySchema(Schema):
    name = fields.String()
    mass = fields.Float()
    position = fields.List(fields.Float())
    velocity = fields.List(fields.Float())
    radius = fields.Float()

    # Receives deserialized data and returns processed data
    @post_load
    def instantiate_body(self, data, **kwargs):
        return Body(**data)


# Creates a schema for the object 'SolarProbe'
# with all data assigned to it
class SolarProbeSchema(BodySchema):
    alpha = fields.Float()
    delta = fields.Float()
    area = fields.Float()
    r_diff = fields.Float()
    r_spec = fields.Float()
    e_f = fields.Float()
    e_b = fields.Float()
    a_f = fields.Float()
    a_b = fields.Float()
    chi_f = fields.Float()
    chi_b = fields.Float()

    # Receives deserialized data and returns processed data
    @post_load
    def instantiate_body(self, data, **kwargs):
        return SolarProbe(**data)


# Creates a schema for the object 'KeplerianBody'
# with all data assigned to it
class KeplerianBodySchema(Schema):
    name = fields.String()
    mass = fields.Float()
    a = fields.Float()
    e = fields.Float()
    i = fields.Float()
    omega = fields.Float()
    OMEGA = fields.Float()
    radius = fields.Float()
    central_body = fields.Nested(BodySchema, allow_none=True)
    # This is done to allow recursive nested schema
    keplerian_central_body = fields.Nested("KeplerianBodySchema",
                                           allow_none=True)
    M = fields.Float(allow_nan=True)
    theta = fields.Float(allow_nan=True)

    # Receives deserialized data and returns processed data
    @post_load
    def instantiate_body(self, data, **kwargs):
        return KeplerianBody(**data)


# Creates a schema for the object 'KeplerianSolarProbe'
# with all data assigned to it
class KeplerianSolarProbeSchema(KeplerianBodySchema):
    alpha = fields.Float()
    delta = fields.Float()
    area = fields.Float()
    r_diff = fields.Float()
    r_spec = fields.Float()
    e_f = fields.Float()
    e_b = fields.Float()
    a_f = fields.Float()
    a_b = fields.Float()
    chi_f = fields.Float()
    chi_b = fields.Float()

    # Receives deserialized data and returns processed data
    @post_load
    def instantiate_body(self, data, **kwargs):
        return KeplerianSolarProbe(**data)


# Creates a schema for all objects
class RequestDto(Schema):
    time = fields.Integer()
    bodies = fields.Nested(BodySchema, many=True)
    solar_probes = fields.Nested(SolarProbeSchema, many=True)
    keplerian_bodies = fields.Nested(KeplerianBodySchema, many=True)
    keplerian_solar_probes = fields.Nested(KeplerianSolarProbeSchema,
                                           many=True)
