from flask import render_template

from . import news_blue


@news_blue.route('/<int:news_index>')
def show_news(news_index):

    return render_template('news/detail.html')