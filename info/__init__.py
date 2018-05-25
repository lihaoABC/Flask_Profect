from flask import Flask
# 导入数据库拓展，并添加相关配置
from flask_sqlalchemy import SQLAlchemy
# 导入redis数据库拓展，添加相关配置
import redis
# csrf
from flask_wtf.csrf import CSRFProtect
# 利用flask-session拓展，将session数据保存在redis中
from flask_session import Session

from config import config

db = SQLAlchemy()
redis_store = None


def create_app(config_name):
    app = Flask(__name__)
    # 参数导入一定要放在db创建之前
    app.config.from_object(config[config_name])
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 只做验证工作
    CSRFProtect(app)  # cookie中的csrf_token以及表单中的csrf_token需要手动实现
    # session实例
    Session(app)
    return app
