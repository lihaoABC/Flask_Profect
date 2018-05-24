from flask import Flask
# 导入数据库拓展，并添加相关配置
from flask_sqlalchemy import SQLAlchemy
# 导入redis数据库拓展，添加相关配置
import redis
# csrf
from flask_wtf.csrf import CSRFProtect
# 利用flask-session拓展，将session数据保存在redis中
from flask_session import Session


app = Flask(__name__)


# Config类
class Config(object):
    """工程配置信息"""
    DEBUG = True
    SECRET_KEY = 'TgmL5kH7QEhnStpDZcpvvo1ip+4JJ3ovnGV9QmEqJwo='

    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/information_F'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask_session配置信息
    SESSION_TYPE = 'redis'              # 指定session保存到redis中
    SESSION_USE_SIGNER = True           # 让cookie中的session——id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis实例
    PERMANENT_SESSION_LIFETIME = 86400  # session有效期，单位是秒




app.config.from_object(Config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 只做验证工作
CSRFProtect(app) # cookie中的csrf_token以及表单中的csrf_token需要手动实现
# session实例
Session(app)


@app.route('/index')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()
