from gameserver import db, app
from sqlalchemy import Boolean
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    #tictactoegame = db.relationship("TicTacToeGame", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"{self.nickname}:{self.email}"

class TicTacToeGame(db.Model):
    __tablename__ = "games"
    '''In "Boolean" fields 0 is False and 1 is True'''


    id = db.Column(db.Integer, primary_key=True)
    game_token = db.Column(db.String(13), unique=True, nullable=False) # need to set
    is_game_started = db.Column(db.Integer, default=0) # boolean field # set after join
    is_game_ended = db.Column(db.Integer, default=0) # boolean field 
    # change after turns
    user_host_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=False) #need to set
    user_guest_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=True) # set on join
    user_turn = db.Column(db.Integer, nullable=False, default=0) # False: 0. True: 1. # set after join
    #change after turn 
    game_turn = db.Column(db.Integer, default=0) # boolean field 
    #change after turn 
    #game_data = db.Column(db.String(255), nullable=True)
    winner = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=True) 
    # only if is_game_ended == 1
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Game {self.game_token}"




