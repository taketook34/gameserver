from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
import os

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from gameserver import views
