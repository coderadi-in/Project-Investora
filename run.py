'''coderadi'''

# ? Importing libraries
from main import *

# ! Buiding database
with server.app_context():
    db.create_all()

# ! Running the server
if __name__ == "__main__":
    server.run(debug=False, host='0.0.0.0')
