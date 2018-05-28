# 4导入蓝图对象
from flask import render_template, current_app, session

from info.models import User
from . import index_blue


# 5使用蓝图对象
@index_blue.route('/')
def index():
    # 获取当前用户的ID
    user_id = session.get('user_id', None)

    # 通过ID获取用户信息
    user = None

    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        'user': user.to_dict() if user else None
    }

    return render_template('./news/index.html', data=data)


@index_blue.route('/favicon.ico')
def favicon():

    return  current_app.send_static_file('news/favicon.ico')