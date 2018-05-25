# flask_script与数据库迁移拓展
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app, db
from config import DevelopmentConfig, ProductionConfig

app = create_app('development')
# 数据库迁移
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/index')
def index():

    return 'index'


if __name__ == '__main__':
    manager.run()
