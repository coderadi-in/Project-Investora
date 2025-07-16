'''coderadi'''

# ? Configuration class
class Config():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'project.investora.coderadi-flask'