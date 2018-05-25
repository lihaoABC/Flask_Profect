from flask import Blueprint

index_blue = Blueprint("view", __name__)

from . import views
