from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    nickname = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)

class UserLoginSchema(Schema):
    nickname = fields.String(required=True)
    password = fields.String(required=True)

class TicTacToeGameTurnSchema(Schema):
    x = fields.Int(required=True, min=0, max=2)
    y = fields.Int(required=True, min=0, max=2)