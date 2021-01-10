from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import pymysql

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
# 建立数据库关系
pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)

# 绑定app和数据库，以便进行操作
migrate = Migrate(app, db)

from realm_app import routes, models
