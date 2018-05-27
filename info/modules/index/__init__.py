# 1导入蓝图功能
from flask import Blueprint

# 2创建蓝图对象
index_blue = Blueprint("index", __name__)

# 3导入子模块
from . import views
