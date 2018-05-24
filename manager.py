from flask import Flask
# 导入数据库拓展，并添加相关配置
from flask_sqlalchemy import SQLAlchemy
# 导入redis数据库拓展，添加相关配置
import redis


app = Flask(__name__)


# Config类
class Config(object):
    """工程配置信息"""
    DEBUG = True

    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/information_F'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


app.config.from_object(Config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


@app.route('/index')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()
