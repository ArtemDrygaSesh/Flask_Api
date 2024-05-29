from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


#main
app = Flask(__name__)
app.debug = True
app.config.from_object('config')

#database
db = SQLAlchemy(app)

#migrations
migrate = Migrate(app, db)

#hashing
bcrypt = Bcrypt(app)

#schemas
ms = Marshmallow(app)

#auth
auth = HTTPBasicAuth()



from app import models, endpoints, schemas

