# 1导入蓝图功能
from flask import Blueprint

# 2创建蓝图对象
passport_blue = Blueprint("passport", __name__, url_prefix='/passport')

# 3导入子模块
from . import views