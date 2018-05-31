# 4导入蓝图对象
from flask import render_template, current_app, session, jsonify, request

from info import constants
from info.models import User, News, Category
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


    # 分类导航栏
    # 获取新闻分类数据
    categories = Category.query.all()
    # 定义列表保存分类数据
    category_list = []

    for category in categories:
        category_list.append(category.to_dict())

    data = {
        'user': user.to_dict() if user else None,
        "news_click_list": news_click_list,
        "categories": category_list
    }

    return render_template('./news/index.html', data=data)


# 首页新闻数据列表数据显示
"""
url：'/news_list'
type of request: GET
type of arguments: JSON
args_name: page, per_page, cid
"""


@index_blue.route('/news_list')
def get_news_list():
    """
    1.获取参数
    2.校验参数
    3.查询数据库
    4.返回数据
    :return:
    """
    # 1.获取参数,2. 校验参数
    try:
        cid = request.args.get('cid', 1, type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.查询数据库
    # 过滤掉cid=1的情况
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)

    try:
        pagination = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    # 获取查询内容
    items = pagination.items
    # 获取总页数
    total_page = pagination.pages
    # 获取当前页
    current_page = pagination.page

    news_dict_li = []
    for news in items:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "news_dict_li": news_dict_li,
        "current_page":current_page,
        "total_page":total_page
    }

    # 4. 返回数据
    return jsonify(errno=RET.OK, errmsg="successed", data=data)






@index_blue.route('/favicon.ico')
def favicon():

    return current_app.send_static_file('news/favicon.ico')