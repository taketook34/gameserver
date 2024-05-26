from gameserver import app, db
from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256
from marshmallow import ValidationError
from flask_jwt_extended import JWTManager, jwt_required
from flask_jwt_extended import create_access_token, jwt_required, verify_jwt_in_request
import os
import random

from gameserver.serializers import UserSchema, UserLoginSchema, TicTacToeGameTurnSchema
from gameserver.models import User, TicTacToeGame
from gamespackage.tictactoe import TicTacToeSession, CageIsFilledError, FileIsExists

# invertor = lambda x: 1 if x == 0 else 0
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
    return jsonify({"message": "This is main page"}), 200


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


    return jsonify({"message": "succes", "user_data": user_data}), 200

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
    
    return jsonify(to_return), 200



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
@jwt_required()
def creategame():
    
    jwt_claims = verify_jwt_in_request()
    host_id = jwt_claims[1]["sub"]
    # проверить не участвует ли юзер в дургих играх


    with app.app_context():
        for i in TicTacToeGame.query.filter_by(is_game_ended=0, is_game_started=1):
            if host_id == i.user_host_id or host_id == i.user_guest_id:
                return jsonify({"message": "User currently in another game"}), 203

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

    return jsonify(message), 201


@app.route('/tic-tac-toe/all', methods=['GET'])
@jwt_required()
def allgames():
    message = []
    with app.app_context():
        games = TicTacToeGame.query.all()

        for game in games:
            message.append({"id":game.id, "game_token":game.game_token, "host_id":game.user_host_id,
             "is_game_started":game.is_game_started, "is_game_ended": game.is_game_ended})
        
        return jsonify({'games': message}), 200

@app.route('/tic-tac-toe/joingame/<game_token>', methods=['PUT'])
@jwt_required()
def joingame(game_token):
    '''
    ДОСТУП: Любой игрок кроме создателя
    УСЛОВИЯ ДЛЯ ПРОВЕРКИ: Игра еще не началась, игра не закончилась, вводящий не создатель
    подключает гостя в комнату, меняет параметры игры что бы игра началась

    '''
    jwt_claims = verify_jwt_in_request()
    joiner_id = jwt_claims[1]["sub"]
    # проверить не участвует ли юзер в других играх
    with app.app_context():
        for i in TicTacToeGame.query.filter_by(is_game_ended=0, is_game_started=1):
            if joiner_id == i.user_host_id or joiner_id == i.user_guest_id:
                return jsonify({"error": "User currently in another game"}), 403

        game_to_start = TicTacToeGame.query.filter_by(game_token=game_token).first()

        if game_to_start:
            if joiner_id == game_to_start.user_host_id:
                return jsonify({"error": f"Host cant be a guest!"}), 403
            
            if game_to_start.is_game_started == 1 or game_to_start.is_game_ended == 1:
                return jsonify({"error": f"Game is not available"}), 403
            
            
            game_to_start.user_guest_id = joiner_id
            game_to_start.is_game_started = 1
            #game_to_start.user_turn = random.choice([game_to_start.user_host_id, game_to_start.user_guest_id]) 
            game_to_start.user_turn = game_to_start.user_host_id # на время тестирования для четкого определния первого юзера

            db.session.add(game_to_start)
            db.session.commit()

    return jsonify({"message": f"You conneted to {game_token} game"}), 200



@app.route('/tic-tac-toe/game-turn/<game_token>', methods=['PUT'])
def gameturn(game_token):
    '''
    ДОСТУП: игрок хост и игрок гост у которого ход (проверять по токену)
    Пользователь отправляет на сервер свое измение игровой карты
    Проверить надо:
        - пользователь или хост или гость
        - заданая игра не закончена и начата
        - проверить что ход соответсвует тому кому надо
        - проверить что бы не было ошибок при записи
        - проверить что бы после хода игра не закончилась
        
    '''
    jwt_claims = verify_jwt_in_request()
    gamer_id = jwt_claims[1]["sub"]
    turn_data = request.get_json()

    turn_schema = TicTacToeGameTurnSchema()
    try:
        turn_attempt = turn_schema.load(turn_data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400


    with app.app_context():
        game_to_update = TicTacToeGame.query.filter_by(game_token=game_token).first()

        if not game_to_update:
            return jsonify({"error": "Game not found"}), 403

        if gamer_id != game_to_update.user_host_id and gamer_id != game_to_update.user_guest_id:
            return jsonify({"error": "Wrong user"}), 403
        
        if game_to_update.is_game_ended == 1:
            return jsonify({"error": "Game is over", "winner": game_to_update.winner}), 403

        if game_to_update.is_game_started == 0:
            return jsonify({"error": "Game not started"}), 403
        

        if gamer_id != game_to_update.user_turn:
            return jsonify({"error": "Not user turn"}), 203

        session = TicTacToeSession(filename_token=game_token, folder_name=app.config['FILES_FOLDER'])
        try:     
            session.update(turn_attempt['x'], turn_attempt['y'], gamer_id)
        except  CageIsFilledError as error:
            return  jsonify({"error": f"{error}"}), 203
        
        game_data = session.loaded_data

        session.commit()
        
        
        if game_to_update.user_turn == game_to_update.user_host_id:
            game_to_update.user_turn = game_to_update.user_guest_id
        else:
            game_to_update.user_turn = game_to_update.user_host_id

        game_to_update.game_turn += 1

        if session.check_winner():
            game_to_update.is_game_ended = 1
            game_to_update.is_game_started = 0
            game_to_update.winner = gamer_id

        db.session.add(game_to_update)
        db.session.commit()

        message = {
                    "id": game_to_update.id,
                    "game_token": game_to_update.game_token,
                    "is_game_started": game_to_update.is_game_started,
                    "is_game_ended": game_to_update.is_game_ended,
                    "user_host_id": game_to_update.user_host_id,
                    "user_guest_id": game_to_update.user_guest_id,
                    "user_turn": game_to_update.user_turn,
                    "game_turn": game_to_update.game_turn,
                    "game_data": game_data,
                    "winner": game_to_update.winner,

                }
            

    
    return jsonify({"message": "Succesful attempt to make turn", "game_data": message})



@app.route('/tic-tac-toe/game-info/<game_token>', methods=['GET'])
@jwt_required()
def gameinfo(game_token):
    '''
    ДОСТУП: игрок хост и игрок гост (проверять по токену)
    возвращение всех игровых данных сессии. если игра окончена то происходит выведение окончательных данных игры которые не изменяются
    '''

    jwt_claims = verify_jwt_in_request()
    gamer_id = jwt_claims[1]["sub"]
    
    with app.app_context():
        game_to_watch = TicTacToeGame.query.filter_by(game_token=game_token).first()

        if game_to_watch:
            if gamer_id == game_to_watch.user_host_id or gamer_id == game_to_watch.user_guest_id:
                

                # download data using module
                session = TicTacToeSession(filename_token=game_token, folder_name=app.config['FILES_FOLDER'])
                game_data = session.loaded_data

                message = {
                    "id": game_to_watch.id,
                    "game_token": game_to_watch.game_token,
                    "is_game_started": game_to_watch.is_game_started,
                    "is_game_ended": game_to_watch.is_game_ended,
                    "user_host_id": game_to_watch.user_host_id,
                    "user_guest_id": game_to_watch.user_guest_id,
                    "user_turn": game_to_watch.user_turn,
                    "game_turn": game_to_watch.game_turn,
                    "game_data": game_data,
                    "winner": game_to_watch.winner,

                }
            else:
                return jsonify({"error": f"You can't get connection to game"}), 403
            
        else:
            return jsonify({"error": f"Game is not available"}), 403

    
    return jsonify({"game_info": message})



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
                return jsonify({"error": "You cannot delete game!"}), 403
        else:
            return jsonify({"error": "Game with this token doesn\'t exist"}), 404

    return jsonify({"message": f"Succes deletion game {game_token}"}), 200
