import redis
import logging


# Config类
class Config(object):
    """工程配置信息"""
    # 设置密钥
    SECRET_KEY = 'TgmL5kH7QEhnStpDZcpvvo1ip+4JJ3ovnGV9QmEqJwo='
    # 设置日志默认等级
    LOG_LEVEL = logging.DEBUG

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


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    LOG_LEVEL = logging.ERROR


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}