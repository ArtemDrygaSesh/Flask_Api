import os

basedir = os.path.abspath(os.path.dirname(__file__))

#database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migrations')

#JSON config
JSON_SORT_KEYS = False