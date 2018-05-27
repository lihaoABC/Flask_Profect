import redis
import logging

from flask import Flask
# 导入数据库拓展，并添加相关配置
from flask_sqlalchemy import SQLAlchemy
# 导入redis数据库拓展，添加相关配置
# csrf
from flask_wtf.csrf import CSRFProtect
# 利用flask-session拓展，将session数据保存在redis中
from flask_session import Session
from config import config
from logging.handlers import RotatingFileHandler


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

    # 6注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    return app


def set_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)