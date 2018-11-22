import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
# from flask.ext.script import Manager
# from flask.ext.migrate import Migrate, MigrateCommand

from app import db, create_app

app = create_app()
app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand) # TODO(Nico) rename this

@manager.command
def recreate_db():
    """Recreates a local database. You probably should not use this on production."""
    # db.drop_all()
    db.create_all()
    db.session.commit()

if __name__ == '__main__':
    manager.run()