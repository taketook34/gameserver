from gameserver import app, db
from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256
from marshmallow import ValidationError
from flask_jwt_extended import JWTManager, jwt_required
from flask_jwt_extended import create_access_token, jwt_required, verify_jwt_in_request
import os
import random

from gameserver.serializers import UserSchema, UserLoginSchema
from gameserver.models import User, TicTacToeGame
from gamespackage.tictactoe import TicTacToeSession, CageIsFilledError, FileIsExists


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
@jwt_required()
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
    print(data)
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
@jwt_required()
def creategame():
    
    jwt_claims = verify_jwt_in_request()
    host_id = jwt_claims[1]["sub"]

    with app.app_context():
        new_game = TicTacToeGame(
            game_token=os.urandom(6).hex(),
            user_host_id = host_id
        )

        db.session.add(new_game)
        db.session.commit()

        session = TicTacToeSession(filename_token=new_game.game_token, is_new=True, folder_name=app.config['FILES_FOLDER'])
        session.commit()

        message = {
            "id": new_game.id, 
            "game_token": new_game.game_token,
            "user_host_id": new_game.user_host_id,
            "is_game_started": new_game.is_game_started,
            "turn": new_game.game_turn,
            "date": new_game.created_at,
        }

    return jsonify(message)


@app.route('/tic-tac-toe/all', methods=['GET'])
@jwt_required()
def allgames():
    message = []
    with app.app_context():
        games = TicTacToeGame.query.all()

        for game in games:
            message.append({"id":game.id, "game_token":game.game_token, "host_id":game.user_host_id})
        
        return jsonify({'games': message})

@app.route('/tic-tac-toe/joingame/<game_token>', methods=['PUT'])
def joingame(game_token):
    '''
    ДОСТУП: Любой игрок кроме создателя
    УСЛОВИЯ ДЛЯ ПРОВЕРКИ: Игра еще не началась, игра не закончилась, вводящий не создатель
    подключает гостя в комнату, меняет параметры игры что бы игра началась

    '''
    jwt_claims = verify_jwt_in_request()
    joiner_id = jwt_claims[1]["sub"]
    
    with app.app_context():
        game_to_start = TicTacToeGame.query.filter_by(game_token=game_token).first()

        if game_to_start:
            if joiner_id == game_to_start.user_host_id:
                return jsonify({"error": f"Host cant be a guest!"})
            
            if game_to_start.is_game_started == 1 or game_to_start.is_game_ended == 1:
                return jsonify({"error": f"Game is not available"})
            
            
            game_to_start.user_guest_id = joiner_id
            game_to_start.is_game_started = 1
            game_to_start.user_turn = random.randint(0, 1)

            db.session.add(game_to_start)
            db.session.commit()

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



@app.route('/tic-tac-toe/deletegame/<game_token>', methods=['DELETE'])
@jwt_required()
def deletegame(game_token):
    '''
    ДОСТУП: игрок хост и игрок гость  (проверять по токену) 
    удаление игры (удаление записи в базе данных)
    '''
    jwt_claims = verify_jwt_in_request()
    deleter_id = jwt_claims[1]["sub"]

    with app.app_context():
        game_to_delete = TicTacToeGame.query.filter_by(game_token=game_token).first()
        if game_to_delete:

            if game_to_delete.user_host_id == deleter_id:
                # delete file from folder
                session = TicTacToeSession(filename_token=game_to_delete.game_token, is_new=False, folder_name=app.config['FILES_FOLDER'])
                session.deletegame()

                db.session.delete(game_to_delete)
                db.session.commit()

            else:
                return jsonify({"error": "You cannot delete game!"})
        else:
            return jsonify({"error": "Game with this token doesn\'t exist"})

    return jsonify({"message": f"Succes deletion game {game_token}"})
