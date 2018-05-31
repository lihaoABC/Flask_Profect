# 4导入蓝图对象
from flask import render_template, current_app, session, jsonify

from info import constants
from info.models import User, News
from info.utils.response_code import RET
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

    # 首页显示排行
    news_list = None
    # 查询数据库
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="排行数据库查询失败")

    news_click_list = []
    for news in news_list if news_list else []:
        news_click_list.append(news.to_basic_dict())

    data = {
        'user': user.to_dict() if user else None,
        "news_click_list": news_click_list
    }

    return render_template('./news/index.html', data=data)


@index_blue.route('/favicon.ico')
def favicon():

    return current_app.send_static_file('news/favicon.ico')