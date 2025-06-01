from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True, validate=validate.Length(max=120))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    created_at = fields.DateTime(dump_only=True)

class UserCreateSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))

class UserUpdateSchema(Schema):
    email = fields.Email(validate=validate.Length(max=120))
    name = fields.Str(validate=validate.Length(min=1, max=80))
    password = fields.Str(validate=validate.Length(min=6, max=100))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True) 