from gameserver import app, db
from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256
from marshmallow import ValidationError
from flask_jwt_extended import JWTManager, jwt_required
from flask_jwt_extended import create_access_token, jwt_required, verify_jwt_in_request

from gameserver.serializers import UserSchema, UserLoginSchema
from gameserver.models import User

jwt = JWTManager(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
   return (
       jsonify({"message": "The token has expired.", "error": "token_expired"}),
       401,
   )

@jwt.invalid_token_loader
def invalid_token_callback(error):
   return (
       jsonify(
           {"message": "Signature verification failed.", "error": "invalid_token"}
       ),
       401,
   )

@jwt.unauthorized_loader
def missing_token_callback(error):
   return (
       jsonify(
           {
               "description": "Request does not contain an access token.",
               "error": "authorization_required",
           }
       ),
       401,
   )


@app.route('/home', methods=['GET'])
def home():
    return jsonify({"message": "This is main page"})


@app.route('/user/register', methods=['POST'])
def register():
    data = request.get_json()

    user_schema = UserSchema()
    try:
        user_attempt = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    with app.app_context():
        new_user = User(nickname=user_attempt["nickname"], password=pbkdf2_sha256.hash(user_attempt['password']), email=user_attempt["email"])
        db.session.add(new_user)
        db.session.commit()

    user_data = {
        "id": new_user.id,
        "nickname": new_user.nickname,
        "email": new_user.email,
    }


    return jsonify({"message": "succes", "user_data": user_data})

@app.route('/user/all', methods=['GET'])
def showusers():
    to_return = {"users": []}
    with app.app_context():
        users = User.query.all()
    
    for user in users:
        to_return['users'].append({
            "id": user.id,
            "nickname": user.nickname,
            "email": user.email,
        })
    
    return jsonify(to_return)



@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()

    user_schema = UserLoginSchema()
    try:
        user_login = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    with app.app_context():
        user_to_login = User.query.filter_by(nickname=user_login["nickname"]).first()

        if user_to_login and pbkdf2_sha256.verify(user_login["password"], user_to_login.password):
            access_token = create_access_token(identity=user_to_login.id)
            return jsonify({"message": "succes login", "acces_token": access_token}), 200
        else:
            return jsonify({"message": "unsucces login"}), 200




@app.route('/tic-tac-toe/creategame', methods=['GET'])
def creategame():
    return jsonify({"message": "Type your nick name for data"})



@app.route('/tic-tac-toe/joingame/<game_token>', methods=['GET'])
def joingame(game_token):

    return jsonify({"message": f"You conneted to {game_token} game"})



@app.route('/tic-tac-toe/game-turn/<game_token>', methods=['POST'])
def gameturn(game_token):
    '''
    ДОСТУП: игрок хост и игрок гост у которого ход (проверять по токену)
    Пользователь отправляет на сервер свое измение игровой карты
    '''
    return jsonify({"message": "Type your nick name for data"})



@app.route('/tic-tac-toe/game-info/<game_token>', methods=['GET'])
def gameinfo(game_token):
    '''
    ДОСТУП: игрок хост и игрок гост (проверять по токену)
    возвращение всех игровых данных сессии. если игра окончена то происходит выведение окончательных данных игры которые не изменяются
    '''

    return jsonify({"message": "Type your nick name for data"})



@app.route('/tic-tac-toe/deletegame/<game_token>', methods=['GET'])
def deletegame(game_token):
    '''
    ДОСТУП: игрок хост и игрок гость  (проверять по токену) 
    удаление игры (удаление записи в базе данных)
    '''
    return jsonify({"message": "Type your nick name for data"})
