'''coderadi'''

# ? Configuration class
class Config():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'project.investora.coderadi-flask'
    GOOGLE_CLIENT_ID = '31649701701-tu175agauqnk4hv99fuj6s8d2mm6jpa2.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
