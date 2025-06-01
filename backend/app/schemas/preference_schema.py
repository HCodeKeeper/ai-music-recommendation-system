from marshmallow import Schema, fields, validate

class PreferenceSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    track_id = fields.Str(required=True)
    preference_type = fields.Str(required=True, validate=validate.OneOf(['like', 'dislike', 'skip']))
    created_at = fields.DateTime(dump_only=True)

class PreferenceCreateSchema(Schema):
    track_id = fields.Str(required=True)
    preference_type = fields.Str(required=True, validate=validate.OneOf(['like', 'dislike', 'skip']))

class PreferenceUpdateSchema(Schema):
    preference_type = fields.Str(validate=validate.OneOf(['like', 'dislike', 'skip'])) 