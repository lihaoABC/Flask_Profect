# 3.1 导入蓝图对象
import random
import re
from datetime import datetime

from flask import request, make_response, current_app, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha


# 3.2 使用蓝图实现路由

# 开发中, 接口的地址和参数是后端人员确定的(也可以和前端商量)


"""
获取短信验证码
URL: 127.0.0.1:5000/passport/sms_code?
参数: mobile, image_code, image_code_id
"""


@passport_blue.route('/sms_code', methods=['POST'])
def get_sms_code():
    # 代码步骤分析

    # 一. 获取参数
    # 1. 获取参数(手机号\图像验证码内容, 图像验证码ID)
    # request.data接收的是json格式的字符串
    # json.loads(request.data)
    params_dict = request.json
    mobile = params_dict.get('mobile')
    image_code = params_dict.get('image_code')
    image_code_id = params_dict.get('image_code_id')

    # 二. 校验数据
    # 2. 校验数据(1. 数据完全性, 2. 正则匹配手机号)
    if not all([mobile, image_code, image_code_id]):
        # 如果有参数不全, 则会进入分支中
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    if not re.match(r'1[3456789][0-9]{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式有误')

    # 三. 逻辑处理
    # 3. 先从redis中获取数据(需要判断是否有数据)try
    try:
        real_image_code = redis_store.get('Image_code_id_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    # 要判断redis过期的情况
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码已过期')

    # 4. 用户传入的于服务器的验证码做对比(如果失败, 返回错误信息JSON)
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg='验证码输入错误')

    # 5. 如果对比一致, 生成验证码的值(第三方只负责发短信 '0000'), 保存到redis中
    # 06d: 以6位返回, 如果不足6位, 以0补齐
    sms_code_str = '%06d' % random.randint(0, 999999)
    current_app.logger.debug('sms_code: %s' % sms_code_str)

    # 6. 调用第三方发送短信
    result = CCP().send_template_sms(mobile, [sms_code_str, 5], 1)
    if result != 0:
        # 表示发送失败
        return jsonify(errno=RET.THIRDERR, errmsg='短信发送失败')

    # 保存到redis中
    try:
        redis_store.set('SMS_' + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码保存redis失败')

    # 四. 返回数据
    # 7. 返回成功的数据
    return jsonify(errno=RET.OK, errmsg='短信验证码发送成功')


# 获取图像验证码的路由/接口
# URL: /passport/image_code?image_code_id=XXXXXXXXXX
# 参数: image_code_id
@passport_blue.route('/image_code')
def get_image_code():

    # 1. 获取参数ID
    image_code_id = request.args.get('image_code_id')

    # 2. 生成验证码内容
    name, text, image_data = captcha.generate_captcha()

    # 3. 保存到redis中 try:
    try:
        # 1. redis_store为了有智能提示, 可以增加类型注释
        # 2. set本身也是可以设置过期时间的, 在参数的第三个位置
        redis_store.set('Image_code_id_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        # 记录到日志中
        current_app.logger.error(e)
        # 返回一个错误信息 前后端的数据, 采用JSON格式来返回. 可以通知前端局部数据的处理
        # {'errno': '4001', errmsg:'保存图片验证码失败'}
        return make_response(jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败'))

    # 4. 返回图像
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/jpg'
    return response


# 注册功能
"""
借口设计：
URL:/passport/register
请求方式：POST
传入参数：JSON格式
参数名：mobile, sms_code, passwprd
"""

@passport_blue.route('/register', methods=['POST'])
def register():
    """
    逻辑分析
    1. 获取参数和判断是否有值
    2. 从redis中获取指定手机号对应的短信验证码
    3. 校验验证码
    4. 初始化user模型， 并设置数据并添加到数据库
    5. 保存当前用户的状态
    6. 返回注册结果
    """

    # 1. 获取参数和判断是否有值
    json_data = request.json
    mobile = json_data.get('mobile')
    sms_code = json_data.get('sms_code')
    password = json_data.get("password")

    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    if not re.match(r"1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号错误")

    # 2.从redis中获取指定手机号对的的短信校验码
    try:
        real_sms_code = redis_store.get('SMS_' + mobile)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取本地验证码失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码过期')

    # 3.验证校验码

    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    # 删除短信验证码
    try:
        redis_store.delete("SMS_" + mobile)

    except Exception as e:
        current_app.logger.error(e)

    # 4. 初始化user、模型， 并设置数据并添加到数据库
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    # 对密码进行加密
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        # 数据保存错误
        return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")

    # 5. 保存用户登录状态
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = mobile

    # 6.返回注册结果
    return jsonify(errno=RET.OK, errmsg="OK")


# 接口设计
"""
URL：/passport/login
请求方式：POST
传入参数：JSON格式
参数：mobile, password
"""

@passport_blue.route('/login', methods=["POST"])
def login():
    """
    1. 获取参数和判断是否有值
    2. 从数据库查询出指定的用户
    3. 校验密码
    4. 保存用户登录状态
    5. 返回结果
    :return:
    """

    # 1. 获取参数和判断是否有值
    json_data = request.json
    mobile = json_data.get('mobile')
    password = json_data.get('password')

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    if not re.match(r'1[3456789]\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号错误")

    # 2. 从数据库查询出指定的用户
    try:
        user = User.query.filter_by(mobile=mobile).first()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 3. 校验密码
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg='密码错误')

    # 4. 保存用户登录状态
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile

    # 记录用户最后一次登录时间
    User.last_login = datetime.now()

    # 5.登录成功
    return jsonify(errno=RET.OK, errmsg="登录成功")