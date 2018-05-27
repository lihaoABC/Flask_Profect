# 4导入蓝图对象
from . import index_blue


# 5使用蓝图对象
@index_blue.route('/index')
def index():

    return 'index'
