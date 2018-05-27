# 4导入蓝图对象
from flask import render_template

from . import index_blue


# 5使用蓝图对象
@index_blue.route('/')
def index():

    return render_template('./news/index.html')
