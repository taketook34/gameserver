from gameserver import db, app

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"{self.nickname}:{self.email}"
