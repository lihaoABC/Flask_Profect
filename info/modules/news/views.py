from flask import render_template, jsonify, current_app

from info import constants
from info.models import News
from info.utils.response_code import RET
from . import news_blue


@news_blue.route('/<int:news_index>')
def show_news(news_index):
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
        "news_click_list": news_click_list
    }
    return render_template('news/detail.html', data=data)