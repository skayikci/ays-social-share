from marshmallow import Schema, fields, ValidationError

class PostSchema(Schema):
    content = fields.String(required=True, validate=lambda s: 1 <= len(s) <= 10000)
    platform = fields.String(required=True, validate=lambda s: s in ['twitter', 'linkedin'])
