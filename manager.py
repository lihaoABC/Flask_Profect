from flask import Flask, session
# 导入数据库拓展，并添加相关配置
from flask_sqlalchemy import SQLAlchemy
# 导入redis数据库拓展，添加相关配置
import redis
# csrf
from flask_wtf.csrf import CSRFProtect
# 利用flask-session拓展，将session数据保存在redis中
from flask_session import Session
# flask_script与数据库迁移拓展
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from config import Config

app = Flask(__name__)


app.config.from_object(Config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 只做验证工作
CSRFProtect(app) # cookie中的csrf_token以及表单中的csrf_token需要手动实现
# session实例
Session(app)
# 数据库迁移
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/index')
def index():
    session['name'] = 'mike'
    return 'index'


if __name__ == '__main__':
    manager.run()
