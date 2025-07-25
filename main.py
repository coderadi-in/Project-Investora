'''coderadi'''

# ? Importing libraries
from flask import Flask, flash, redirect, url_for
from backend.config import Config
from backend.extensions import *
from routers.router import router
from routers.api import api
from routers.auth import auth
from routers.add import add

# ! Building server
server = Flask(__name__)
server.config.from_object(Config)

# ! Binding extensions
db.init_app(server)
migrate.init_app(server, db)
logger.init_app(server)

# ! Binding routers
server.register_blueprint(router)
server.register_blueprint(api)
server.register_blueprint(auth)
server.register_blueprint(add)

# & 401 Error Handler
@server.errorhandler(401)
def handle_401(error):
    flash("Login required", "warning")
    return redirect(url_for('auth.signup'))