from app import db
from app.base_init import init_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = init_app()
db.init_app(app)
manager = Manager(app)
migrate = Migrate(app, db)

# note the limitations of Alembic auto-migrate
# https://alembic.sqlalchemy.org/en/latest/autogenerate.html
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
